#!/usr/bin/env python3
"""
RemoveBG Desktop Application - Entry Point
BiRefNet ONNX Background Removal
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
import qasync

from src.ui.main_window_new import MainWindowNew  # Use new modern UI
from src.ui.view_models.main_view_model import MainViewModel
from src.application.use_cases.remove_background_use_case import RemoveBackgroundUseCase
from src.infrastructure.engines.onnx_birefnet_engine import OnnxBiRefNetEngine
from src.infrastructure.image_io.local_image_io import LocalImageIO
from src.infrastructure.settings.json_settings_store import JsonSettingsStore
from src.domain.entities.settings import Settings


def main():
    """Main entry point for the application."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("RemoveBG")
    app.setOrganizationName("TinhSoftware")
    app.setApplicationVersion("0.1.0")
    
    # Load settings
    settings_store = JsonSettingsStore()
    settings = settings_store.load()
    
    # Check if model exists
    if not settings.model_path.exists():
        QMessageBox.warning(
            None,
            "Model Not Found",
            f"BiRefNet ONNX model not found at:\n{settings.model_path}\n\n"
            "Please download the model and place it in:\n"
            "assets/models/birefnet.onnx\n\n"
            "The application will continue, but you won't be able to process images."
        )
    
    try:
        # Initialize infrastructure
        image_io = LocalImageIO()
        engine = OnnxBiRefNetEngine(settings)
        
        # Initialize use case
        use_case = RemoveBackgroundUseCase(engine, image_io, settings)
        
        # Initialize view model
        view_model = MainViewModel(use_case, image_io, settings)
        
        # Create and show main window with new modern UI
        window = MainWindowNew(view_model)
        window.show()
        
        # Setup async event loop
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        with loop:
            sys.exit(loop.run_forever())
            
    except Exception as e:
        QMessageBox.critical(
            None,
            "Initialization Error",
            f"Failed to initialize application:\n{str(e)}\n\n"
            "Please check that all dependencies are installed and "
            "the model file exists."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
