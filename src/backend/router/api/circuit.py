"""Quantum circuit API endpoints"""

import logging

from fastapi import APIRouter, HTTPException, status

from backend.model.circuit import CircuitRequest, ErrorResponse, SimulationResult
from backend.quantum.converter import json_to_qasm
from backend.quantum.simulator import SimulationError, simulate_qasm

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/circuit", tags=["circuit"])


@router.post(
    "/simulate",
    response_model=SimulationResult,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid circuit request"},
        500: {"model": ErrorResponse, "description": "Simulation error"},
    },
    summary="Simulate quantum circuit",
    description="""
    Simulate a quantum circuit via the JSON → OpenQASM → Qiskit pipeline.

    **Pipeline:**
    1. Validate circuit request (gates, qubits, shots)
    2. Convert JSON to OpenQASM 2.0
    3. Simulate with Qiskit AerSimulator
    4. Return measurement counts and execution time

    **Supported Gates:**
    - Single-qubit: H, X, Y, Z
    - Rotation: RX, RY, RZ (with optional angle parameter)
    - Two-qubit: CNOT

    **Constraints:**
    - Qubits: 2-5
    - Gates: max 20 per circuit
    - Shots: 100-10,000
    """,
)
async def simulate(request: CircuitRequest) -> SimulationResult:
    """
    Simulate a quantum circuit and return measurement results.

    Args:
        request: Circuit specification with qubits, gates, and shots

    Returns:
        Simulation results with counts and execution time

    Raises:
        HTTPException: If validation or simulation fails
    """
    try:
        logger.info(f"Simulating circuit: {request.qubits} qubits, {len(request.gates)} gates, {request.shots} shots")

        # Convert JSON to OpenQASM
        qasm_code = json_to_qasm(qubits=request.qubits, gates=request.gates)

        logger.debug(f"Generated QASM:\n{qasm_code}")

        # Simulate circuit
        result = simulate_qasm(qasm_code=qasm_code, shots=request.shots)

        logger.info(
            f"Simulation completed in {result['execution_time']:.3f}s, got {len(result['counts'])} unique outcomes"
        )

        return SimulationResult(counts=result["counts"], execution_time=result["execution_time"])

    except ValueError as e:
        # Validation errors from Pydantic or our validators
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": str(e), "error_code": "VALIDATION_ERROR"},
        ) from e

    except SimulationError as e:
        # Errors from Qiskit simulation
        logger.error(f"Simulation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"detail": str(e), "error_code": "SIMULATION_ERROR"},
        ) from e

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"},
        ) from e


@router.get(
    "/gates",
    response_model=dict[str, list[str]],
    summary="List supported gates",
    description="Get a list of all supported quantum gates organized by category",
)
async def list_gates() -> dict[str, list[str]]:
    """
    List all supported quantum gates by category.

    Returns:
        Dictionary mapping category names to lists of gate types
    """
    return {
        "single_qubit": ["H", "X", "Y", "Z"],
        "rotation": ["RX", "RY", "RZ"],
        "two_qubit": ["CNOT"],
    }
