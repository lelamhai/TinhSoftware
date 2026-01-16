"""Multi-language support for the application."""

TRANSLATIONS = {
    'en': {
        # Window
        'window_title': 'RemoveBG - AI Background Removal',
        'status_ready': 'Ready - Drag & drop image to start',
        
        # Input section
        'input_image': '🖼️ INPUT IMAGE',
        'drag_drop_text': 'Drag & Drop Image Here\nor Click to Browse',
        'loaded': 'Loaded',
        'change_image': 'Change Image',
        
        # Process button
        'remove_background': '🎯 REMOVE BACKGROUND',
        'processing': '⏳ Processing...',
        
        # Save & Export
        'save_export': '💾 SAVE & EXPORT',
        'save_png': '💾 Save PNG',
        'save_png_tooltip': 'Save as transparent PNG',
        'mask': '📄 Mask',
        'mask_tooltip': 'Export mask in different formats',
        'batch': '📂 Batch...',
        'batch_tooltip': 'Batch process multiple images',
        
        # Reset
        'reset': '🔄 Reset',
        
        # Output section
        'output_preview': '✨ OUTPUT PREVIEW',
        'no_image_loaded': 'No image loaded',
        'fit': 'Fit',
        'zoom_in': 'Zoom +',
        'zoom_out': 'Zoom -',
        'checkerboard': 'Checkerboard',
        
        # Processing info
        'processing_info': '📊 PROCESSING INFO',
        'no_image_processed': 'No image processed yet',
        'processing_complete': '✓ Processing complete!',
        'time': 'Time',
        'input': 'Input',
        'size': 'Size',
        
        # Adjustments
        'fine_tune': '🎨 FINE-TUNE ADJUSTMENTS',
        'threshold': 'Threshold:',
        'smooth': 'Smooth:',
        'feather': 'Feather:',
        
        # Background color
        'bg_color_preview': '🎨 BACKGROUND COLOR PREVIEW',
        'preview_with': 'Preview with:',
        'pick_color': 'Pick Color',
        'clear': 'Clear',
        
        # Options
        'options': '⚙️ OPTIONS',
        'auto_crop': 'Auto-crop output',
        
        # Language
        'language': '🌐 Language',
        
        # Dialogs
        'select_image': 'Select Image',
        'image_files': 'Image Files',
        'save_png_dialog': 'Save PNG',
        'png_image': 'PNG Image',
        'success': 'Success',
        'error': 'Error',
        'image_saved': 'Image saved to:',
        'failed_save': 'Failed to save image:',
        'failed_process': 'Failed to process:',
        'processing_failed': 'Error - Processing failed',
        'done': 'Done!',
        
        # Export mask
        'export_mask_format': 'Export Mask Format',
        'select_mask_format': 'Select mask format:',
        'grayscale': 'Grayscale (0-255)',
        'binary': 'Binary (Black/White)',
        'alpha_channel': 'Alpha Channel',
        'ok': 'OK',
        'cancel': 'Cancel',
        'save_mask': 'Save Mask',
        'mask_exported': 'Mask Exported',
        'mask_exported_success': 'Mask exported successfully!',
        'format': 'Format',
        'file': 'File',
        'export_error': 'Export Error',
        'failed_export_mask': 'Failed to export mask:',
        
        # Batch processing
        'select_input_folder': 'Select Input Folder',
        'select_output_folder': 'Select Output Folder',
        'no_images': 'No Images',
        'no_images_found': 'No image files found in selected folder.',
        'batch_process': 'Batch Process',
        'process_images': 'Process {count} images?',
        'output': 'Output',
        'yes': 'Yes',
        'no': 'No',
        'batch_processing': 'Batch Processing',
        'processing_images': 'Processing images...',
        'processing': 'Processing',
        'completed': 'Completed',
        'failed': 'Failed',
        'progress': 'Progress',
        'eta': 'ETA',
        'batch_complete': 'Batch Complete',
        'batch_complete_msg': 'Batch processing complete!',
        'total': 'Total',
        'successful': 'Successful',
        'success_rate': 'Success rate',
        'total_time': 'Total time',
        'output_folder': 'Output folder',
        'batch_error': 'Batch Error',
        'batch_failed': 'Batch processing failed:',
    },
    
    'vi': {
        # Window
        'window_title': 'RemoveBG - Xóa Phông Nền AI',
        'status_ready': 'Sẵn sàng - Kéo thả ảnh để bắt đầu',
        
        # Input section
        'input_image': '🖼️ ẢNH ĐẦU VÀO',
        'drag_drop_text': 'Kéo Thả Ảnh Vào Đây\nhoặc Nhấn để Chọn File',
        'loaded': 'Đã tải',
        'change_image': 'Đổi Ảnh',
        
        # Process button
        'remove_background': '🎯 XÓA PHÔNG NỀN',
        'processing': '⏳ Đang xử lý...',
        
        # Save & Export
        'save_export': '💾 LƯU & XUẤT',
        'save_png': '💾 Lưu PNG',
        'save_png_tooltip': 'Lưu dạng PNG trong suốt',
        'mask': '📄 Mask',
        'mask_tooltip': 'Xuất mask theo định dạng khác',
        'batch': '📂 Hàng loạt...',
        'batch_tooltip': 'Xử lý nhiều ảnh cùng lúc',
        
        # Reset
        'reset': '🔄 Làm mới',
        
        # Output section
        'output_preview': '✨ KẾT QUẢ',
        'no_image_loaded': 'Chưa tải ảnh',
        'fit': 'Vừa khung',
        'zoom_in': 'Phóng to',
        'zoom_out': 'Thu nhỏ',
        'checkerboard': 'Ô cờ',
        
        # Processing info
        'processing_info': '📊 THÔNG TIN XỬ LÝ',
        'no_image_processed': 'Chưa xử lý ảnh nào',
        'processing_complete': '✓ Xử lý hoàn tất!',
        'time': 'Thời gian',
        'input': 'Đầu vào',
        'size': 'Kích thước',
        
        # Adjustments
        'fine_tune': '🎨 TINH CHỈNH',
        'threshold': 'Ngưỡng:',
        'smooth': 'Làm mịn:',
        'feather': 'Làm mờ:',
        
        # Background color
        'bg_color_preview': '🎨 XEM MÀU PHÔNG NỀN',
        'preview_with': 'Xem với:',
        'pick_color': 'Chọn màu',
        'clear': 'Xóa',
        
        # Options
        'options': '⚙️ TÙY CHỌN',
        'auto_crop': 'Tự động cắt ảnh',
        
        # Language
        'language': '🌐 Ngôn ngữ',
        
        # Dialogs
        'select_image': 'Chọn Ảnh',
        'image_files': 'File Ảnh',
        'save_png_dialog': 'Lưu PNG',
        'png_image': 'Ảnh PNG',
        'success': 'Thành công',
        'error': 'Lỗi',
        'image_saved': 'Đã lưu ảnh tại:',
        'failed_save': 'Lưu ảnh thất bại:',
        'failed_process': 'Xử lý thất bại:',
        'processing_failed': 'Lỗi - Xử lý thất bại',
        'done': 'Hoàn tất!',
        
        # Export mask
        'export_mask_format': 'Định Dạng Xuất Mask',
        'select_mask_format': 'Chọn định dạng mask:',
        'grayscale': 'Thang xám (0-255)',
        'binary': 'Nhị phân (Đen/Trắng)',
        'alpha_channel': 'Kênh Alpha',
        'ok': 'OK',
        'cancel': 'Hủy',
        'save_mask': 'Lưu Mask',
        'mask_exported': 'Đã Xuất Mask',
        'mask_exported_success': 'Xuất mask thành công!',
        'format': 'Định dạng',
        'file': 'File',
        'export_error': 'Lỗi Xuất',
        'failed_export_mask': 'Xuất mask thất bại:',
        
        # Batch processing
        'select_input_folder': 'Chọn Thư Mục Đầu Vào',
        'select_output_folder': 'Chọn Thư Mục Đầu Ra',
        'no_images': 'Không Có Ảnh',
        'no_images_found': 'Không tìm thấy file ảnh trong thư mục.',
        'batch_process': 'Xử Lý Hàng Loạt',
        'process_images': 'Xử lý {count} ảnh?',
        'output': 'Đầu ra',
        'yes': 'Có',
        'no': 'Không',
        'batch_processing': 'Xử Lý Hàng Loạt',
        'processing_images': 'Đang xử lý ảnh...',
        'processing': 'Đang xử lý',
        'completed': 'Hoàn thành',
        'failed': 'Thất bại',
        'progress': 'Tiến trình',
        'eta': 'Còn lại',
        'batch_complete': 'Hoàn Tất',
        'batch_complete_msg': 'Xử lý hàng loạt hoàn tất!',
        'total': 'Tổng',
        'successful': 'Thành công',
        'success_rate': 'Tỷ lệ thành công',
        'total_time': 'Tổng thời gian',
        'output_folder': 'Thư mục đầu ra',
        'batch_error': 'Lỗi Hàng Loạt',
        'batch_failed': 'Xử lý hàng loạt thất bại:',
    }
}


class Translator:
    """Simple translator class."""
    
    def __init__(self, language: str = 'en'):
        """Initialize translator."""
        self.current_language = language
    
    def set_language(self, language: str):
        """Set current language."""
        if language in TRANSLATIONS:
            self.current_language = language
    
    def get(self, key: str, **kwargs) -> str:
        """Get translated text."""
        text = TRANSLATIONS.get(self.current_language, {}).get(key, key)
        # Support for string formatting
        if kwargs:
            text = text.format(**kwargs)
        return text
    
    def t(self, key: str, **kwargs) -> str:
        """Shorthand for get()."""
        return self.get(key, **kwargs)
