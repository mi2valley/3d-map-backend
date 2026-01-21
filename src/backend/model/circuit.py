from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class BackendType(str, Enum):
    """Supported backend types"""

    IDEAL = "ideal"
    NOISY_FAKE = "noisy_fake"
    # QPU = "qpu"  # Reserved for future implementation


class SimulationProfile(BaseModel):
    """Simulation execution profile"""

    type: BackendType = Field(default=BackendType.IDEAL, description="Backend type")
    backend_name: Optional[str] = Field(None, description="Fake backend name (required for noisy_fake)")
    seed: Optional[int] = Field(None, ge=0, description="Random seed for reproducibility")

    @field_validator("backend_name")
    @classmethod
    def validate_backend_name(cls, v: Optional[str], info) -> Optional[str]:
        backend_type = info.data.get("type")
        if backend_type == BackendType.NOISY_FAKE and not v:
            raise ValueError("backend_name is required for noisy_fake type")
        return v


class BackendInfo(BaseModel):
    """Backend information for UI display"""

    id: str = Field(..., description="Backend identifier")
    name: str = Field(..., description="Display name")
    num_qubits: int = Field(..., ge=1, description="Number of qubits")
    backend_type: BackendType = Field(..., description="Backend type")
    description: Optional[str] = Field(None, description="Backend description")


class Gate(BaseModel):
    """Quantum gate definition"""

    type: str = Field(..., description="Gate type (H, X, Y, Z, CNOT, RX, RY, RZ)")
    qubit: Optional[int] = Field(None, description="Target qubit index for single-qubit gates", ge=0)
    control: Optional[int] = Field(None, description="Control qubit index for CNOT", ge=0)
    target: Optional[int] = Field(None, description="Target qubit index for CNOT", ge=0)
    parameter: Optional[float] = Field(None, description="Rotation angle in radians for rotation gates")
    position: int = Field(..., description="Time step position in circuit", ge=0)

    @field_validator("type")
    @classmethod
    def validate_gate_type(cls, v: str) -> str:
        valid_types = ["H", "X", "Y", "Z", "CNOT", "RX", "RY", "RZ"]
        if v not in valid_types:
            raise ValueError(f"Invalid gate type: {v}. Must be one of {valid_types}")
        return v

    @field_validator("parameter")
    @classmethod
    def validate_parameter(cls, v: Optional[float], info) -> Optional[float]:
        gate_type = info.data.get("type")
        if gate_type in ["RX", "RY", "RZ"] and v is None:
            # Default rotation angle for rotation gates
            return 0.785398163  # π/4
        return v


class CircuitRequest(BaseModel):
    """Request payload for circuit simulation"""

    qubits: int = Field(..., ge=1, le=5, description="Number of qubits (1-5)")
    gates: list[Gate] = Field(..., max_length=20, description="List of gates (max 20)")
    shots: int = Field(1024, ge=100, le=10000, description="Number of measurement shots")
    profile: SimulationProfile = Field(
        default_factory=SimulationProfile, description="Simulation profile (backend selection)"
    )

    @field_validator("gates")
    @classmethod
    def validate_gates(cls, v: list[Gate], info) -> list[Gate]:
        qubits = info.data.get("qubits", 0)

        for gate in v:
            # Validate qubit indices
            if gate.qubit is not None and gate.qubit >= qubits:
                raise ValueError(f"Gate qubit index {gate.qubit} exceeds number of qubits {qubits}")

            if gate.control is not None and gate.control >= qubits:
                raise ValueError(f"Gate control index {gate.control} exceeds number of qubits {qubits}")

            if gate.target is not None and gate.target >= qubits:
                raise ValueError(f"Gate target index {gate.target} exceeds number of qubits {qubits}")

            # Validate gate-specific constraints
            if gate.type == "CNOT":
                if gate.control is None or gate.target is None:
                    raise ValueError("CNOT gate requires both control and target qubits")
                if gate.control == gate.target:
                    raise ValueError("CNOT control and target must be different qubits")
            else:
                if gate.qubit is None:
                    raise ValueError(f"{gate.type} gate requires qubit field")

        return v


class QSpherePoint(BaseModel):
    """Q-sphere coordinate for a single basis state"""

    state: str = Field(..., description="Basis state string, e.g. '010'")
    x: float = Field(..., description="X coordinate on unit sphere")
    y: float = Field(..., description="Y coordinate on unit sphere")
    z: float = Field(..., description="Z coordinate on unit sphere")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability |amplitude|^2")
    phase: float = Field(..., description="Phase of amplitude in radians (-π..π)")


class SimulationResult(BaseModel):
    """Simulation result payload"""

    counts: dict[str, int] = Field(..., description="Measurement counts dictionary")
    execution_time: float = Field(..., description="Execution time in seconds", ge=0)
    qsphere: Optional[list[QSpherePoint]] = Field(
        None,
        description="Optional Q-sphere coordinates for visualizing the output state",
    )


class ErrorResponse(BaseModel):
    """Error response payload"""

    detail: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
