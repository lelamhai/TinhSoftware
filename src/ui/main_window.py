"""Main window for RemoveBG application."""
import asyncio
from pathlib import Path
from typing import Optional, List

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QStatusBar,
    QGroupBox, QSlider, QRadioButton, QButtonGroup,
    QLineEdit, QMessageBox, QCheckBox, QToolBar, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage, QAction

from src.ui.widgets.image_preview import ImagePreviewWidget
from src.ui.view_models.main_view_model import MainViewModel
from src.domain.entities.settings import Settings
from src.infrastructure.engines.provider_manager import ProviderManager


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, view_model: MainViewModel):
        """Initialize main window."""
        super().__init__()
        self.view_model = view_model
        self.input_image_path: Optional[Path] = None
        self.output_image_path: Optional[Path] = None
        self.background_image_path: Optional[Path] = None
        self.bg_color = None  # None = transparent, tuple = color
        self.transparent_result = None  # Store transparent RGBA result for compositing
        self.raw_mask = None  # Store raw mask from AI (before post-processing)
        self.original_image = None  # Store original ImageInput for reprocessing
        
        self.setWindowTitle("RemoveBG Desktop - BiRefNet")
        self.setGeometry(100, 100, 1400, 900)
        self.setAcceptDrops(True)
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Top toolbar
        toolbar = self._create_toolbar()
        main_layout.addLayout(toolbar)
        
        # Preview area
        preview_layout = self._create_preview_area()
        main_layout.addLayout(preview_layout)
        
        # Settings panel
        settings_panel = self._create_settings_panel()
        main_layout.addWidget(settings_panel)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _create_toolbar(self) -> QHBoxLayout:
        """Create top toolbar with action buttons."""
        layout = QHBoxLayout()
        
        self.btn_open = QPushButton("Open Image")
        self.btn_remove = QPushButton("Remove BG")
        self.btn_save = QPushButton("Save PNG")
        self.btn_save_mask = QPushButton("Export Mask")
        self.btn_batch = QPushButton("Batch...")
        self.btn_reset = QPushButton("Reset")
        
        self.btn_remove.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.btn_save_mask.setEnabled(False)
        
        layout.addWidget(self.btn_open)
        layout.addWidget(self.btn_remove)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.btn_save_mask)
        layout.addWidget(self.btn_batch)
        layout.addWidget(self.btn_reset)
        layout.addStretch()
        
        return layout
    
    def _create_preview_area(self) -> QHBoxLayout:
        """Create image preview area."""
        layout = QHBoxLayout()
        
        # Left: Input preview
        input_group = QGroupBox("Input Preview")
        input_layout = QVBoxLayout()
        self.preview_input = ImagePreviewWidget()
        self.preview_input.setStyleSheet("QLabel { background-color: #f0f0f0; }")
        
        # Input controls
        input_controls = QHBoxLayout()
        btn_fit_input = QPushButton("Fit")
        btn_fit_input.clicked.connect(self.preview_input.fit_to_view)
        btn_zoom_in_input = QPushButton("Zoom +")
        btn_zoom_in_input.clicked.connect(self.preview_input.zoom_in)
        btn_zoom_out_input = QPushButton("Zoom -")
        btn_zoom_out_input.clicked.connect(self.preview_input.zoom_out)
        btn_reset_input = QPushButton("100%")
        btn_reset_input.clicked.connect(self.preview_input.reset_zoom)
        
        input_controls.addWidget(btn_fit_input)
        input_controls.addWidget(btn_zoom_in_input)
        input_controls.addWidget(btn_zoom_out_input)
        input_controls.addWidget(btn_reset_input)
        input_controls.addStretch()
        
        input_layout.addWidget(self.preview_input)
        input_layout.addLayout(input_controls)
        input_group.setLayout(input_layout)
        
        # Right: Output preview
        output_group = QGroupBox("Output Preview (Transparent)")
        output_layout = QVBoxLayout()
        self.preview_output = ImagePreviewWidget()
        self.preview_output.setStyleSheet("QLabel { background-color: #ffffff; }")
        
        # Output controls
        output_controls = QHBoxLayout()
        btn_fit_output = QPushButton("Fit")
        btn_fit_output.clicked.connect(self.preview_output.fit_to_view)
        btn_zoom_in_output = QPushButton("Zoom +")
        btn_zoom_in_output.clicked.connect(self.preview_output.zoom_in)
        btn_zoom_out_output = QPushButton("Zoom -")
        btn_zoom_out_output.clicked.connect(self.preview_output.zoom_out)
        btn_reset_output = QPushButton("100%")
        btn_reset_output.clicked.connect(self.preview_output.reset_zoom)
        
        self.chk_checkerboard = QCheckBox("Checkerboard")
        self.chk_checkerboard.setChecked(True)
        self.chk_checkerboard.stateChanged.connect(self._on_checkerboard_toggled)
        
        output_controls.addWidget(btn_fit_output)
        output_controls.addWidget(btn_zoom_in_output)
        output_controls.addWidget(btn_zoom_out_output)
        output_controls.addWidget(btn_reset_output)
        output_controls.addWidget(self.chk_checkerboard)
        output_controls.addStretch()
        
        output_layout.addWidget(self.preview_output)
        output_layout.addLayout(output_controls)
        output_group.setLayout(output_layout)
        
        layout.addWidget(input_group)
        layout.addWidget(output_group)
        
        return layout
    
    def _create_settings_panel(self) -> QGroupBox:
        """Create settings panel."""
        group = QGroupBox("Settings")
        layout = QVBoxLayout()
        
        # Model path
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.txt_model = QLineEdit(str(self.view_model.settings.model_path))
        self.txt_model.setReadOnly(True)
        model_layout.addWidget(self.txt_model)
        self.btn_browse_model = QPushButton("Browse...")
        self.btn_browse_model.clicked.connect(self._on_browse_model)
        model_layout.addWidget(self.btn_browse_model)
        layout.addLayout(model_layout)
        
        # Device selection
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Device:"))
        self.device_group = QButtonGroup()
        self.radio_cpu = QRadioButton("CPU")
        self.radio_cuda = QRadioButton("GPU-CUDA")
        self.radio_dml = QRadioButton("GPU-DirectML")
        
        self.device_group.addButton(self.radio_cpu, 0)
        self.device_group.addButton(self.radio_cuda, 1)
        self.device_group.addButton(self.radio_dml, 2)
        
        # Connect device change handler
        self.device_group.buttonClicked.connect(self._on_device_changed)
        
        # Auto-detect available providers
        provider_info = ProviderManager.get_provider_info()
        self.radio_cpu.setChecked(True)
        self.radio_cuda.setEnabled("CUDAExecutionProvider" in provider_info)
        self.radio_dml.setEnabled("DmlExecutionProvider" in provider_info)
        
        # Set recommended provider
        recommended = ProviderManager.get_recommended_provider()
        if recommended == "CUDA":
            self.radio_cuda.setChecked(True)
        elif recommended == "DirectML":
            self.radio_dml.setChecked(True)
        
        device_layout.addWidget(self.radio_cpu)
        device_layout.addWidget(self.radio_cuda)
        device_layout.addWidget(self.radio_dml)
        
        # Add provider info tooltip
        provider_status = []
        for key, info in provider_info.items():
            provider_status.append(f"{info['display_name']}: {info['description']}")
        
        lbl_provider_info = QLabel("ⓘ")
        lbl_provider_info.setToolTip("\n".join(provider_status))
        device_layout.addWidget(lbl_provider_info)
        
        device_layout.addStretch()
        layout.addLayout(device_layout)
        
        # Advanced options
        advanced_layout = QHBoxLayout()
        self.chk_auto_crop = QCheckBox("Auto-crop output")
        self.chk_auto_crop.setChecked(self.view_model.settings.auto_crop_output)
        self.chk_auto_crop.stateChanged.connect(self._on_auto_crop_changed)
        advanced_layout.addWidget(self.chk_auto_crop)
        
        advanced_layout.addWidget(QLabel("  Default Save Folder:"))
        self.txt_save_folder = QLineEdit(self.view_model.settings.default_save_folder)
        advanced_layout.addWidget(self.txt_save_folder)
        self.btn_browse_save = QPushButton("Browse...")
        self.btn_browse_save.clicked.connect(self._on_browse_save_folder)
        advanced_layout.addWidget(self.btn_browse_save)
        
        layout.addLayout(advanced_layout)
        
        # Background preview color (Optional)
        bg_group = QGroupBox("Background Preview Color (Optional)")
        bg_layout = QHBoxLayout()
        
        bg_layout.addWidget(QLabel("Preview with color:"))
        self.btn_pick_color = QPushButton("Pick Color")
        self.btn_pick_color.clicked.connect(self._on_pick_color)
        self.btn_pick_color.setEnabled(False)
        self.lbl_color_preview = QLabel("")
        self.lbl_color_preview.setFixedSize(50, 25)
        self.lbl_color_preview.setStyleSheet("background-color: transparent; border: 1px solid #000;")
        self.bg_color = None  # None = transparent, tuple = color
        bg_layout.addWidget(self.btn_pick_color)
        bg_layout.addWidget(self.lbl_color_preview)
        
        self.btn_clear_color = QPushButton("Clear (Transparent)")
        self.btn_clear_color.clicked.connect(self._on_clear_color)
        self.btn_clear_color.setEnabled(False)
        bg_layout.addWidget(self.btn_clear_color)
        
        bg_layout.addStretch()
        
        bg_group.setLayout(bg_layout)
        layout.addWidget(bg_group)
        
        # Processing params
        params_layout = QHBoxLayout()
        
        # Threshold
        params_layout.addWidget(QLabel("Threshold:"))
        self.slider_threshold = QSlider(Qt.Orientation.Horizontal)
        self.slider_threshold.setMinimum(0)
        self.slider_threshold.setMaximum(100)
        self.slider_threshold.setValue(int(self.view_model.settings.threshold * 100))
        self.label_threshold = QLabel(f"{self.view_model.settings.threshold:.2f}")
        params_layout.addWidget(self.slider_threshold)
        params_layout.addWidget(self.label_threshold)
        
        # Smooth
        params_layout.addWidget(QLabel("  Smooth:"))
        self.slider_smooth = QSlider(Qt.Orientation.Horizontal)
        self.slider_smooth.setMinimum(0)
        self.slider_smooth.setMaximum(10)
        self.slider_smooth.setValue(self.view_model.settings.smooth_pixels)
        self.label_smooth = QLabel(f"{self.view_model.settings.smooth_pixels} px")
        params_layout.addWidget(self.slider_smooth)
        params_layout.addWidget(self.label_smooth)
        
        # Feather
        params_layout.addWidget(QLabel("  Feather:"))
        self.slider_feather = QSlider(Qt.Orientation.Horizontal)
        self.slider_feather.setMinimum(0)
        self.slider_feather.setMaximum(10)
        self.slider_feather.setValue(self.view_model.settings.feather_pixels)
        self.label_feather = QLabel(f"{self.view_model.settings.feather_pixels} px")
        params_layout.addWidget(self.slider_feather)
        params_layout.addWidget(self.label_feather)
        self.txt_save_folder.textChanged.connect(self._on_save_folder_changed)
        
        layout.addLayout(params_layout)
        
        group.setLayout(layout)
        return group
    
    def _connect_signals(self):
        """Connect UI signals to handlers."""
        self.btn_open.clicked.connect(self._on_open_image)
        self.btn_remove.clicked.connect(self._on_remove_background)
        self.btn_save.clicked.connect(self._on_save_image)
        self.btn_save_mask.clicked.connect(self._on_save_mask)
        self.btn_batch.clicked.connect(self._on_batch_process)
        self.btn_reset.clicked.connect(self._on_reset)        
        self.slider_threshold.valueChanged.connect(self._on_threshold_changed)
        self.slider_smooth.valueChanged.connect(self._on_smooth_changed)
        self.slider_feather.valueChanged.connect(self._on_feather_changed)
    
    def _on_open_image(self):
        """Handle open image button."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Images (*.jpg *.jpeg *.png *.webp *.bmp)"
        )
        
        if file_path:
            self.input_image_path = Path(file_path)
            
            # Display image
            pixmap = QPixmap(str(file_path))
            self.preview_input.set_image(pixmap, use_checkerboard=False)
            self.preview_input.fit_to_view()
            
            self.btn_remove.setEnabled(True)
            self.btn_save_mask.setEnabled(False)
            self.status_bar.showMessage(f"Loaded: {file_path}")
    
    def _on_remove_background(self):
        """Handle remove background button."""
        if not self.input_image_path:
            return
        
        self.status_bar.showMessage("Processing...")
        self.btn_remove.setEnabled(False)
        
        # Run async task
        QTimer.singleShot(100, lambda: asyncio.create_task(self._process_image()))
    
    async def _process_image(self):
        """Process image asynchronously - Always create transparent PNG."""
        try:
            # Always remove background to transparent
            result = await self.view_model.remove_background(self.input_image_path)
            
            # Store raw data for real-time reprocessing
            self.transparent_result = result.output.data.copy()
            self.raw_mask = result.raw_mask
            self.original_image = result.original_image
            
            # Display output
            self.output_image_path = self.input_image_path.parent / f"{self.input_image_path.stem}_nobg.png"
            
            # Display with current background color (or transparent)
            self._update_preview_with_background()
            self.preview_output.fit_to_view()
            
            self.btn_save.setEnabled(True)
            self.btn_save_mask.setEnabled(True)
            self.btn_pick_color.setEnabled(True)
            self.btn_clear_color.setEnabled(True)
            
            crop_info = ""
            if hasattr(result, 'crop_bounds') and result.crop_bounds:
                crop_info = f" | Cropped: {result.crop_bounds[2]}x{result.crop_bounds[3]}"
            
            self.status_bar.showMessage(
                f"Done! Time: {result.processing_time_ms:.0f}ms{crop_info}"
            )
            
            # Cache result
            self.view_model.last_result = result
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Processing Error",
                f"Failed to process image:\n\n{str(e)}\n\n"
                "Please check:\n"
                "- Model file exists and is valid\n"
                "- Image file is not corrupted\n"
                "- Enough memory available"
            )
            self.status_bar.showMessage("Error - Processing failed")
            self.btn_remove.setEnabled(True)
    
    def _on_save_image(self):
        """Handle save image button."""
        if not self.view_model.last_result:
            return
        
        # Use default save folder if set
        default_path = self.output_image_path or Path("output.png")
        if self.view_model.settings.default_save_folder:
            save_folder = Path(self.view_model.settings.default_save_folder)
            if save_folder.exists():
                default_path = save_folder / default_path.name
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PNG",
            str(default_path),
            "PNG Image (*.png)"
        )
        
        if file_path:
            asyncio.create_task(self._save_image(Path(file_path)))
    
    async def _save_image(self, path: Path):
        """Save image asynchronously."""
        try:
            await self.view_model.save_output(path)
            self.status_bar.showMessage(f"Saved: {path}")
            QMessageBox.information(self, "Success", f"Image saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save image:\n{str(e)}")
    
    def _on_reset(self):
        """Handle reset button."""
        self.input_image_path = None
        self.output_image_path = None
        self.background_image_path = None
        self.preview_input.clear_image()
        self.preview_output.clear_image()
        self.btn_remove.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.btn_save_mask.setEnabled(False)
        self.view_model.last_result = None
        self.status_bar.showMessage("Ready")
    
    def _on_auto_crop_changed(self, state: int):
        """Handle auto-crop checkbox change."""
        self.view_model.settings.auto_crop_output = (state == Qt.CheckState.Checked.value)
    
    def _on_save_folder_changed(self, text: str):
        """Handle save folder text change."""
        self.view_model.settings.default_save_folder = text
    
    def _on_browse_model(self):
        """Handle browse model button."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select ONNX Model",
            str(self.view_model.settings.model_path.parent),
            "ONNX Models (*.onnx)"
        )
        
        if file_path:
            self.view_model.settings.model_path = Path(file_path)
            self.txt_model.setText(str(file_path))
            self.status_bar.showMessage(f"Model changed: {file_path} (Restart required)")
            
            QMessageBox.information(
                self,
                "Model Changed",
                "Model path updated successfully!\n\n"
                "Please restart the application for changes to take effect."
            )
    
    def _on_device_changed(self):
        """Handle device selection change."""
        device_id = self.device_group.checkedId()
        
        if device_id == 0:
            provider = "CPUExecutionProvider"
        elif device_id == 1:
            provider = "CUDAExecutionProvider"
        else:
            provider = "DmlExecutionProvider"
        
        self.view_model.settings.execution_provider = provider
        self.status_bar.showMessage(f"Device changed to: {provider} (Restart required)")
        
        QMessageBox.information(
            self,
            "Device Changed",
            f"Execution provider set to: {provider}\n\n"
            "Please restart the application for changes to take effect."
        )
    
    def _on_browse_save_folder(self):
        """Handle browse save folder button."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Default Save Folder",
            self.view_model.settings.default_save_folder or str(Path.home())
        )
        if folder:
            self.txt_save_folder.setText(folder)
            self.view_model.settings.default_save_folder = folder
    
    def _on_checkerboard_toggled(self, state: int):
        """Handle checkerboard checkbox toggle."""
        if self.view_model.last_result:
            use_checkerboard = (state == Qt.CheckState.Checked.value)
            self.preview_output.set_image_from_array(
                self.view_model.last_result.output.data,
                use_checkerboard=use_checkerboard
            )
    
    def _on_batch_process(self):
        """Handle batch process button."""
        # Select input folder
        input_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Input Folder",
            str(Path.home())
        )
        
        if not input_folder:
            return
        
        # Select output folder
        output_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            str(Path(input_folder).parent)
        )
        
        if not output_folder:
            return
        
        # Find all image files
        input_path = Path(input_folder)
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
        image_files = [
            f for f in input_path.iterdir()
            if f.suffix.lower() in image_extensions
        ]
        
        if not image_files:
            QMessageBox.warning(
                self,
                "No Images",
                "No image files found in selected folder."
            )
            return
        
        # Confirm batch processing
        reply = QMessageBox.question(
            self,
            "Batch Process",
            f"Process {len(image_files)} images?\n\n"
            f"Input: {input_folder}\n"
            f"Output: {output_folder}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            asyncio.create_task(
                self._run_batch_process(image_files, Path(output_folder))
            )
    
    async def _run_batch_process(self, image_files: List[Path], output_folder: Path):
        """Run batch processing."""
        from src.application.use_cases.batch_process_use_case import BatchProcessUseCase
        
        # Create batch use case
        batch_use_case = BatchProcessUseCase(
            engine=self.view_model.use_case.engine,
            image_io=self.view_model.use_case.image_io,
            settings=self.view_model.settings,
            max_workers=4
        )
        
        # Create progress dialog
        progress_dialog = QMessageBox(self)
        progress_dialog.setWindowTitle("Batch Processing")
        progress_dialog.setText("Processing images...")
        progress_dialog.setStandardButtons(QMessageBox.StandardButton.NoButton)
        progress_dialog.show()
        
        async def progress_callback(progress):
            """Update progress dialog."""
            progress_dialog.setText(
                f"Processing: {progress.current_file}\n"
                f"Completed: {progress.completed}/{progress.total}\n"
                f"Failed: {progress.failed}\n"
                f"Progress: {progress.percentage:.1f}%\n"
                f"ETA: {progress.eta_ms/1000:.1f}s"
            )
        
        try:
            result = await batch_use_case.execute(
                image_paths=image_files,
                output_folder=output_folder,
                progress_callback=progress_callback
            )
            
            progress_dialog.close()
            
            # Show summary
            QMessageBox.information(
                self,
                "Batch Complete",
                f"Batch processing complete!\n\n"
                f"Total: {result.total}\n"
                f"Successful: {result.successful}\n"
                f"Failed: {result.failed}\n"
                f"Success rate: {result.success_rate:.1f}%\n"
                f"Total time: {result.total_time_ms/1000:.1f}s\n\n"
                f"Output folder: {output_folder}"
            )
            
        except Exception as e:
            progress_dialog.close()
            QMessageBox.critical(
                self,
                "Batch Error",
                f"Batch processing failed:\n{str(e)}"
            )
    
    def _on_checkerboard_toggled(self, state: int):
        """Handle checkerboard checkbox toggle."""
        if self.view_model.last_result:
            use_checkerboard = (state == Qt.CheckState.Checked.value)
            self.preview_output.set_image_from_array(
                self.view_model.last_result.output.data,
                use_checkerboard=use_checkerboard
            )
    
    def _on_threshold_changed(self, value: int):
        """Handle threshold slider change - Update preview real-time."""
        threshold = value / 100.0
        self.label_threshold.setText(f"{threshold:.2f}")
        self.view_model.settings.threshold = threshold
        
        # Reprocess and update preview
        self._reprocess_with_settings()
    
    def _on_smooth_changed(self, value: int):
        """Handle smooth slider change - Update preview real-time."""
        self.label_smooth.setText(f"{value} px")
        self.view_model.settings.smooth_pixels = value
        
        # Reprocess and update preview
        self._reprocess_with_settings()
    
    def _on_feather_changed(self, value: int):
        """Handle feather slider change - Update preview real-time."""
        self.label_feather.setText(f"{value} px")
        self.view_model.settings.feather_pixels = value
        
        # Reprocess and update preview
        self._reprocess_with_settings()
    
    def _on_pick_color(self):
        """Handle pick color button - Update preview real-time."""
        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor
        
        # Get initial color
        initial_color = QColor(*self.bg_color) if self.bg_color else QColor(255, 255, 255)
        
        color = QColorDialog.getColor(
            initial_color,
            self,
            "Select Background Preview Color"
        )
        
        if color.isValid():
            self.bg_color = (color.red(), color.green(), color.blue())
            self.lbl_color_preview.setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); "
                f"border: 1px solid #000;"
            )
            
            # Update preview with new color (real-time)
            if hasattr(self, 'transparent_result'):
                self._update_preview_with_background()
    
    def _on_clear_color(self):
        """Clear background color - Show transparent."""
        self.bg_color = None
        self.lbl_color_preview.setStyleSheet("background-color: transparent; border: 1px solid #000;")
        
        # Update preview to transparent
        if hasattr(self, 'transparent_result'):
            self._update_preview_with_background()
    
    def _update_preview_with_background(self):
        """Update preview with current background color or transparent."""
        import numpy as np
        
        if not hasattr(self, 'transparent_result'):
            return
        
        rgba = self.transparent_result.copy()
        
        if self.bg_color is not None:
            # Composite with solid color background
            rgb = rgba[:, :, :3].astype(np.float32)
            alpha = rgba[:, :, 3:4].astype(np.float32) / 255.0
            
            # Create background with color
            bg_color = np.array(self.bg_color, dtype=np.float32)
            background = np.full_like(rgb, bg_color)
            
            # Composite: foreground * alpha + background * (1 - alpha)
            result_rgb = rgb * alpha + background * (1 - alpha)
            result_rgb = np.clip(result_rgb, 0, 255).astype(np.uint8)
            
            # Create opaque RGBA
            result = np.dstack([result_rgb, np.full((rgba.shape[0], rgba.shape[1]), 255, dtype=np.uint8)])
            
            # Display without checkerboard (solid background)
            self.preview_output.set_image_from_array(result, use_checkerboard=False)
        else:
            # Display transparent with checkerboard
            use_checkerboard = self.chk_checkerboard.isChecked()
            self.preview_output.set_image_from_array(rgba, use_checkerboard=use_checkerboard)
    
    def _reprocess_with_settings(self):
        """Reprocess mask with current settings and update preview."""
        if not hasattr(self, 'raw_mask') or self.raw_mask is None:
            return
        
        if not hasattr(self, 'original_image') or self.original_image is None:
            return
        
        # Import necessary modules
        from src.domain.services.post_process_mask import PostProcessMask
        from src.domain.services.alpha_compose import AlphaCompose
        
        # Re-apply post-processing with current settings
        processed_mask = PostProcessMask.apply(self.raw_mask, self.view_model.settings)
        
        # Compose new RGBA
        output = AlphaCompose.compose(self.original_image, processed_mask)
        
        # Update transparent result
        self.transparent_result = output.data.copy()
        
        # Update preview with current background color
        self._update_preview_with_background()
    
    def _on_save_mask(self):
        """Handle save mask button."""
        if not self.input_image_path or not self.view_model.last_result:
            return
        
        # Ask for mask format
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Export Mask Format")
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Select mask format:"))
        radio_grayscale = QRadioButton("Grayscale (0-255)")
        radio_binary = QRadioButton("Binary (Black/White)")
        radio_alpha = QRadioButton("Alpha Channel")
        radio_grayscale.setChecked(True)
        
        layout.addWidget(radio_grayscale)
        layout.addWidget(radio_binary)
        layout.addWidget(radio_alpha)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Determine format
            if radio_grayscale.isChecked():
                format_type = "grayscale"
            elif radio_binary.isChecked():
                format_type = "binary"
            else:
                format_type = "alpha"
            
            asyncio.create_task(self._export_mask(format_type))
    
    async def _export_mask(self, format_type: str):
        """Export mask asynchronously."""
        from src.application.use_cases.export_mask_use_case import ExportMaskUseCase
        
        try:
            # Create use case
            export_use_case = ExportMaskUseCase(
                engine=self.view_model.use_case.engine,
                image_io=self.view_model.use_case.image_io,
                settings=self.view_model.settings
            )
            
            # Export based on format
            if format_type == "grayscale":
                result = await export_use_case.execute_grayscale(self.input_image_path)
            elif format_type == "binary":
                result = await export_use_case.execute_binary(self.input_image_path)
            else:
                result = await export_use_case.execute_alpha(self.input_image_path)
            
            # Ask where to save
            default_folder = self.view_model.settings.default_save_folder or str(self.input_image_path.parent)
            default_name = f"{self.input_image_path.stem}_mask.png"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Mask",
                str(Path(default_folder) / default_name),
                "PNG Image (*.png)"
            )
            
            if file_path:
                await self.view_model.use_case.image_io.save_png_rgba(
                    result.output,
                    Path(file_path)
                )
                self.status_bar.showMessage(f"Mask saved: {file_path} ({result.processing_time_ms:.0f}ms)")
                
                QMessageBox.information(
                    self,
                    "Mask Exported",
                    f"Mask exported successfully!\n\n"
                    f"Format: RGBA\n"
                    f"Time: {result.processing_time_ms:.0f}ms\n"
                    f"File: {file_path}"
                )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export mask:\n{str(e)}"
            )
    
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle drop event."""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            file_path = Path(files[0])
            # Check if it's an image
            if file_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}:
                self.input_image_path = file_path
                
                # Display image
                pixmap = QPixmap(str(file_path))
                self.preview_input.set_image(pixmap, use_checkerboard=False)
                self.preview_input.fit_to_view()
                
                self.btn_remove.setEnabled(True)
                self.btn_save_mask.setEnabled(False)
                self.status_bar.showMessage(f"Loaded: {file_path} (drag & drop)")
            else:
                QMessageBox.warning(
                    self,
                    "Invalid File",
                    "Please drop an image file (JPG, PNG, WebP, BMP)"
                )
