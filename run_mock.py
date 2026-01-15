"""
BiRefNet Background Removal Application
Sử dụng ONNX model thật với BiRefNet AI
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    print("="*70)
    print("🚀 BiRefNet - AI Background Removal")
    print("="*70)
    print()
    
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import Qt
    import qasync
    
    from src.ui.main_window_new import MainWindowNew
    from src.ui.view_models.main_view_model import MainViewModel
    from src.application.use_cases.remove_background_use_case import RemoveBackgroundUseCase
    from src.infrastructure.engines.onnx_birefnet_engine import OnnxBiRefNetEngine
    from src.infrastructure.image_io.local_image_io import LocalImageIO
    from src.infrastructure.settings.json_settings_store import JsonSettingsStore
    from src.domain.entities.settings import Settings
    
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
            f"{settings.model_path.parent}\n\n"
            "The app will continue but processing will fail."
        )
    
    # Initialize components
    try:
        engine = OnnxBiRefNetEngine(settings)
        image_io = LocalImageIO()
        remove_bg_use_case = RemoveBackgroundUseCase(engine, image_io, settings)
        view_model = MainViewModel(remove_bg_use_case, image_io, settings)
        
        # Create and show main window
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        window = MainWindowNew(view_model)
        window.show()
        
        with loop:
            sys.exit(loop.run_forever())
            
    except Exception as e:
        QMessageBox.critical(
            None,
            "Initialization Error",
            f"Failed to initialize application:\n{str(e)}"
        )
        sys.exit(1)
