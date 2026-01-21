"""Backend registry for quantum circuit simulation"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from qiskit_ibm_runtime.fake_provider import (
    FakeGuadalupeV2,
    FakeKyoto,
    FakeManilaV2,
    FakePerth,
    FakeSherbrooke,
)

if TYPE_CHECKING:
    from qiskit.providers import BackendV2


@dataclass(frozen=True)
class BackendSpec:
    """Specification for a registered backend"""

    id: str
    name: str
    num_qubits: int
    description: str
    factory: type


# Registered fake backends (5+ qubits)
FAKE_BACKENDS: dict[str, BackendSpec] = {
    "fake_manila": BackendSpec(
        id="fake_manila",
        name="Fake Manila",
        num_qubits=5,
        description="5-qubit noisy simulator based on IBM Manila",
        factory=FakeManilaV2,
    ),
    "fake_perth": BackendSpec(
        id="fake_perth",
        name="Fake Perth",
        num_qubits=7,
        description="7-qubit noisy simulator based on IBM Perth",
        factory=FakePerth,
    ),
    "fake_guadalupe": BackendSpec(
        id="fake_guadalupe",
        name="Fake Guadalupe",
        num_qubits=16,
        description="16-qubit noisy simulator based on IBM Guadalupe",
        factory=FakeGuadalupeV2,
    ),
    "fake_kyoto": BackendSpec(
        id="fake_kyoto",
        name="Fake Kyoto",
        num_qubits=127,
        description="127-qubit noisy simulator based on IBM Kyoto",
        factory=FakeKyoto,
    ),
    "fake_sherbrooke": BackendSpec(
        id="fake_sherbrooke",
        name="Fake Sherbrooke",
        num_qubits=127,
        description="127-qubit noisy simulator based on IBM Sherbrooke",
        factory=FakeSherbrooke,
    ),
}


def get_fake_backend(backend_id: str) -> BackendV2:
    """
    Create and return a fake backend instance.

    Args:
        backend_id: The backend identifier

    Returns:
        Instantiated fake backend

    Raises:
        ValueError: If backend_id is not found
    """
    if backend_id not in FAKE_BACKENDS:
        available = ", ".join(FAKE_BACKENDS.keys())
        raise ValueError(f"Unknown backend: {backend_id}. Available: {available}")

    return FAKE_BACKENDS[backend_id].factory()


def list_available_backends() -> list[BackendSpec]:
    """Return all available backend specifications"""
    return list(FAKE_BACKENDS.values())
