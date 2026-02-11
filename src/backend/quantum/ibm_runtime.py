"""IBM Quantum Runtime service access and backend discovery."""

from __future__ import annotations

from dataclasses import dataclass

from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime.exceptions import IBMNotAuthorizedError, IBMRuntimeError

from backend.config import get_settings


class IBMRuntimeConfigurationError(ValueError):
    """Raised when required IBM Runtime configuration is missing or invalid."""


class IBMRuntimeAuthenticationError(PermissionError):
    """Raised when IBM Runtime authentication fails."""


class IBMRuntimeConnectionError(ConnectionError):
    """Raised when IBM Runtime backends cannot be fetched due to connectivity issues."""


@dataclass(frozen=True)
class IBMBackendInfo:
    """Normalized backend information independent from API schemas."""

    name: str
    num_qubits: int
    coupling_map: list[list[int]]
    basis_gates: list[str]
    is_operational: bool
    pending_jobs: int


def get_runtime_service() -> QiskitRuntimeService:
    """Create IBM Quantum runtime service from environment-backed settings."""

    settings = get_settings()

    if not settings.ibm_quantum_api_token:
        raise IBMRuntimeConfigurationError("IBM_QUANTUM_API_TOKEN is not set.")

    try:
        service_kwargs = {
            "channel": settings.ibm_quantum_channel,
            "token": settings.ibm_quantum_api_token,
        }
        if settings.ibm_quantum_instance:
            service_kwargs["instance"] = settings.ibm_quantum_instance

        return QiskitRuntimeService(**service_kwargs)
    except IBMNotAuthorizedError as exc:
        raise IBMRuntimeAuthenticationError("IBM Quantum authentication failed.") from exc
    except IBMRuntimeError as exc:
        raise IBMRuntimeConnectionError("Failed to initialize IBM Quantum Runtime service.") from exc


def _normalize_backend_info(backend: object) -> IBMBackendInfo:
    """Convert backend object to normalized DTO."""

    coupling_map = []
    if getattr(backend, "coupling_map", None) and getattr(backend.coupling_map, "get_edges", None):
        coupling_map = [list(edge) for edge in backend.coupling_map.get_edges()]

    basis_gates = list(getattr(backend, "operation_names", []))

    status = backend.status()

    return IBMBackendInfo(
        name=str(backend.name),
        num_qubits=int(getattr(backend, "num_qubits", 0)),
        coupling_map=coupling_map,
        basis_gates=basis_gates,
        is_operational=bool(getattr(status, "operational", False)),
        pending_jobs=int(getattr(status, "pending_jobs", 0)),
    )


def list_real_backends() -> list[IBMBackendInfo]:
    """List operational non-simulator IBM backends as normalized DTOs."""

    service = get_runtime_service()
    try:
        backends = service.backends(simulator=False, operational=True)
        return [_normalize_backend_info(backend) for backend in backends]
    except IBMNotAuthorizedError as exc:
        raise IBMRuntimeAuthenticationError("IBM Quantum authentication failed while listing backends.") from exc
    except IBMRuntimeError as exc:
        raise IBMRuntimeConnectionError("Failed to list IBM Quantum backends.") from exc
