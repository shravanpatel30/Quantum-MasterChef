import numpy as np

from qiskit.quantum_info import Statevector
from qiskit_aer import Aer
from qiskit.circuit import QuantumCircuit, CircuitInstruction
from qiskit.circuit import Reset
from qiskit.circuit.library import standard_gates
from qiskit.circuit.exceptions import CircuitError

'''
This is the list of statevectors in a dictionary format {"1" : [initial statevector, final statevector, hints]} for easy mode,
feel free to change this to teach or practice on how to read qspheres and how to think about quantum state vectors
'''

statevector_easy = {
    1: [
        Statevector.from_label("11"),
        Statevector([1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j], dims=(2, 2)),
        "You just have to flip the state of both qubits",
    ],
    2: [
        Statevector.from_label("00"),
        Statevector(
            [0.70710678 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.70710678 + 0.0j], dims=(2, 2)
        ),
        "This state is also referred as Φ+. Use H and CX gates",
    ],
    3: [
        Statevector.from_label("00"),
        Statevector(
            [
                0.70710678 - 8.65956056e-17j,
                0.0 + 0.00e00j,
                0.0 + 0.00e00j,
                -0.70710678 + 8.65956056e-17j,
            ],
            dims=(2, 2),
        ),
        "This state is also referred as Φ-. Same as first Bell state but with a negative phase",
    ],
    4: [
        Statevector.from_label("00"),
        Statevector(
            [0.0 + 0.0j, 0.70710678 + 0.0j, 0.70710678 + 0.0j, 0.0 + 0.0j], dims=(2, 2)
        ),
        "This state is also referred as Ψ+. Use H, CX and X gates",
    ],
    5: [
        Statevector.from_label("00"),
        Statevector(
            [0.0 + 0.0j, 0.70710678 - 0.0j, -0.70710678 + 0.0j, -0.0 + 0.0j],
            dims=(2, 2),
        ),
        "This state is also referred as Ψ-. This state just has a phase compared to Ψ+",
    ],
    6: [
        Statevector.from_label("11"),
        Statevector(
            [
                0.0 + 0.00e00j,
                -0.70710678 + 8.65956056e-17j,
                0.70710678 - 8.65956056e-17j,
                0.0 + 0.00e00j,
            ],
            dims=(2, 2),
        ),
        "Make sure you have initialized your quantum circuit to the given state. Think in terms of Bell states",
    ],
    7: [
        Statevector.from_label("10"),
        Statevector(
            [0.70710678 + 0.0j, 0.0 - 0.0j, -0.0 + 0.0j, -0.70710678 + 0.0j],
            dims=(2, 2),
        ),
        "Make sure you have initialized your quantum circuit to the given state. Think in terms of Bell states",
    ],
    8: [
        Statevector.from_label("01"),
        Statevector(
            [
                0.00e00 - 0.0j,
                8.65956056e-17 + 0.70710678j,
                -8.65956056e-17 - 0.70710678j,
                0.00e00 - 0.0j,
            ],
            dims=(2, 2),
        ),
        "Make sure you have initialized your quantum circuit to the given state.Think about how you will introduce a phase",
    ],
    9: [
        Statevector.from_label("000"),
        Statevector(
            [
                0.70710678 + 0.0j,
                0.0 + 0.0j,
                0.0 + 0.0j,
                0.0 + 0.0j,
                0.0 + 0.0j,
                0.0 + 0.0j,
                0.0 + 0.0j,
                0.70710678 + 0.0j,
            ],
            dims=(2, 2, 2),
        ),
        "This state is commonly named as GHZ state.You will need an extra cx gate compared to Bell states",
    ],
    10: [
        Statevector.from_label("10r"),
        Statevector(
            [
                0.0 + 0.0j,
                0.0 + 0.0j,
                0.0 + 0.0j,
                0.5 - 0.5j,
                0.5 + 0.5j,
                0.0 + 0.0j,
                0.0 + 0.0j,
                0.0 + 0.0j,
            ],
            dims=(2, 2, 2),
        ),
        "This state is related to GHZ state. Try to think how you will get the phases",
    ],
}

"""Custom utility function for generating random circuits."""


def random_circuit(
    num_qubits, depth, max_operands=2, seed=None, initial_state: Statevector = None
):
    if num_qubits == 0:
        return QuantumCircuit()
    if max_operands < 1 or max_operands > 4:
        raise CircuitError("max_operands must be between 1 and 4")
    max_operands = max_operands if num_qubits > max_operands else num_qubits

    gates_1q = [
        # (Gate class, number of qubits, number of parameters)
        (standard_gates.IGate, 1, 0),
        (standard_gates.SXGate, 1, 0),
        (standard_gates.XGate, 1, 0),
        (standard_gates.RZGate, 1, 1),
        (standard_gates.RGate, 1, 2),
        (standard_gates.HGate, 1, 0),
        (standard_gates.PhaseGate, 1, 1),
        (standard_gates.RXGate, 1, 1),
        (standard_gates.RYGate, 1, 1),
        (standard_gates.SGate, 1, 0),
        (standard_gates.SdgGate, 1, 0),
        (standard_gates.SXdgGate, 1, 0),
        (standard_gates.TGate, 1, 0),
        (standard_gates.TdgGate, 1, 0),
        (standard_gates.UGate, 1, 3),
        (standard_gates.U1Gate, 1, 1),
        (standard_gates.U2Gate, 1, 2),
        (standard_gates.U3Gate, 1, 3),
        (standard_gates.YGate, 1, 0),
        (standard_gates.ZGate, 1, 0),
    ]
    gates_2q = [
        (standard_gates.CXGate, 2, 0),
        (standard_gates.DCXGate, 2, 0),
        (standard_gates.CHGate, 2, 0),
        (standard_gates.CPhaseGate, 2, 1),
        (standard_gates.CRXGate, 2, 1),
        (standard_gates.CRYGate, 2, 1),
        (standard_gates.CRZGate, 2, 1),
        (standard_gates.CSXGate, 2, 0),
        (standard_gates.CUGate, 2, 4),
        (standard_gates.CU1Gate, 2, 1),
        (standard_gates.CU3Gate, 2, 3),
        (standard_gates.CYGate, 2, 0),
        (standard_gates.CZGate, 2, 0),
        (standard_gates.RXXGate, 2, 1),
        (standard_gates.RYYGate, 2, 1),
        (standard_gates.RZZGate, 2, 1),
        (standard_gates.RZXGate, 2, 1),
        (standard_gates.CSGate, 2, 0),
        (standard_gates.CSdgGate, 2, 0),
        (standard_gates.SwapGate, 2, 0),
        (standard_gates.iSwapGate, 2, 0),
    ]
    gates_3q = [
        (standard_gates.CCXGate, 3, 0),
        (standard_gates.CSwapGate, 3, 0),
        (standard_gates.CCZGate, 3, 0),
        (standard_gates.RCCXGate, 3, 0),
    ]
    gates_4q = [
        (standard_gates.C3SXGate, 4, 0),
        (standard_gates.RC3XGate, 4, 0),
    ]

    gates = gates_1q.copy()
    if max_operands >= 2:
        gates.extend(gates_2q)
    if max_operands >= 3:
        gates.extend(gates_3q)
    if max_operands >= 4:
        gates.extend(gates_4q)
    gates = np.array(
        gates,
        dtype=[("class", object), ("num_qubits", np.int64), ("num_params", np.int64)],
    )
    gates_1q = np.array(gates_1q, dtype=gates.dtype)

    qc = QuantumCircuit(num_qubits)

    if initial_state is None:
        qc.initialize(Statevector.from_label("0" * num_qubits))
    else:
        qc.initialize(initial_state)

    if seed is None:
        seed = np.random.randint(0, np.iinfo(np.int32).max)
    rng = np.random.default_rng(seed)

    qubits = np.array(qc.qubits, dtype=object, copy=True)

    # Apply arbitrary random operations in layers across all qubits.
    for layer_number in range(depth):
        # We generate all the randomness for the layer in one go, to avoid many separate calls to
        # the randomisation routines, which can be fairly slow.

        # This reliably draws too much randomness, but it's less expensive than looping over more
        # calls to the rng. After, trim it down by finding the point when we've used all the qubits.
        gate_specs = rng.choice(gates, size=len(qubits))
        cumulative_qubits = np.cumsum(gate_specs["num_qubits"], dtype=np.int64)
        # Efficiently find the point in the list where the total gates would use as many as
        # possible of, but not more than, the number of qubits in the layer.  If there's slack, fill
        # it with 1q gates.
        max_index = np.searchsorted(cumulative_qubits, num_qubits, side="right")
        gate_specs = gate_specs[:max_index]
        slack = num_qubits - cumulative_qubits[max_index - 1]
        if slack:
            gate_specs = np.hstack((gate_specs, rng.choice(gates_1q, size=slack)))

        # For efficiency in the Python loop, this uses Numpy vectorisation to pre-calculate the
        # indices into the lists of qubits and parameters for every gate, and then suitably
        # randomises those lists.
        q_indices = np.empty(len(gate_specs) + 1, dtype=np.int64)
        p_indices = np.empty(len(gate_specs) + 1, dtype=np.int64)
        q_indices[0] = p_indices[0] = 0
        np.cumsum(gate_specs["num_qubits"], out=q_indices[1:])
        np.cumsum(gate_specs["num_params"], out=p_indices[1:])
        # parameters = rng.uniform(0, 2 * np.pi, size=p_indices[-1])
        parameters = rng.choice(
            np.arange(0, 2 * np.pi + np.pi / 4, np.pi / 4), size=p_indices[-1]
        )
        rng.shuffle(qubits)

        # We've now generated everything we're going to need.  Now just to add everything.
        for gate, q_start, q_end, p_start, p_end in zip(
            gate_specs["class"],
            q_indices[:-1],
            q_indices[1:],
            p_indices[:-1],
            p_indices[1:],
        ):
            operation = gate(*parameters[p_start:p_end])
            qc.append(
                CircuitInstruction(operation=operation, qubits=qubits[q_start:q_end])
            )

    return qc
