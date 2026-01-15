"""Modern redesigned main window."""
import asyncio
from pathlib import Path
from typing import Optional, List
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QMessageBox, QGroupBox, QSlider, QCheckBox,
    QStatusBar, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent

from .view_models.main_view_model import MainViewModel
from .widgets.image_preview import ImagePreviewWidget


class MainWindowNew(QMainWindow):
    """Modern redesigned main window with better UX."""
    
    def __init__(self, view_model: MainViewModel):
        super().__init__()
        self.view_model = view_model
        self.input_image_path: Optional[Path] = None
        self.output_image_path: Optional[Path] = None
        self.bg_color = None
        self.transparent_result = None
        self.raw_mask = None
        self.original_image = None
        
        self.setWindowTitle("RemoveBG - AI Background Removal")
        self.setGeometry(100, 100, 1600, 900)
        self.setAcceptDrops(True)
        
        self._setup_modern_ui()
        self._connect_signals()
        self._apply_modern_styles()
    
    def _setup_modern_ui(self):
        """Setup modern UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # LEFT COLUMN - Input & Actions
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel, stretch=1)
        
        # RIGHT COLUMN - Output & Settings
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, stretch=1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Drag & drop image to start")
    
    def _create_left_panel(self) -> QWidget:
        """Create left panel with upload and actions."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Upload Area
        upload_group = QGroupBox("📤 UPLOAD IMAGE")
        upload_layout = QVBoxLayout()
        
        # Drag & Drop Area
        self.drop_area = QLabel("Drag & Drop Image Here\nor Click to Browse")
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setMinimumHeight(150)
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 3px dashed #3498db;
                border-radius: 10px;
                background: #ecf0f1;
                font-size: 16px;
                color: #7f8c8d;
                padding: 20px;
            }
            QLabel:hover {
                background: #d5dbdb;
                border-color: #2980b9;
            }
        """)
        self.drop_area.mousePressEvent = lambda e: self._on_open_image()
        upload_layout.addWidget(self.drop_area)
        
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        # Preview
        preview_group = QGroupBox("🖼️ INPUT PREVIEW")
        preview_layout = QVBoxLayout()
        
        self.preview_input = ImagePreviewWidget()
        self.preview_input.setMinimumHeight(300)
        preview_layout.addWidget(self.preview_input)
        
        # Preview controls
        controls = QHBoxLayout()
        self.btn_fit_input = QPushButton("Fit")
        self.btn_zoom_in_input = QPushButton("Zoom +")
        self.btn_zoom_out_input = QPushButton("Zoom -")
        self.lbl_zoom_input = QLabel("100%")
        
        controls.addWidget(self.btn_fit_input)
        controls.addWidget(self.btn_zoom_in_input)
        controls.addWidget(self.btn_zoom_out_input)
        controls.addWidget(self.lbl_zoom_input)
        controls.addStretch()
        preview_layout.addLayout(controls)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group, stretch=1)
        
        # Big Process Button
        self.btn_process = QPushButton("🎯 REMOVE BACKGROUND")
        self.btn_process.setMinimumHeight(60)
        self.btn_process.setEnabled(False)
        self.btn_process.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2ecc71);
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2980b9, stop:1 #27ae60);
            }
            QPushButton:disabled {
                background: #bdc3c7;
            }
        """)
        layout.addWidget(self.btn_process)
        
        # Action Buttons
        actions_group = QGroupBox("💾 SAVE & EXPORT")
        actions_layout = QVBoxLayout()
        
        self.btn_save = QPushButton("💾 Save PNG (Transparent)")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setEnabled(False)
        
        self.btn_export_mask = QPushButton("📄 Export Mask")
        self.btn_export_mask.setMinimumHeight(40)
        self.btn_export_mask.setEnabled(False)
        
        self.btn_batch = QPushButton("📂 Batch Process...")
        self.btn_batch.setMinimumHeight(40)
        
        actions_layout.addWidget(self.btn_save)
        actions_layout.addWidget(self.btn_export_mask)
        actions_layout.addWidget(self.btn_batch)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Reset button
        self.btn_reset = QPushButton("🔄 Reset")
        self.btn_reset.setMinimumHeight(35)
        layout.addWidget(self.btn_reset)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create right panel with output and settings."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Output Preview
        output_group = QGroupBox("✨ OUTPUT PREVIEW")
        output_layout = QVBoxLayout()
        
        self.preview_output = ImagePreviewWidget()
        self.preview_output.setMinimumHeight(400)
        output_layout.addWidget(self.preview_output)
        
        # Output controls
        controls = QHBoxLayout()
        self.btn_fit_output = QPushButton("Fit")
        self.btn_zoom_in_output = QPushButton("Zoom +")
        self.btn_zoom_out_output = QPushButton("Zoom -")
        self.lbl_zoom_output = QLabel("100%")
        self.chk_checkerboard = QCheckBox("Checkerboard")
        self.chk_checkerboard.setChecked(True)
        
        controls.addWidget(self.btn_fit_output)
        controls.addWidget(self.btn_zoom_in_output)
        controls.addWidget(self.btn_zoom_out_output)
        controls.addWidget(self.lbl_zoom_output)
        controls.addStretch()
        controls.addWidget(self.chk_checkerboard)
        output_layout.addLayout(controls)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group, stretch=1)
        
        # Processing Info
        info_group = QGroupBox("📊 PROCESSING INFO")
        info_layout = QVBoxLayout()
        self.lbl_info = QLabel("No image processed yet")
        self.lbl_info.setWordWrap(True)
        info_layout.addWidget(self.lbl_info)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Adjustments
        adjust_group = QGroupBox("🎨 FINE-TUNE ADJUSTMENTS")
        adjust_layout = QVBoxLayout()
        
        # Threshold
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Threshold:"))
        self.slider_threshold = QSlider(Qt.Orientation.Horizontal)
        self.slider_threshold.setMinimum(0)
        self.slider_threshold.setMaximum(100)
        self.slider_threshold.setValue(int(self.view_model.settings.threshold * 100))
        self.label_threshold = QLabel(f"{self.view_model.settings.threshold:.2f}")
        threshold_layout.addWidget(self.slider_threshold, stretch=1)
        threshold_layout.addWidget(self.label_threshold)
        adjust_layout.addLayout(threshold_layout)
        
        # Smooth
        smooth_layout = QHBoxLayout()
        smooth_layout.addWidget(QLabel("Smooth:"))
        self.slider_smooth = QSlider(Qt.Orientation.Horizontal)
        self.slider_smooth.setMinimum(0)
        self.slider_smooth.setMaximum(20)
        self.slider_smooth.setValue(self.view_model.settings.smooth_pixels)
        self.label_smooth = QLabel(f"{self.view_model.settings.smooth_pixels} px")
        smooth_layout.addWidget(self.slider_smooth, stretch=1)
        smooth_layout.addWidget(self.label_smooth)
        adjust_layout.addLayout(smooth_layout)
        
        # Feather
        feather_layout = QHBoxLayout()
        feather_layout.addWidget(QLabel("Feather:"))
        self.slider_feather = QSlider(Qt.Orientation.Horizontal)
        self.slider_feather.setMinimum(0)
        self.slider_feather.setMaximum(10)
        self.slider_feather.setValue(self.view_model.settings.feather_pixels)
        self.label_feather = QLabel(f"{self.view_model.settings.feather_pixels} px")
        feather_layout.addWidget(self.slider_feather, stretch=1)
        feather_layout.addWidget(self.label_feather)
        adjust_layout.addLayout(feather_layout)
        
        adjust_group.setLayout(adjust_layout)
        layout.addWidget(adjust_group)
        
        # Background Color
        bg_group = QGroupBox("🎨 BACKGROUND COLOR PREVIEW")
        bg_layout = QHBoxLayout()
        
        self.btn_pick_color = QPushButton("Pick Color")
        self.btn_pick_color.setEnabled(False)
        self.lbl_color_preview = QLabel("")
        self.lbl_color_preview.setFixedSize(50, 30)
        self.lbl_color_preview.setStyleSheet("background-color: transparent; border: 2px solid #bdc3c7; border-radius: 5px;")
        self.btn_clear_color = QPushButton("Clear")
        self.btn_clear_color.setEnabled(False)
        
        bg_layout.addWidget(QLabel("Preview with:"))
        bg_layout.addWidget(self.btn_pick_color)
        bg_layout.addWidget(self.lbl_color_preview)
        bg_layout.addWidget(self.btn_clear_color)
        bg_layout.addStretch()
        
        bg_group.setLayout(bg_layout)
        layout.addWidget(bg_group)
        
        # Options
        options_group = QGroupBox("⚙️ OPTIONS")
        options_layout = QVBoxLayout()
        
        self.chk_auto_crop = QCheckBox("Auto-crop output")
        self.chk_auto_crop.setChecked(self.view_model.settings.auto_crop_output)
        options_layout.addWidget(self.chk_auto_crop)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        return panel
    
    def _apply_modern_styles(self):
        """Apply modern stylesheet."""
        self.setStyleSheet("""
            QMainWindow {
                background: #f5f6fa;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #dfe6e9;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton:disabled {
                background: #bdc3c7;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #ecf0f1;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #2980b9;
            }
            QCheckBox {
                font-size: 12px;
            }
            QLabel {
                font-size: 12px;
            }
        """)
    
    def _connect_signals(self):
        """Connect UI signals."""
        # Preview controls
        self.btn_fit_input.clicked.connect(lambda: self.preview_input.fit_to_view())
        self.btn_zoom_in_input.clicked.connect(lambda: self.preview_input.zoom_in())
        self.btn_zoom_out_input.clicked.connect(lambda: self.preview_input.zoom_out())
        
        self.btn_fit_output.clicked.connect(lambda: self.preview_output.fit_to_view())
        self.btn_zoom_in_output.clicked.connect(lambda: self.preview_output.zoom_in())
        self.btn_zoom_out_output.clicked.connect(lambda: self.preview_output.zoom_out())
        
        # Action buttons
        self.btn_process.clicked.connect(self._on_remove_background)
        self.btn_save.clicked.connect(self._on_save_image)
        self.btn_export_mask.clicked.connect(self._on_save_mask)
        self.btn_batch.clicked.connect(self._on_batch_process)
        self.btn_reset.clicked.connect(self._on_reset)
        
        # Sliders
        self.slider_threshold.valueChanged.connect(self._on_threshold_changed)
        self.slider_smooth.valueChanged.connect(self._on_smooth_changed)
        self.slider_feather.valueChanged.connect(self._on_feather_changed)
        
        # Background color
        self.btn_pick_color.clicked.connect(self._on_pick_color)
        self.btn_clear_color.clicked.connect(self._on_clear_color)
        
        # Options
        self.chk_auto_crop.stateChanged.connect(self._on_auto_crop_changed)
        self.chk_checkerboard.stateChanged.connect(self._on_checkerboard_changed)
    
    # Event handlers (copy from original main_window.py)
    def _on_open_image(self):
        """Handle open image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Images (*.jpg *.jpeg *.png *.webp *.bmp)"
        )
        
        if file_path:
            self.input_image_path = Path(file_path)
            pixmap = QPixmap(str(file_path))
            self.preview_input.set_image(pixmap, use_checkerboard=False)
            self.preview_input.fit_to_view()
            
            self.drop_area.setText(f"✓ {Path(file_path).name}")
            self.drop_area.setStyleSheet("""
                QLabel {
                    border: 3px solid #27ae60;
                    border-radius: 10px;
                    background: #d5f4e6;
                    font-size: 14px;
                    color: #27ae60;
                    padding: 20px;
                }
            """)
            
            self.btn_process.setEnabled(True)
            self.status_bar.showMessage(f"Loaded: {file_path}")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop."""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.input_image_path = Path(files[0])
            pixmap = QPixmap(str(files[0]))
            self.preview_input.set_image(pixmap, use_checkerboard=False)
            self.preview_input.fit_to_view()
            
            self.drop_area.setText(f"✓ {Path(files[0]).name}")
            self.drop_area.setStyleSheet("""
                QLabel {
                    border: 3px solid #27ae60;
                    border-radius: 10px;
                    background: #d5f4e6;
                    font-size: 14px;
                    color: #27ae60;
                    padding: 20px;
                }
            """)
            
            self.btn_process.setEnabled(True)
            self.status_bar.showMessage(f"Loaded: {files[0]}")
    
    def _on_remove_background(self):
        """Handle remove background button."""
        if not self.input_image_path:
            return
        
        self.btn_process.setEnabled(False)
        self.status_bar.showMessage("Processing...")
        
        QTimer.singleShot(100, lambda: asyncio.create_task(self._process_image()))
    
    async def _process_image(self):
        """Process image asynchronously."""
        try:
            result = await self.view_model.remove_background(self.input_image_path)
            
            self.transparent_result = result.output.data.copy()
            self.raw_mask = result.raw_mask
            self.original_image = result.original_image
            
            self.output_image_path = self.input_image_path.parent / f"{self.input_image_path.stem}_nobg.png"
            
            self._update_preview_with_background()
            self.preview_output.fit_to_view()
            
            self.btn_save.setEnabled(True)
            self.btn_export_mask.setEnabled(True)
            self.btn_pick_color.setEnabled(True)
            self.btn_clear_color.setEnabled(True)
            
            self.lbl_info.setText(
                f"✓ Processing complete!\n"
                f"Time: {result.processing_time_ms:.0f}ms\n"
                f"Input: {result.input_size[0]}x{result.input_size[1]}\n"
                f"Size: {result.output_size_mb:.2f} MB"
            )
            
            self.status_bar.showMessage(f"Done! ({result.processing_time_ms:.0f}ms)")
            self.view_model.last_result = result
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process:\n{str(e)}")
            self.status_bar.showMessage("Error - Processing failed")
        
        self.btn_process.setEnabled(True)
    
    # Copy remaining methods from original main_window.py
    def _on_threshold_changed(self, value: int):
        threshold = value / 100.0
        self.label_threshold.setText(f"{threshold:.2f}")
        self.view_model.settings.threshold = threshold
        self._reprocess_with_settings()
    
    def _on_smooth_changed(self, value: int):
        self.label_smooth.setText(f"{value} px")
        self.view_model.settings.smooth_pixels = value
        self._reprocess_with_settings()
    
    def _on_feather_changed(self, value: int):
        self.label_feather.setText(f"{value} px")
        self.view_model.settings.feather_pixels = value
        self._reprocess_with_settings()
    
    def _on_auto_crop_changed(self, state: int):
        self.view_model.settings.auto_crop_output = (state == Qt.CheckState.Checked.value)
    
    def _on_checkerboard_changed(self, state: int):
        if hasattr(self, 'transparent_result') and self.transparent_result is not None:
            self._update_preview_with_background()
    
    def _on_pick_color(self):
        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor
        
        initial_color = QColor(*self.bg_color) if self.bg_color else QColor(255, 255, 255)
        color = QColorDialog.getColor(initial_color, self, "Select Background Preview Color")
        
        if color.isValid():
            self.bg_color = (color.red(), color.green(), color.blue())
            self.lbl_color_preview.setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); "
                f"border: 2px solid #bdc3c7; border-radius: 5px;"
            )
            
            if hasattr(self, 'transparent_result'):
                self._update_preview_with_background()
    
    def _on_clear_color(self):
        self.bg_color = None
        self.lbl_color_preview.setStyleSheet("background-color: transparent; border: 2px solid #bdc3c7; border-radius: 5px;")
        
        if hasattr(self, 'transparent_result'):
            self._update_preview_with_background()
    
    def _update_preview_with_background(self):
        import numpy as np
        
        if not hasattr(self, 'transparent_result') or self.transparent_result is None:
            return
        
        rgba = self.transparent_result.copy()
        
        if self.bg_color is not None:
            rgb = rgba[:, :, :3].astype(np.float32)
            alpha = rgba[:, :, 3:4].astype(np.float32) / 255.0
            
            bg_color = np.array(self.bg_color, dtype=np.float32)
            background = np.full_like(rgb, bg_color)
            
            result_rgb = rgb * alpha + background * (1 - alpha)
            result_rgb = np.clip(result_rgb, 0, 255).astype(np.uint8)
            
            result = np.dstack([result_rgb, np.full((rgba.shape[0], rgba.shape[1]), 255, dtype=np.uint8)])
            self.preview_output.set_image_from_array(result, use_checkerboard=False)
        else:
            use_checkerboard = self.chk_checkerboard.isChecked()
            self.preview_output.set_image_from_array(rgba, use_checkerboard=use_checkerboard)
    
    def _reprocess_with_settings(self):
        if not hasattr(self, 'raw_mask') or self.raw_mask is None:
            return
        if not hasattr(self, 'original_image') or self.original_image is None:
            return
        
        from src.domain.services.post_process_mask import PostProcessMask
        from src.domain.services.alpha_compose import AlphaCompose
        
        processed_mask = PostProcessMask.apply(self.raw_mask, self.view_model.settings)
        output = AlphaCompose.compose(self.original_image, processed_mask)
        
        self.transparent_result = output.data.copy()
        self._update_preview_with_background()
    
    def _on_save_image(self):
        """Save PNG - copy from original."""
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
    
    def _on_save_mask(self):
        """Export mask - copy from original."""
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
    
    def _on_batch_process(self):
        """Batch process - copy from original."""
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
    
    def _on_reset(self):
        """Reset application state."""
        self.input_image_path = None
        self.output_image_path = None
        self.transparent_result = None
        self.raw_mask = None
        self.original_image = None
        
        self.preview_input.clear_image()
        self.preview_output.clear_image()
        
        self.drop_area.setText("Drag & Drop Image Here\nor Click to Browse")
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 3px dashed #3498db;
                border-radius: 10px;
                background: #ecf0f1;
                font-size: 16px;
                color: #7f8c8d;
                padding: 20px;
            }
            QLabel:hover {
                background: #d5dbdb;
                border-color: #2980b9;
            }
        """)
        
        self.btn_process.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.btn_export_mask.setEnabled(False)
        self.btn_pick_color.setEnabled(False)
        self.btn_clear_color.setEnabled(False)
        
        self.lbl_info.setText("No image processed yet")
        self.status_bar.showMessage("Ready - Drag & drop image to start")
