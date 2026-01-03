"""JSON to OpenQASM 2.0 converter"""

from backend.model.circuit import Gate


def json_to_qasm(qubits: int, gates: list[Gate]) -> str:
    """
    Convert circuit JSON to OpenQASM 2.0 format.

    Args:
        qubits: Number of qubits in the circuit
        gates: List of Gate objects

    Returns:
        OpenQASM 2.0 code as string

    Example:
        >>> gates = [Gate(type="H", qubit=0, position=0)]
        >>> qasm = json_to_qasm(qubits=2, gates=gates)
        >>> print(qasm)
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[2];
        creg c[2];
        h q[0];
        measure q -> c;
    """
    qasm_lines = [
        "OPENQASM 2.0;",
        'include "qelib1.inc";',
        f"qreg q[{qubits}];",
        f"creg c[{qubits}];",
    ]

    # Sort gates by position to ensure correct execution order
    sorted_gates = sorted(gates, key=lambda g: g.position)

    for gate in sorted_gates:
        qasm_line = _gate_to_qasm(gate)
        if qasm_line:
            qasm_lines.append(qasm_line)

    # Add measurements at the end
    qasm_lines.append("measure q -> c;")

    return "\n".join(qasm_lines)


def _gate_to_qasm(gate: Gate) -> str:
    """
    Convert a single gate to its OpenQASM representation.

    Args:
        gate: Gate object

    Returns:
        OpenQASM gate instruction
    """
    gate_type = gate.type

    # Single-qubit Pauli gates
    if gate_type == "H":
        return f"h q[{gate.qubit}];"
    elif gate_type == "X":
        return f"x q[{gate.qubit}];"
    elif gate_type == "Y":
        return f"y q[{gate.qubit}];"
    elif gate_type == "Z":
        return f"z q[{gate.qubit}];"

    # Rotation gates (parameterized)
    elif gate_type == "RX":
        angle = gate.parameter if gate.parameter is not None else 0.785398163  # π/4
        return f"rx({angle}) q[{gate.qubit}];"
    elif gate_type == "RY":
        angle = gate.parameter if gate.parameter is not None else 0.785398163  # π/4
        return f"ry({angle}) q[{gate.qubit}];"
    elif gate_type == "RZ":
        angle = gate.parameter if gate.parameter is not None else 0.785398163  # π/4
        return f"rz({angle}) q[{gate.qubit}];"

    # Two-qubit gates
    elif gate_type == "CNOT":
        return f"cx q[{gate.control}],q[{gate.target}];"

    return ""
