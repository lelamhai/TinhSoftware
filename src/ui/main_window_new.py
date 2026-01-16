"""Modern redesigned main window."""
import asyncio
from pathlib import Path
from typing import Optional, List
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QMessageBox, QGroupBox, QSlider, QCheckBox,
    QStatusBar, QFrame, QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent

from .view_models.main_view_model import MainViewModel
from .widgets.image_preview import ImagePreviewWidget
from .translations import Translator


class MainWindowNew(QMainWindow):
    """Modern redesigned main window with better UX."""
    
    def __init__(self, view_model: MainViewModel):
        super().__init__()
        self.view_model = view_model
        self.translator = Translator('vi')  # Default to Vietnamese
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
        
        # Main vertical layout (top bar + content)
        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setSpacing(0)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top bar with language selector
        top_bar = QWidget()
        top_bar.setStyleSheet("background: white; border-bottom: 1px solid #dfe6e9;")
        top_bar.setFixedHeight(50)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(20, 0, 20, 0)
        
        # App title on left
        title_label = QLabel("🎨 RemoveBG - AI Background Removal")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch()
        
        # Language selector on right
        self.lang_selector = QComboBox()
        self.lang_selector.addItem("VI - Tiếng Việt", "vi")
        self.lang_selector.addItem("EN - English", "en")
        self.lang_selector.setCurrentIndex(0)
        self.lang_selector.setMinimumWidth(180)
        self.lang_selector.setStyleSheet("""
            QComboBox {
                padding: 8px 15px;
                border: 2px solid #3498db;
                border-radius: 6px;
                background: white;
                font-size: 13px;
                font-weight: bold;
                color: #2c3e50;
            }
            QComboBox:hover {
                border-color: #2980b9;
                background: #ecf0f1;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #3498db;
                margin-right: 8px;
            }
        """)
        self.lang_selector.currentIndexChanged.connect(self._on_language_changed)
        top_bar_layout.addWidget(self.lang_selector)
        
        outer_layout.addWidget(top_bar)
        
        # Content area (2 columns)
        content_widget = QWidget()
        main_layout = QHBoxLayout(content_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # LEFT COLUMN - Single preview + process button
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel, stretch=3)
        
        # RIGHT COLUMN - All controls
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, stretch=2)
        
        outer_layout.addWidget(content_widget, stretch=1)
        
        # Status bar (simple, no language selector)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.translator.t('status_ready'))
    
    def _create_left_panel(self) -> QWidget:
        """Create left panel with single preview and process button."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Single preview area (shows input or output)
        self.input_group = QGroupBox(self.translator.t('input_image'))
        input_layout = QVBoxLayout()
        
        # Image preview
        self.preview_input = ImagePreviewWidget()
        self.preview_input.setMinimumHeight(500)
        input_layout.addWidget(self.preview_input)
        
        # Drag & Drop overlay label
        self.drop_area = QLabel(self.translator.t('drag_drop_text'))
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 3px dashed #3498db;
                border-radius: 10px;
                background: rgba(236, 240, 241, 0.95);
                font-size: 18px;
                font-weight: bold;
                color: #3498db;
                padding: 40px;
            }
            QLabel:hover {
                background: rgba(213, 219, 219, 0.95);
                border-color: #2980b9;
                color: #2980b9;
            }
        """)
        self.drop_area.mousePressEvent = lambda e: self._on_open_image()
        self.drop_area.setParent(self.preview_input)
        self.drop_area.setGeometry(30, 100, 540, 200)
        
        # Zoom controls overlay (top-left corner)
        zoom_controls_widget = QWidget(self.preview_input)
        zoom_controls_layout = QVBoxLayout(zoom_controls_widget)
        zoom_controls_layout.setContentsMargins(0, 0, 0, 0)
        zoom_controls_layout.setSpacing(8)
        
        self.btn_fit_input = QPushButton("⛶")
        self.btn_zoom_in_input = QPushButton("+")
        self.btn_zoom_out_input = QPushButton("−")
        
        # Modern circular button style with shadow and gradient
        icon_button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95), 
                    stop:1 rgba(245, 245, 245, 0.95));
                border: none;
                border-radius: 20px;
                padding: 0px;
                font-size: 18px;
                font-weight: bold;
                color: #3498db;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, 
                    stop:1 #2980b9);
                border: none;
                color: white;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, 
                    stop:1 #21618c);
                border: none;
                color: white;
            }
        """
        self.btn_fit_input.setStyleSheet(icon_button_style)
        self.btn_zoom_in_input.setStyleSheet(icon_button_style)
        self.btn_zoom_out_input.setStyleSheet(icon_button_style)
        
        self.btn_fit_input.setToolTip(self.translator.t('fit'))
        self.btn_zoom_in_input.setToolTip(self.translator.t('zoom_in'))
        self.btn_zoom_out_input.setToolTip(self.translator.t('zoom_out'))
        
        # Add shadow effect
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        for btn in [self.btn_fit_input, self.btn_zoom_in_input, self.btn_zoom_out_input]:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(8)
            shadow.setColor(QColor(0, 0, 0, 80))
            shadow.setOffset(0, 2)
            btn.setGraphicsEffect(shadow)
        
        zoom_controls_layout.addWidget(self.btn_fit_input)
        zoom_controls_layout.addWidget(self.btn_zoom_in_input)
        zoom_controls_layout.addWidget(self.btn_zoom_out_input)
        
        zoom_controls_widget.setGeometry(10, 10, 40, 136)
        zoom_controls_widget.setStyleSheet("background: transparent; border: none;")
        
        self.input_group.setLayout(input_layout)
        layout.addWidget(self.input_group, stretch=1)
        
        # Action buttons container (modern card design)
        actions_container = QWidget()
        actions_container.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(15, 15, 15, 15)
        actions_layout.setSpacing(12)
        
        # Change Image Button (modern design with icon)
        self.btn_change_image = QPushButton(self.translator.t('change_image').upper())
        self.btn_change_image.setMinimumHeight(55)
        self.btn_change_image.clicked.connect(self._on_open_image)
        self.btn_change_image.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6c757d, stop:1 #495057);
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a6268, stop:1 #343a40);
            }
            QPushButton:pressed {
                background: #343a40;
            }
        """)
        actions_layout.addWidget(self.btn_change_image, stretch=1)
        
        # Process Button (Remove Background / Reset)
        self.btn_process = QPushButton(self.translator.t('remove_background').upper())
        self.btn_process.setMinimumHeight(55)
        self.btn_process.setEnabled(False)
        self.btn_process.setProperty('is_reset_mode', False)
        self.btn_process.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2ecc71);
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2980b9, stop:1 #27ae60);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #21618c, stop:1 #1e8449);
            }
            QPushButton:disabled {
                background: #bdc3c7;
                color: #95a5a6;
            }
        """)
        actions_layout.addWidget(self.btn_process, stretch=2)
        
        layout.addWidget(actions_container)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create right panel with all controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Processing Info
        self.info_group = QGroupBox(self.translator.t('processing_info'))
        info_layout = QVBoxLayout()
        self.lbl_info = QLabel(self.translator.t('no_image_processed'))
        self.lbl_info.setWordWrap(True)
        info_layout.addWidget(self.lbl_info)
        self.info_group.setLayout(info_layout)
        layout.addWidget(self.info_group)
        
        # Adjustments
        self.adjust_group = QGroupBox(self.translator.t('fine_tune'))
        adjust_layout = QVBoxLayout()
        
        # Threshold
        threshold_layout = QHBoxLayout()
        self.lbl_threshold_title = QLabel(self.translator.t('threshold'))
        threshold_layout.addWidget(self.lbl_threshold_title)
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
        self.lbl_smooth_title = QLabel(self.translator.t('smooth'))
        smooth_layout.addWidget(self.lbl_smooth_title)
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
        self.lbl_feather_title = QLabel(self.translator.t('feather'))
        feather_layout.addWidget(self.lbl_feather_title)
        self.slider_feather = QSlider(Qt.Orientation.Horizontal)
        self.slider_feather.setMinimum(0)
        self.slider_feather.setMaximum(10)
        self.slider_feather.setValue(self.view_model.settings.feather_pixels)
        self.label_feather = QLabel(f"{self.view_model.settings.feather_pixels} px")
        feather_layout.addWidget(self.slider_feather, stretch=1)
        feather_layout.addWidget(self.label_feather)
        adjust_layout.addLayout(feather_layout)
        
        self.adjust_group.setLayout(adjust_layout)
        layout.addWidget(self.adjust_group)
        
        # Background Color Preview
        self.bg_group = QGroupBox(self.translator.t('bg_color_preview'))
        bg_layout = QVBoxLayout()
        bg_layout.setSpacing(10)
        
        # Checkerboard checkbox
        self.chk_checkerboard = QCheckBox(self.translator.t('checkerboard'))
        self.chk_checkerboard.setChecked(True)
        bg_layout.addWidget(self.chk_checkerboard)
        
        # Color picker section
        color_container = QWidget()
        color_layout = QHBoxLayout(color_container)
        color_layout.setContentsMargins(0, 5, 0, 5)
        color_layout.setSpacing(10)
        
        self.btn_pick_color = QPushButton(self.translator.t('pick_color'))
        self.btn_pick_color.setEnabled(False)
        self.btn_pick_color.setMinimumHeight(40)
        self.btn_pick_color.setToolTip(self.translator.t('pick_color_tooltip') if hasattr(self.translator, 't') else "Click to pick color, double-click to clear")
        color_layout.addWidget(self.btn_pick_color, stretch=2)
        
        # Color preview box (larger) - double-click to clear
        self.lbl_color_preview = QLabel("")
        self.lbl_color_preview.setFixedSize(80, 40)
        self.lbl_color_preview.setStyleSheet(
            "background-color: transparent; "
            "border: 2px solid #bdc3c7; "
            "border-radius: 8px;"
        )
        self.lbl_color_preview.setToolTip("Double-click to clear color")
        self.lbl_color_preview.mouseDoubleClickEvent = lambda e: self._on_clear_color()
        color_layout.addWidget(self.lbl_color_preview)
        
        bg_layout.addWidget(color_container)
        
        self.bg_group.setLayout(bg_layout)
        layout.addWidget(self.bg_group)
        
        # Options
        self.options_group = QGroupBox(self.translator.t('options'))
        options_layout = QVBoxLayout()
        
        self.chk_auto_crop = QCheckBox(self.translator.t('auto_crop'))
        self.chk_auto_crop.setChecked(self.view_model.settings.auto_crop_output)
        options_layout.addWidget(self.chk_auto_crop)
        
        self.options_group.setLayout(options_layout)
        layout.addWidget(self.options_group)
        
        # Save & Export Button (moved to bottom)
        self.actions_group = QGroupBox(self.translator.t('save_export'))
        actions_layout = QVBoxLayout()
        
        # Save PNG button only
        self.btn_save = QPushButton(self.translator.t('save_png').upper())
        self.btn_save.setMinimumHeight(55)
        self.btn_save.setEnabled(False)
        self.btn_save.setToolTip(self.translator.t('save_png_tooltip'))
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        actions_layout.addWidget(self.btn_save)
        
        self.actions_group.setLayout(actions_layout)
        layout.addWidget(self.actions_group)
        
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
    
    def _update_zoom_label(self):
        """Update zoom percentage label (removed - no longer used)."""
        pass
    
    def _connect_signals(self):
        """Connect UI signals."""
        # Preview controls (only input preview now)
        self.btn_fit_input.clicked.connect(self._on_fit_view)
        self.btn_zoom_in_input.clicked.connect(self._on_zoom_in)
        self.btn_zoom_out_input.clicked.connect(self._on_zoom_out)
        
        # Action buttons - Process button toggles between remove/reset
        self.btn_process.clicked.connect(self._on_process_clicked)
        self.btn_save.clicked.connect(self._on_save_image)
        
        # Sliders
        self.slider_threshold.valueChanged.connect(self._on_threshold_changed)
        self.slider_smooth.valueChanged.connect(self._on_smooth_changed)
        self.slider_feather.valueChanged.connect(self._on_feather_changed)
        
        # Background color
        self.btn_pick_color.clicked.connect(self._on_pick_color)
        
        # Options
        self.chk_auto_crop.stateChanged.connect(self._on_auto_crop_changed)
        self.chk_checkerboard.stateChanged.connect(self._on_checkerboard_changed)
    
    def _on_fit_view(self):
        """Handle fit to view button."""
        self.preview_input.fit_to_view()
        self._update_zoom_label()
    
    def _on_zoom_in(self):
        """Handle zoom in button."""
        self.preview_input.zoom_in()
        self._update_zoom_label()
    
    def _on_zoom_out(self):
        """Handle zoom out button."""
        self.preview_input.zoom_out()
        self._update_zoom_label()
    
    def _on_process_clicked(self):
        """Handle process button click - toggles between remove background and reset."""
        is_reset_mode = self.btn_process.property('is_reset_mode')
        
        if is_reset_mode:
            # Reset mode - restore original image
            self._on_reset()
        else:
            # Remove background mode
            self._on_remove_background()
    
    # Event handlers (copy from original main_window.py)
    def _on_open_image(self):
        """Handle open image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.translator.t('select_image'),
            "",
            f"{self.translator.t('image_files')} (*.jpg *.jpeg *.png *.webp *.bmp)"
        )
        
        if file_path:
            self.input_image_path = Path(file_path)
            pixmap = QPixmap(str(file_path))
            self.preview_input.set_image(pixmap, use_checkerboard=False)
            self.preview_input.fit_to_view()
            
            # Hide drop area overlay
            self.drop_area.hide()
            
            self.btn_process.setEnabled(True)
            self.status_bar.showMessage(f"{self.translator.t('loaded')}: {file_path}")
    
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
            
            # Hide drop area overlay
            self.drop_area.hide()
            
            self.btn_process.setEnabled(True)
            self.status_bar.showMessage(f"{self.translator.t('loaded')}: {files[0]}")
    
    def _on_remove_background(self):
        """Handle remove background button."""
        if not self.input_image_path:
            return
        
        self.btn_process.setEnabled(False)
        self.btn_process.setText(self.translator.t('processing').upper())
        self.status_bar.showMessage(self.translator.t('processing'))
        
        QTimer.singleShot(100, lambda: asyncio.create_task(self._process_image()))
    
    async def _process_image(self):
        """Process image asynchronously."""
        try:
            result = await self.view_model.remove_background(self.input_image_path)
            
            self.transparent_result = result.output.data.copy()
            self.raw_mask = result.raw_mask
            self.original_image = result.original_image
            
            self.output_image_path = self.input_image_path.parent / f"{self.input_image_path.stem}_nobg.png"
            
            # Show result on INPUT preview (overlay)
            self._update_preview_with_background()
            self.preview_input.fit_to_view()
            
            # Change button to Reset mode
            self.btn_process.setText(self.translator.t('reset').upper())
            self.btn_process.setProperty('is_reset_mode', True)
            self.btn_process.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #e74c3c, stop:1 #c0392b);
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                    border: none;
                    border-radius: 10px;
                    padding: 15px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #c0392b, stop:1 #a93226);
                }
            """)
            
            # Enable save button and color picker
            self.btn_save.setEnabled(True)
            self.btn_pick_color.setEnabled(True)
            
            # Update info
            t = self.translator.t
            self.lbl_info.setText(
                f"{t('processing_complete')}\n"
                f"{t('time')}: {result.processing_time_ms:.0f}ms\n"
                f"{t('input')}: {result.input_size[0]}x{result.input_size[1]}\n"
                f"{t('size')}: {result.output_size_mb:.2f} MB"
            )
            
            self.status_bar.showMessage(f"{t('done')} ({result.processing_time_ms:.0f}ms)")
            self.view_model.last_result = result
            
        except Exception as e:
            t = self.translator.t
            QMessageBox.critical(self, t('error'), f"{t('failed_process')}\n{str(e)}")
            self.status_bar.showMessage(t('processing_failed'))
        
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
        if state == 0:  # Unchecked
            # Set màu trắng mặc định
            if self.bg_color is None:
                self.bg_color = (255, 255, 255)
                self.lbl_color_preview.setStyleSheet(
                    "background-color: rgb(255, 255, 255); "
                    "border: 2px solid #bdc3c7; border-radius: 5px;"
                )
        
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
                f"border: 2px solid #bdc3c7; "
                f"border-radius: 8px;"
            )
            
            # Tự động uncheck checkerboard khi pick color
            self.chk_checkerboard.setChecked(False)
            
            if hasattr(self, 'transparent_result'):
                self._update_preview_with_background()
    
    def _on_clear_color(self):
        self.bg_color = None
        self.lbl_color_preview.setStyleSheet(
            "background-color: transparent; "
            "border: 2px solid #bdc3c7; "
            "border-radius: 8px;"
        )
        
        # Tự động check checkerboard khi clear color
        self.chk_checkerboard.setChecked(True)
        
        if hasattr(self, 'transparent_result'):
            self._update_preview_with_background()
    
    def _update_preview_with_background(self):
        import numpy as np
        
        if not hasattr(self, 'transparent_result') or self.transparent_result is None:
            return
        
        rgba = self.transparent_result.copy()
        
        # Check checkerboard state first
        use_checkerboard = self.chk_checkerboard.isChecked()
        
        if use_checkerboard:
            # Show with checkerboard pattern
            self.preview_input.update_image_from_array_keep_view(rgba, use_checkerboard=True)
        elif self.bg_color is not None:
            # Show with solid color background
            rgb = rgba[:, :, :3].astype(np.float32)
            alpha = rgba[:, :, 3:4].astype(np.float32) / 255.0
            
            bg_color = np.array(self.bg_color, dtype=np.float32)
            background = np.full_like(rgb, bg_color)
            
            result_rgb = rgb * alpha + background * (1 - alpha)
            result_rgb = np.clip(result_rgb, 0, 255).astype(np.uint8)
            
            result = np.dstack([result_rgb, np.full((rgba.shape[0], rgba.shape[1]), 255, dtype=np.uint8)])
            self.preview_input.update_image_from_array_keep_view(result, use_checkerboard=False)
        else:
            # No color and no checkerboard - shouldn't happen, but show transparent
            self.preview_input.update_image_from_array_keep_view(rgba, use_checkerboard=False)
    
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
            self.translator.t('save_png_dialog'),
            str(default_path),
            f"{self.translator.t('png_image')} (*.png)"
        )
        
        if file_path:
            asyncio.create_task(self._save_image(Path(file_path)))
    
    async def _save_image(self, path: Path):
        """Save image asynchronously."""
        t = self.translator.t
        try:
            await self.view_model.save_output(path)
            self.status_bar.showMessage(f"{t('image_saved')} {path}")
            QMessageBox.information(self, t('success'), f"{t('image_saved')}\n{path}")
        except Exception as e:
            QMessageBox.critical(self, t('error'), f"{t('failed_save')}\n{str(e)}")
    
    def _on_save_mask(self):
        """Export mask - copy from original."""
        if not self.input_image_path or not self.view_model.last_result:
            return
        
        # Ask for mask format
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QDialogButtonBox
        
        t = self.translator.t
        dialog = QDialog(self)
        dialog.setWindowTitle(t('export_mask_format'))
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel(t('select_mask_format')))
        radio_grayscale = QRadioButton(t('grayscale'))
        radio_binary = QRadioButton(t('binary'))
        radio_alpha = QRadioButton(t('alpha_channel'))
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
        """Reset to original image."""
        if self.input_image_path and self.input_image_path.exists():
            # Restore original image
            pixmap = QPixmap(str(self.input_image_path))
            self.preview_input.set_image(pixmap, use_checkerboard=False)
            self.preview_input.fit_to_view()
            
            # Clear processed data
            self.transparent_result = None
            self.raw_mask = None
            self.original_image = None
            
            # Change button back to Remove Background mode
            self.btn_process.setText(self.translator.t('remove_background').upper())
            self.btn_process.setProperty('is_reset_mode', False)
            self.btn_process.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #3498db, stop:1 #2ecc71);
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                    border: none;
                    border-radius: 10px;
                    padding: 15px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2980b9, stop:1 #27ae60);
                }
            """)
            self.btn_process.setEnabled(True)
            
            # Disable save buttons
            self.btn_save.setEnabled(False)
            self.btn_pick_color.setEnabled(False)
            
            # Reset info
            self.lbl_info.setText(self.translator.t('no_image_processed'))
            self.status_bar.showMessage(self.translator.t('status_ready'))
        else:
            # No image - full reset
            self.input_image_path = None
            self.output_image_path = None
            self.transparent_result = None
            self.raw_mask = None
            self.original_image = None
            
            self.preview_input.clear_image()
            
            # Show drop area overlay again
            self.drop_area.show()
            
            self.btn_process.setEnabled(False)
            self.btn_save.setEnabled(False)
            self.btn_pick_color.setEnabled(False)
        
        self.lbl_info.setText(self.translator.t('no_image_processed'))
        self.status_bar.showMessage(self.translator.t('status_ready'))
    
    def _on_language_changed(self, index: int):
        """Handle language change."""
        lang_code = self.lang_selector.itemData(index)
        self.translator.set_language(lang_code)
        self._refresh_ui_text()
    
    def _refresh_ui_text(self):
        """Refresh all UI text with current language."""
        t = self.translator.t
        
        # Window title
        self.setWindowTitle(t('window_title'))
        
        # GroupBox titles
        self.input_group.setTitle(t('input_image'))
        self.actions_group.setTitle(t('save_export'))
        self.info_group.setTitle(t('processing_info'))
        self.adjust_group.setTitle(t('fine_tune'))
        self.bg_group.setTitle(t('bg_color_preview'))
        self.options_group.setTitle(t('options'))
        
        # Status bar
        if not self.input_image_path:
            self.status_bar.showMessage(t('status_ready'))
        
        # Drop area
        if self.drop_area.isVisible():
            self.drop_area.setText(t('drag_drop_text'))
        
        # Process button - check current mode
        is_reset_mode = self.btn_process.property('is_reset_mode')
        if is_reset_mode:
            self.btn_process.setText(t('reset').upper())
        else:
            self.btn_process.setText(t('remove_background').upper())
        
        # Save buttons
        self.btn_save.setText(t('save_png').upper())
        self.btn_save.setToolTip(t('save_png_tooltip'))
        
        # Preview buttons - update tooltips only (using icons)
        self.btn_fit_input.setToolTip(t('fit'))
        self.btn_zoom_in_input.setToolTip(t('zoom_in'))
        self.btn_zoom_out_input.setToolTip(t('zoom_out'))
        self.chk_checkerboard.setText(t('checkerboard'))
        
        # Adjustment labels
        self.lbl_threshold_title.setText(t('threshold'))
        self.lbl_smooth_title.setText(t('smooth'))
        self.lbl_feather_title.setText(t('feather'))
        self.label_threshold.setText(f"{self.view_model.settings.threshold:.2f}")
        self.label_smooth.setText(f"{self.view_model.settings.smooth_pixels} px")
        self.label_feather.setText(f"{self.view_model.settings.feather_pixels} px")
        
        # Background color buttons
        self.btn_pick_color.setText(t('pick_color'))
        
        # Checkbox
        self.chk_auto_crop.setText(t('auto_crop'))
        
        # Info text
        if not self.view_model.last_result:
            self.lbl_info.setText(t('no_image_processed'))

