"""Domain exceptions."""


class DomainError(Exception):
    """Base domain error."""
    pass


class ModelNotFoundError(DomainError):
    """ONNX model file not found."""
    pass


class InvalidImageError(DomainError):
    """Invalid or corrupted image file."""
    pass


class InferenceFailedError(DomainError):
    """ONNX inference failed."""
    pass


class InvalidSettingsError(DomainError):
    """Invalid settings configuration."""
    pass
