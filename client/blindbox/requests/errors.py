class AttestationException(Exception):
    """
    A custom exception class for wrapping attestation errors.
    """

    def __init__(self, code):
        self.code = code

    def __str__(self):
        return f"{self.code}"

class NotAnEnclaveError(AttestationException):
    """
    This exception is raised when the attestation report
    is not generated from an enclave.
    """
    pass

class InvalidEnclaveCode(AttestationException):
    """
    This exception is raised when the cce policy
    in the report does not match the expected policy.
    """
    pass

class NonCompliantUvm(AttestationException):
    """
    This exception is raised when the underlying virtual
    machine is not Azure compliant.
    """
    pass

class FalseAttestationReport(AttestationException):
    """
    This exception is raised when the expected nonce does not match
    the nonce returned in the attestation report.
    """
    pass

class DebugMode(AttestationException):
    """
    This exception is raised when the enclave is running in debug mode.
    """
    pass

class WrongAttester(AttestationException):
    """
    This exception is raised if the attestation token is generated
    by a different attestation endpoint than the one expected.
    """
    pass

class MAATokenNotFound(AttestationException):
    """
    This exception is raised if the attestation service
    is unable to find an MAA token.
    """
    pass
