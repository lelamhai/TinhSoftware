"""Image preview widget with checkerboard background."""
from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPixmap, QPainter, QImage, QPen, QColor, QWheelEvent, QMouseEvent
import numpy as np


class ImagePreviewWidget(QLabel):
    """Image preview with checkerboard background, zoom, and pan."""
    
    def __init__(self, parent=None):
        """Initialize preview widget."""
        super().__init__(parent)
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(500, 400)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Original image data
        self.original_pixmap: QPixmap | None = None
        self.show_checkerboard = False
        
        # Zoom and pan
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.pan_offset = QPoint(0, 0)
        self.last_pan_point = QPoint()
        self.is_panning = False
        
        # Enable mouse tracking
        self.setMouseTracking(True)
    
    def set_image(self, pixmap: QPixmap, use_checkerboard: bool = False):
        """
        Set image to display.
        
        Args:
            pixmap: Image to display
            use_checkerboard: Whether to show checkerboard background (for transparency)
        """
        self.original_pixmap = pixmap
        self.show_checkerboard = use_checkerboard
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.update_display()
    
    def set_image_from_array(self, image_array: np.ndarray, use_checkerboard: bool = False):
        """
        Set image from numpy array.
        
        Args:
            image_array: Image array (RGB or RGBA)
            use_checkerboard: Whether to show checkerboard background
        """
        height, width = image_array.shape[:2]
        channels = image_array.shape[2] if image_array.ndim == 3 else 1
        
        if channels == 4:
            # RGBA
            bytes_per_line = 4 * width
            qimage = QImage(
                image_array.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGBA8888
            )
        elif channels == 3:
            # RGB
            bytes_per_line = 3 * width
            qimage = QImage(
                image_array.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGB888
            )
        else:
            # Grayscale
            bytes_per_line = width
            qimage = QImage(
                image_array.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_Grayscale8
            )
        
        pixmap = QPixmap.fromImage(qimage.copy())
        self.set_image(pixmap, use_checkerboard)
    
    def clear_image(self):
        """Clear displayed image."""
        self.original_pixmap = None
        self.clear()
        self.setText("No image loaded")
    
    def update_display(self):
        """Update the displayed image with zoom and pan."""
        if self.original_pixmap is None:
            return
        
        # Create a pixmap with checkerboard if needed
        if self.show_checkerboard:
            display_pixmap = self._create_checkerboard_image(self.original_pixmap)
        else:
            display_pixmap = self.original_pixmap
        
        # Apply zoom
        scaled_size = display_pixmap.size() * self.zoom_factor
        scaled_pixmap = display_pixmap.scaled(
            scaled_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.setPixmap(scaled_pixmap)
    
    def _create_checkerboard_image(self, pixmap: QPixmap) -> QPixmap:
        """
        Create image with checkerboard background for transparency.
        
        Args:
            pixmap: Original image (should have alpha channel)
            
        Returns:
            Image with checkerboard background
        """
        # Create checkerboard pattern
        checker_size = 16
        width = pixmap.width()
        height = pixmap.height()
        
        result = QPixmap(width, height)
        painter = QPainter(result)
        
        # Draw checkerboard
        color1 = QColor(200, 200, 200)
        color2 = QColor(255, 255, 255)
        
        for y in range(0, height, checker_size):
            for x in range(0, width, checker_size):
                # Alternate colors
                if ((x // checker_size) + (y // checker_size)) % 2 == 0:
                    painter.fillRect(x, y, checker_size, checker_size, color1)
                else:
                    painter.fillRect(x, y, checker_size, checker_size, color2)
        
        # Draw image on top
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        
        return result
    
    def fit_to_view(self):
        """Fit image to view size."""
        if self.original_pixmap is None:
            return
        
        # Calculate zoom to fit
        pixmap_size = self.original_pixmap.size()
        widget_size = self.size()
        
        width_ratio = widget_size.width() / pixmap_size.width()
        height_ratio = widget_size.height() / pixmap_size.height()
        
        self.zoom_factor = min(width_ratio, height_ratio, 1.0)
        self.pan_offset = QPoint(0, 0)
        self.update_display()
    
    def reset_zoom(self):
        """Reset zoom to 100%."""
        self.zoom_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.update_display()
    
    def zoom_in(self):
        """Zoom in by 25%."""
        self.zoom_factor = min(self.zoom_factor * 1.25, self.max_zoom)
        self.update_display()
    
    def zoom_out(self):
        """Zoom out by 25%."""
        self.zoom_factor = max(self.zoom_factor / 1.25, self.min_zoom)
        self.update_display()
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming."""
        if self.original_pixmap is None:
            return
        
        # Get wheel delta
        delta = event.angleDelta().y()
        
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for panning."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_panning = True
            self.last_pan_point = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for panning."""
        if self.is_panning:
            delta = event.pos() - self.last_pan_point
            self.pan_offset += delta
            self.last_pan_point = event.pos()
            # Note: Pan functionality would require custom paintEvent
            # For simplicity, we're keeping it basic in Phase 2
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
