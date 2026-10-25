"""Standard error types for WLAN Observatory."""


class ObservatoryError(Exception):
    """Base application exception."""


class DatasetError(ObservatoryError):
    """Raised when dataset files or structures violate expected schemas."""


class ValidationError(ObservatoryError):
    """Raised when validation criteria fail."""


class SimulationError(ObservatoryError):
    """Raised when simulation parameters or execution encounter an unrecoverable state."""


class ProvenanceError(ObservatoryError):
    """Raised when an unverified metric or invalid provenance tag is accessed."""
