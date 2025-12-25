"""Utility to compute Q-sphere coordinates from a statevector."""

from __future__ import annotations

from typing import Dict, List

import numpy as np
from qiskit.quantum_info import Statevector

from backend.model.circuit import QSpherePoint


def _bitstring(index: int, num_qubits: int) -> str:
    return format(index, f"0{num_qubits}b")


def _theta_for_weight(weight: int, num_qubits: int) -> float:
    """
    Map Hamming weight to polar angle on the sphere.

    0 ones -> north pole (θ = 0), all ones -> south pole (θ = π).
    """
    if num_qubits <= 1:
        return 0.0 if weight == 0 else np.pi
    return np.pi * weight / num_qubits


def compute_qsphere_points(state: Statevector, max_qubits: int = 5) -> list[QSpherePoint]:
    """
    Compute Q-sphere coordinates from a statevector.

    Args:
        state: Final statevector of the circuit (without measurements).
        max_qubits: Return an empty list if the circuit exceeds this many qubits.

    Returns:
        List of QSpherePoint entries (probabilities normalized).
    """
    num_qubits = state.num_qubits
    if num_qubits > max_qubits:
        return []

    amplitudes = np.asarray(state.data)
    dim = amplitudes.shape[0]
    points: List[QSpherePoint] = []

    # Group basis states by Hamming weight so we can spread them evenly around φ.
    by_weight: Dict[int, List[int]] = {}
    for idx in range(dim):
        bs = _bitstring(idx, num_qubits)
        weight = bs.count("1")
        by_weight.setdefault(weight, []).append(idx)

    for weight, indices in by_weight.items():
        if not indices:
            continue

        theta = _theta_for_weight(weight, num_qubits)
        count_in_ring = len(indices)

        for pos, idx in enumerate(indices):
            amplitude = amplitudes[idx]
            probability = float(np.real(amplitude * np.conj(amplitude)))
            if probability < 1e-12:
                # Skip numerically zero states to reduce clutter.
                continue

            phase = float(np.angle(amplitude))
            phi = 2.0 * np.pi * pos / count_in_ring

            x = float(np.sin(theta) * np.cos(phi))
            y = float(np.sin(theta) * np.sin(phi))
            z = float(np.cos(theta))

            points.append(
                QSpherePoint(
                    state=_bitstring(idx, num_qubits),
                    x=x,
                    y=y,
                    z=z,
                    probability=probability,
                    phase=phase,
                )
            )

    total_prob = sum(point.probability for point in points) or 1.0
    for point in points:
        point.probability = point.probability / total_prob

    return points
