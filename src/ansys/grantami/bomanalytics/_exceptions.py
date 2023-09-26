"""BoM Analytics exceptions."""


class GrantaMIException(RuntimeError):
    """Provides the critical error message to show if processing a BoM Analytics query fails."""

    pass


class LicensingException(Exception):
    """Raised when an operation cannot be performed due to a lack of appropriate license."""

    pass
