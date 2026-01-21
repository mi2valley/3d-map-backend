"""Quantum circuit simulation using Qiskit"""

from __future__ import annotations

import logging
import time
from typing import TypedDict

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

from backend.model.circuit import BackendType, QSpherePoint, SimulationProfile
from backend.quantum.backends import get_fake_backend
from backend.quantum.qsphere import compute_qsphere_points

# if TYPE_CHECKING:
#     from qiskit.providers import BackendV2

logger = logging.getLogger(__name__)


class SimulationError(Exception):
    """Custom exception for simulation errors"""

    pass


class SimulationResultDict(TypedDict):
    """Type definition for simulation result dictionary"""

    counts: dict[str, int]
    execution_time: float
    qsphere: list[QSpherePoint] | None


def simulate_qasm(
    qasm_code: str,
    shots: int = 1024,
    profile: SimulationProfile | None = None,
) -> SimulationResultDict:
    """
    Simulate a quantum circuit from OpenQASM code.

    Args:
        qasm_code: OpenQASM 2.0 code string
        shots: Number of measurement shots (default: 1024)
        profile: Simulation profile specifying backend type

    Returns:
        SimulationResultDict containing:
            - counts: Measurement outcome counts (dict[str, int])
            - execution_time: Simulation execution time in seconds (float)
            - qsphere: Optional Q-sphere points for visualization

    Raises:
        SimulationError: If circuit parsing or simulation fails

    Example:
        >>> qasm = '''
        ... OPENQASM 2.0;
        ... include "qelib1.inc";
        ... qreg q[2];
        ... creg c[2];
        ... h q[0];
        ... cx q[0],q[1];
        ... measure q -> c;
        ... '''
        >>> result = simulate_qasm(qasm, shots=1024)
        >>> print(result['counts'])
        {'00': 512, '11': 512}
    """
    if profile is None:
        profile = SimulationProfile()

    start_time = time.time()

    try:
        circuit = QuantumCircuit.from_qasm_str(qasm_code)

        if profile.type == BackendType.NOISY_FAKE:
            counts = _run_noisy_simulation(circuit, shots, profile)
        else:
            counts = _run_ideal_simulation(circuit, shots, profile.seed)

        execution_time = time.time() - start_time

        # Compute Q-sphere (always from ideal statevector for consistent visualization)
        qsphere = _compute_qsphere(circuit)

        return SimulationResultDict(counts=counts, execution_time=execution_time, qsphere=qsphere)

    except SimulationError:
        raise
    except Exception as e:
        raise SimulationError(f"Simulation failed: {str(e)}") from e


def _run_ideal_simulation(circuit: QuantumCircuit, shots: int, seed: int | None = None) -> dict[str, int]:
    """Run ideal (noiseless) simulation"""
    simulator = AerSimulator()
    job = simulator.run(circuit, shots=shots, seed_simulator=seed)
    return dict(job.result().get_counts())


def _run_noisy_simulation(circuit: QuantumCircuit, shots: int, profile: SimulationProfile) -> dict[str, int]:
    """
    Run noisy simulation using a fake backend.

    The fake backend provides realistic noise models derived from actual
    IBM Quantum hardware calibration data.
    """
    if not profile.backend_name:
        raise SimulationError("backend_name is required for noisy simulation")

    fake_backend = get_fake_backend(profile.backend_name)

    # Transpile circuit to match backend's basis gates and coupling map
    transpiled = transpile(circuit, backend=fake_backend, optimization_level=1)

    logger.info(
        f"Transpiled circuit for {profile.backend_name}: "
        f"{circuit.num_qubits} qubits, depth {circuit.depth()} -> {transpiled.depth()}"
    )

    # Run on fake backend (uses AerSimulator with backend's noise model)
    job = fake_backend.run(transpiled, shots=shots, seed_simulator=profile.seed)
    return dict(job.result().get_counts())


def _compute_qsphere(circuit: QuantumCircuit) -> list[QSpherePoint] | None:
    """Compute Q-sphere coordinates from ideal statevector"""
    try:
        circuit_without_measure = circuit.remove_final_measurements(inplace=False)
        state = Statevector.from_instruction(circuit_without_measure)
        return compute_qsphere_points(state)
    except Exception as exc:
        logger.warning("Failed to compute Q-sphere points: %s", exc)
        return None


def simulate_circuit(qubits: int, gates: list, shots: int = 1024) -> SimulationResultDict:
    """
    Simulate a quantum circuit directly from gate list.

    This is a convenience function that builds the circuit programmatically
    instead of using QASM. Useful for simple circuits.

    Args:
        qubits: Number of qubits
        gates: List of gate dictionaries
        shots: Number of measurement shots

    Returns:
        SimulationResultDict with counts and execution_time

    Note:
        For production use, prefer the json_to_qasm -> simulate_qasm pipeline
        as it provides better validation and extensibility.
    """
    from backend.model.circuit import Gate
    from backend.quantum.converter import json_to_qasm

    # Convert gate dicts to Gate objects if needed
    gate_objects = []
    for gate in gates:
        if isinstance(gate, dict):
            gate_objects.append(Gate(**gate))
        else:
            gate_objects.append(gate)

    # Use the QASM pipeline
    qasm_code = json_to_qasm(qubits, gate_objects)
    return simulate_qasm(qasm_code, shots)
