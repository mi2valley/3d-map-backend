# qamposer-backend API Interface

API interface specification for qamposer-backend used by qamposer-scanner.

## Overview

### Base URL

| Environment | URL                     |
| ----------- | ----------------------- |
| Development | `http://localhost:8080` |
| Production  | TBD                     |

### Common Headers

```
Content-Type: application/json
```

## API Endpoints

### POST /api/circuit/simulate

Simulate a quantum circuit and return measurement results.

#### Request

```typescript
interface CircuitRequest {
  qubits: number; // Number of qubits (1-5)
  gates: Gate[]; // List of gates (max 20)
  shots: number; // Number of shots (100-10000, default: 1024)
  profile: SimulationProfile; // Simulation settings
}

interface Gate {
  type: string; // Gate type
  qubit?: number; // Target qubit for single-qubit gates (0-indexed)
  control?: number; // Control qubit for CNOT (0-indexed)
  target?: number; // Target qubit for CNOT (0-indexed)
  parameter?: number; // Rotation angle in radians
  position: number; // Position in circuit (column index, 0-indexed)
}

interface SimulationProfile {
  type: "ideal" | "noisy_fake"; // Backend type
  backend_name?: string; // Backend name (required for noisy_fake)
  seed?: number; // Random seed for reproducibility
}
```

#### Supported Gate Types

| type   | Description          | Required Fields                           |
| ------ | -------------------- | ----------------------------------------- |
| `H`    | Hadamard gate        | qubit, position                           |
| `X`    | Pauli-X gate         | qubit, position                           |
| `Y`    | Pauli-Y gate         | qubit, position                           |
| `Z`    | Pauli-Z gate         | qubit, position                           |
| `CNOT` | Controlled-NOT gate  | control, target, position                 |
| `RX`   | X-axis rotation gate | qubit, position, parameter (default: π/4) |
| `RY`   | Y-axis rotation gate | qubit, position, parameter (default: π/4) |
| `RZ`   | Z-axis rotation gate | qubit, position, parameter (default: π/4) |

#### Request Example

```json
{
  "qubits": 2,
  "gates": [
    {
      "type": "H",
      "qubit": 0,
      "position": 0
    },
    {
      "type": "CNOT",
      "control": 0,
      "target": 1,
      "position": 1
    }
  ],
  "shots": 1024,
  "profile": {
    "type": "ideal"
  }
}
```

#### Response (Success: 200 OK)

```typescript
interface SimulationResult {
  counts: Record<string, number>; // Measurement counts
  execution_time: number; // Execution time in seconds
  qsphere?: QSpherePoint[]; // Q-sphere coordinates (optional)
}

interface QSpherePoint {
  state: string; // Basis state (e.g., "00", "01")
  x: number; // X coordinate (-1 to 1)
  y: number; // Y coordinate (-1 to 1)
  z: number; // Z coordinate (-1 to 1)
  probability: number; // Probability (0 to 1)
  phase: number; // Phase in radians (-π to π)
}
```

#### Response Example

```json
{
  "counts": {
    "00": 512,
    "11": 512
  },
  "execution_time": 0.125,
  "qsphere": [
    {
      "state": "00",
      "x": 0.0,
      "y": 0.0,
      "z": 1.0,
      "probability": 0.5,
      "phase": 0.0
    },
    {
      "state": "11",
      "x": 0.0,
      "y": 0.0,
      "z": -1.0,
      "probability": 0.5,
      "phase": 0.0
    }
  ]
}
```

#### Error Responses

**400 Bad Request (Validation Error)**

```json
{
  "detail": "Invalid gate type: SWAP. Must be one of ['H', 'X', 'Y', 'Z', 'CNOT', 'RX', 'RY', 'RZ']",
  "error_code": "VALIDATION_ERROR"
}
```

**500 Internal Server Error (Simulation Error)**

```json
{
  "detail": "Simulation failed: circuit too complex",
  "error_code": "SIMULATION_ERROR"
}
```

---

### GET /api/circuit/gates

Get the list of supported gates.

#### Response (200 OK)

```json
{
  "single_qubit": ["H", "X", "Y", "Z"],
  "rotation": ["RX", "RY", "RZ"],
  "two_qubit": ["CNOT"]
}
```

---

### GET /api/circuit/backends

Get the list of available backends.

#### Response (200 OK)

```typescript
interface BackendInfo {
  id: string; // Backend identifier
  name: string; // Display name
  num_qubits: number; // Number of supported qubits
  backend_type: "ideal" | "noisy_fake"; // Type
  description?: string; // Description
}
```

#### Response Example

```json
[
  {
    "id": "ideal",
    "name": "Ideal Simulator",
    "num_qubits": 32,
    "backend_type": "ideal",
    "description": "Noiseless statevector simulator"
  },
  {
    "id": "fake_manila",
    "name": "Fake Manila",
    "num_qubits": 5,
    "backend_type": "noisy_fake",
    "description": "Noisy simulator based on IBM Manila"
  }
]
```

---

### GET /health

Health check endpoint.

#### Response (200 OK)

```json
{
  "status": "ok"
}
```

---

### GET /version

Version information.

#### Response (200 OK)

```json
{
  "version": "1.0.0"
}
```

---

## CORS Configuration

qamposer-backend allows requests from the following origins:

```python
# Development environment
origins = [
    "http://localhost:3000",
    "http://localhost:4321",
    "http://localhost:5173",  # Vite default
]
```

Appropriate origins must be configured for production environment.

---

## Constraints

| Item             | Constraint                           |
| ---------------- | ------------------------------------ |
| Number of qubits | 1-5                                  |
| Number of gates  | Max 20                               |
| Number of shots  | 100-10,000                           |
| Rotation angle   | Radians (default: π/4 ≈ 0.785398163) |

---

_Last updated: 2026-01-22_
