#!/usr/bin/env python3
"""
Benchmark tool for BiRefNet ONNX engine performance.
Tests inference performance with different providers and profiling.
"""
import sys
import time
import cProfile
import pstats
import io
from pathlib import Path
from dataclasses import dataclass
from typing import List
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.entities.settings import Settings
from src.infrastructure.engines.onnx_birefnet_engine import OnnxBiRefNetEngine
from src.infrastructure.engines.provider_manager import ProviderManager
from src.infrastructure.image_io.local_image_io import LocalImageIO
from src.application.use_cases.remove_background_use_case import RemoveBackgroundUseCase
import asyncio


@dataclass
class BenchmarkResult:
    """Single benchmark result."""
    image_path: Path
    resolution: str
    provider: str
    preprocessing_ms: float
    inference_ms: float
    postprocessing_ms: float
    total_ms: float
    
    @property
    def fps(self) -> float:
        """Calculate FPS."""
        return 1000.0 / self.total_ms if self.total_ms > 0 else 0.0
    
    def __str__(self):
        return (
            f"{self.image_path.name:20s} | {self.resolution:10s} | "
            f"{self.provider:12s} | Pre: {self.preprocessing_ms:6.1f}ms | "
            f"Inf: {self.inference_ms:6.1f}ms | Post: {self.postprocessing_ms:6.1f}ms | "
            f"Total: {self.total_ms:7.1f}ms ({self.fps:.2f} FPS)"
        )


@dataclass
class BenchmarkSummary:
    """Summary of multiple benchmark runs."""
    results: List[BenchmarkResult]
    
    @property
    def avg_total_ms(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.total_ms for r in self.results) / len(self.results)
    
    @property
    def avg_inference_ms(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.inference_ms for r in self.results) / len(self.results)
    
    @property
    def avg_fps(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.fps for r in self.results) / len(self.results)
    
    @property
    def min_total_ms(self) -> float:
        if not self.results:
            return 0.0
        return min(r.total_ms for r in self.results)
    
    @property
    def max_total_ms(self) -> float:
        if not self.results:
            return 0.0
        return max(r.total_ms for r in self.results)


class Benchmark:
    """Benchmark tool for performance testing."""
    
    def __init__(self, model_path: Path):
        """
        Initialize benchmark.
        
        Args:
            model_path: Path to ONNX model
        """
        self.model_path = model_path
    
    async def run_single(
        self,
        image_path: Path,
        provider: str = "CPU",
        num_runs: int = 5,
        warmup: bool = True
    ) -> BenchmarkSummary:
        """
        Run benchmark on single image.
        
        Args:
            image_path: Input image path
            provider: Execution provider (CPU, CUDA, DirectML)
            num_runs: Number of iterations
            warmup: Whether to run warmup inference
            
        Returns:
            BenchmarkSummary
        """
        print(f"\n{'='*100}")
        print(f"Benchmarking: {image_path.name}")
        print(f"Provider: {provider}")
        print(f"Runs: {num_runs} (warmup: {warmup})")
        print(f"{'='*100}\n")
        
        # Setup
        settings = Settings(
            model_path=self.model_path,
            execution_provider=provider
        )
        
        engine = OnnxBiRefNetEngine(settings, enable_caching=True)
        image_io = LocalImageIO()
        use_case = RemoveBackgroundUseCase(engine, image_io, settings)
        
        # Load image once
        image_input = await image_io.load_image(image_path)
        resolution = f"{image_input.width}x{image_input.height}"
        
        results = []
        
        # Warmup run
        if warmup:
            print("Warming up...")
            _ = await use_case.execute(image_path)
            print("Warmup complete\n")
        
        # Benchmark runs
        for i in range(num_runs):
            # Time preprocessing
            t0 = time.perf_counter()
            input_tensor, original_size = engine.preprocessor.preprocess(image_input.data)
            t1 = time.perf_counter()
            preprocessing_ms = (t1 - t0) * 1000
            
            # Time inference
            input_name = engine.session.get_inputs()[0].name
            output_name = engine.session.get_outputs()[0].name
            
            t2 = time.perf_counter()
            outputs = engine.session.run([output_name], {input_name: input_tensor})
            t3 = time.perf_counter()
            inference_ms = (t3 - t2) * 1000
            
            # Time postprocessing
            t4 = time.perf_counter()
            mask_data = engine.preprocessor.postprocess_mask(outputs[0], original_size)
            t5 = time.perf_counter()
            postprocessing_ms = (t5 - t4) * 1000
            
            total_ms = preprocessing_ms + inference_ms + postprocessing_ms
            
            result = BenchmarkResult(
                image_path=image_path,
                resolution=resolution,
                provider=provider,
                preprocessing_ms=preprocessing_ms,
                inference_ms=inference_ms,
                postprocessing_ms=postprocessing_ms,
                total_ms=total_ms
            )
            
            results.append(result)
            print(f"Run {i+1}/{num_runs}: {result}")
        
        summary = BenchmarkSummary(results)
        
        print(f"\n{'='*100}")
        print("SUMMARY")
        print(f"{'='*100}")
        print(f"Average Total:     {summary.avg_total_ms:7.1f} ms ({summary.avg_fps:.2f} FPS)")
        print(f"Average Inference: {summary.avg_inference_ms:7.1f} ms")
        print(f"Min Total:         {summary.min_total_ms:7.1f} ms")
        print(f"Max Total:         {summary.max_total_ms:7.1f} ms")
        print(f"{'='*100}\n")
        
        return summary
    
    async def compare_providers(
        self,
        image_path: Path,
        num_runs: int = 5
    ) -> dict:
        """
        Compare performance across all available providers.
        
        Args:
            image_path: Input image path
            num_runs: Number of runs per provider
            
        Returns:
            Dict mapping provider name to BenchmarkSummary
        """
        available_providers = ProviderManager.get_provider_info()
        
        print(f"\n{'='*100}")
        print("PROVIDER COMPARISON")
        print(f"{'='*100}")
        print(f"Available providers: {', '.join(available_providers.keys())}")
        print(f"{'='*100}\n")
        
        results = {}
        
        for provider_key in available_providers:
            friendly_name = available_providers[provider_key]["name"]
            summary = await self.run_single(
                image_path,
                provider=friendly_name,
                num_runs=num_runs,
                warmup=True
            )
            results[friendly_name] = summary
        
        # Print comparison
        print(f"\n{'='*100}")
        print("PROVIDER COMPARISON SUMMARY")
        print(f"{'='*100}")
        
        for provider, summary in sorted(results.items(), key=lambda x: x[1].avg_total_ms):
            print(f"{provider:12s} | Avg: {summary.avg_total_ms:7.1f} ms | FPS: {summary.avg_fps:6.2f}")
        
        print(f"{'='*100}\n")
        
        return results
    
    def profile_inference(
        self,
        image_path: Path,
        provider: str = "CPU"
    ):
        """
        Profile inference with cProfile.
        
        Args:
            image_path: Input image path
            provider: Execution provider
        """
        print(f"\n{'='*100}")
        print(f"Profiling: {image_path.name}")
        print(f"Provider: {provider}")
        print(f"{'='*100}\n")
        
        # Setup
        settings = Settings(
            model_path=self.model_path,
            execution_provider=provider
        )
        
        engine = OnnxBiRefNetEngine(settings)
        image_io = LocalImageIO()
        use_case = RemoveBackgroundUseCase(engine, image_io, settings)
        
        # Profile
        profiler = cProfile.Profile()
        profiler.enable()
        
        # Run inference
        asyncio.run(use_case.execute(image_path))
        
        profiler.disable()
        
        # Print stats
        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats('cumulative')
        stats.print_stats(30)  # Top 30 functions
        
        print(s.getvalue())


async def main():
    """Main benchmark script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark BiRefNet ONNX engine")
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("assets/models/birefnet.onnx"),
        help="Path to ONNX model"
    )
    parser.add_argument(
        "--image",
        type=Path,
        required=True,
        help="Path to test image"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="CPU",
        choices=["CPU", "CUDA", "DirectML"],
        help="Execution provider"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of runs"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare all available providers"
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Run profiler"
    )
    
    args = parser.parse_args()
    
    # Check model exists
    if not args.model.exists():
        print(f"Error: Model not found at {args.model}")
        print("Please download BiRefNet ONNX model and place it in assets/models/")
        return
    
    # Check image exists
    if not args.image.exists():
        print(f"Error: Image not found at {args.image}")
        return
    
    benchmark = Benchmark(args.model)
    
    if args.profile:
        benchmark.profile_inference(args.image, args.provider)
    elif args.compare:
        await benchmark.compare_providers(args.image, args.runs)
    else:
        await benchmark.run_single(args.image, args.provider, args.runs)


if __name__ == "__main__":
    asyncio.run(main())
