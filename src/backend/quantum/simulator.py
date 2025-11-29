"""Quantum circuit simulation using Qiskit"""

from __future__ import annotations

import logging
import time
from typing import TypedDict

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

from backend.model.circuit import QSpherePoint
from backend.quantum.qsphere import compute_qsphere_points

logger = logging.getLogger(__name__)


class SimulationError(Exception):
    """Custom exception for simulation errors"""

    pass


class SimulationResultDict(TypedDict):
    """Type definition for simulation result dictionary"""

    counts: dict[str, int]
    execution_time: float
    qsphere: list[QSpherePoint] | None


def simulate_qasm(qasm_code: str, shots: int = 1024) -> SimulationResultDict:
    """
    Simulate a quantum circuit from OpenQASM code using Qiskit AerSimulator.

    Args:
        qasm_code: OpenQASM 2.0 code string
        shots: Number of measurement shots (default: 1024)

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
    start_time = time.time()

    try:
        # Parse OpenQASM code to Qiskit QuantumCircuit
        circuit = QuantumCircuit.from_qasm_str(qasm_code)

        # Initialize AerSimulator
        simulator = AerSimulator()

        # Run simulation
        job = simulator.run(circuit, shots=shots)
        result = job.result()

        # Get measurement counts and convert to standard dict
        counts = dict(result.get_counts())

        # Calculate execution time
        execution_time = time.time() - start_time

        # Compute Q-sphere coordinates from the final statevector (without measurements)
        qsphere: list[QSpherePoint] | None = None
        try:
            circuit_without_measure = circuit.remove_final_measurements(inplace=False)
            state = Statevector.from_instruction(circuit_without_measure)
            qsphere = compute_qsphere_points(state)
        except Exception as exc:
            logger.warning("Failed to compute Q-sphere points: %s", exc)

        return SimulationResultDict(counts=counts, execution_time=execution_time, qsphere=qsphere)

    except Exception as e:
        raise SimulationError(f"Simulation failed: {str(e)}") from e


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
