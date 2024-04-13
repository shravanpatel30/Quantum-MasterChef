# This file contains the statevectors in a dictionary format {"1" : [initial state, final state, hints]}
from qiskit.quantum_info import Statevector

statevector_easy = {1: [Statevector.from_label('00'), Statevector([0.70710678+0.j, 0.+0.j, 0.+0.j, 0.70710678+0.j], dims=(2, 2)), "This state is also referred as Φ+. Use H and CX gates"],
                    2: [Statevector.from_label('00'), Statevector([0.70710678-8.65956056e-17j,  0.+0.00e+00j, 0.+0.00e+00j, -0.70710678+8.65956056e-17j], dims=(2, 2)), "This state is also referred as Φ-. Same as first Bell state but with a negative phase!"],
                    3: [Statevector.from_label('00'), Statevector([0.+0.j, 0.70710678+0.j, 0.70710678+0.j, 0.+0.j], dims=(2, 2)), "This state is also referred as Ψ+. Use H, CX and X gates"],
                    4: [Statevector.from_label('00'), Statevector([0.+0.j,  0.70710678-0.j, -0.70710678+0.j, -0.+0.j],dims=(2, 2)), "This state is also referred as Ψ-. This state just has a phase compared to Ψ+"]}

# print(list(statevector_easy.keys())[3])
#
# print(len(statevector_easy))