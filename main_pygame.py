# from qiskit import QuantumCircuit, transpile, assemble, Aer
# from qiskit.quantum_info import Statevector
# from qiskit.visualization import plot_bloch_multivector, plot_histogram
#
# def quantum_escape_room(player_circuit, target_state):
#     # Create a quantum circuit with one qubit
#     qc = QuantumCircuit(player_circuit.num_qubits)
#
#
#     # Apply the player's circuit
#     qc.compose(player_circuit, player_circuit.qubits, inplace=True)
#
#     # Execute the circuit
#     simulator = Aer.get_backend('statevector_simulator')
#     job = simulator.run(qc, shots=10)
#     player_state = job.result().get_statevector()
#
#     # Compare the player's state with the target state
#     if Statevector(player_state).equiv(target_state):
#         return "The door opens and you proceed to the next room!"
#     else:
#         return "The door remains locked. Try again!"
#
# # Test the game
# player_circuit = QuantumCircuit(1)
# player_circuit.h(0)
#
# target_state = Statevector.from_label('+')
# print(quantum_escape_room(player_circuit, target_state))
import pygame as pg
from sys import exit
from input_box import render_textbox

width = 1000
height = 800

pg.init()
screen = pg.display.set_mode((width, height))
pg.display.set_caption('Quantum Escape the Room')
clock = pg.time.Clock()

####### Room 1 surface
room1_surf = pg.Surface((int(width / 2), int(height / 2))).convert()
room1_surf.fill('deepskyblue')

####### player input surface
player_input_surf = pg.Surface((int(width / 2), int(height))).convert()
player_input_surf.fill('gold1')

# Font
font = pg.font.SysFont('Arial', 24)

####### target surface
target_surf = pg.Surface((int(width / 2), int(height / 2))).convert()
target_surf.fill('grey70')

####### Simulate surface
simulate_text = font.render(' Simulate ', True, 'white', 'darkblue')
simulate_rect = simulate_text.get_rect(topleft=(width/8 - simulate_text.get_width(), height/2 + 10))  # Get the rect of the text

####### Check surface
check_text = font.render(' Check ', True, 'white', 'darkblue')
check_rect = simulate_text.get_rect(topleft=(width/4 + simulate_text.get_width(), height/2 + 10))  # Get the rect of the text

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()



        # displaying the room1, player input, and target surface
        screen.blit(room1_surf, (width / 2, height / 2))
        screen.blit(player_input_surf, (0, 0))
        screen.blit(target_surf, (width / 2, 0))

        # Add buttons for Simulating and checking the state vector
        screen.blit(simulate_text, simulate_rect)  # Blit the text onto the surface
        screen.blit(check_text, check_rect)

        # Render the player input code textbox
        player_code = render_textbox(screen, 2, 2, width / 2 - 4, height / 2 - 4, font, 'white')

    pg.display.update()
    clock.tick(60)




# import pg
# from qiskit import QuantumCircuit, Aer
# from qiskit.quantum_info import Statevector
#
# # Initialize pg
# pg.init()
#
# # Set up the screen
# WIDTH, HEIGHT = 800, 600
# screen = pg.display.set_mode((WIDTH, HEIGHT))
# pg.display.set_caption("Quantum Escape the Room")
#
# # Colors
# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
#
# # Fonts
# font = pg.font.SysFont(None, 32)
#
# # Quantum Circuit
# player_circuit = QuantumCircuit(1)
# target_state = Statevector.from_label('+')
#
# # Function to draw text on screen
# def draw_text(text, color, x, y):
#     text_surface = font.render(text, True, color)
#     text_rect = text_surface.get_rect()
#     text_rect.center = (x, y)
#     screen.blit(text_surface, text_rect)
#
# # Main game loop
# running = True
# while running:
#     screen.fill(WHITE)
#
#     # Check for events
#     for event in pg.event.get():
#         if event.type == pg.QUIT:
#             running = False
#
#     # Draw the game elements
#     draw_text("Quantum Escape the Room", BLACK, WIDTH // 2, 50)
#
#     # Draw the player's quantum circuit
#     draw_text("Player's Quantum Circuit:", BLACK, 150, 150)
#     draw_text(str(player_circuit), BLACK, 150, 180)
#
#     # Draw the target state
#     draw_text("Target Statevector: " + str(target_state), BLACK, 150, 250)
#
#     # Execute the player's circuit and check if it matches the target state
#     simulator = Aer.get_backend('statevector_simulator')
#     job = simulator.run(player_circuit, shots=10)
#     player_state = job.result().get_statevector()
#
#     if Statevector(player_state).equiv(target_state):
#         draw_text("The door opens and you proceed to the next room!", BLACK, WIDTH // 2, 400)
#     else:
#         draw_text("The door remains locked. Try again!", BLACK, WIDTH // 2, 400)
#
#     pg.display.flip()
#
# # Quit pg
# pg.quit()
