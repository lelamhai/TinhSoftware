#!/usr/bin/env python3
"""
Tool to inspect ONNX model information.
Displays input/output nodes, shapes, and data types.
"""
import sys
from pathlib import Path
import onnxruntime as ort


def inspect_model(model_path: str):
    """Inspect ONNX model and print details."""
    model_path = Path(model_path)
    
    if not model_path.exists():
        print(f"Error: Model file not found: {model_path}")
        return 1
    
    print(f"Loading model: {model_path}")
    print("=" * 60)
    
    try:
        session = ort.InferenceSession(str(model_path))
        
        print("\nINPUT NODES:")
        print("-" * 60)
        for inp in session.get_inputs():
            print(f"Name:  {inp.name}")
            print(f"Shape: {inp.shape}")
            print(f"Type:  {inp.type}")
            print()
        
        print("\nOUTPUT NODES:")
        print("-" * 60)
        for out in session.get_outputs():
            print(f"Name:  {out.name}")
            print(f"Shape: {out.shape}")
            print(f"Type:  {out.type}")
            print()
        
        print("\nPROVIDERS AVAILABLE:")
        print("-" * 60)
        available_providers = ort.get_available_providers()
        for provider in available_providers:
            print(f"  - {provider}")
        
        print("\n" + "=" * 60)
        print("Model inspection complete!")
        
    except Exception as e:
        print(f"Error loading model: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python model_info.py <path_to_onnx_model>")
        print("\nExample:")
        print("  python model_info.py assets/models/birefnet.onnx")
        sys.exit(1)
    
    sys.exit(inspect_model(sys.argv[1]))
