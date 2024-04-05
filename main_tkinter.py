import tkinter as tk
from tkinter import ttk
from ctypes import windll
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from qiskit import QuantumCircuit, transpile, assemble, Aer
from qiskit.quantum_info import Statevector
from qiskit.visualization.state_visualization import state_to_latex
import matplotlib

windll.shcore.SetProcessDpiAwareness(1)

root = tk.Tk()
root.title("Quantum Escape the Room")
root.geometry("1000x900")  # Set window size
# root.resizable(0, 0)
root.update_idletasks()


def simulate():
    global canvas, canvas1

    try:
        # Draw the QuantumCircuit
        user_code = code_text.get("1.0", "end-1c")
        exec(user_code, globals(), locals())
        figure = plt.gcf()
        figure.set_size_inches((3.15, 2))

        if canvas:
            canvas.get_tk_widget().destroy()
        canvas = FigureCanvasTkAgg(figure, plot_area)
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        canvas.draw()

        # Get the state vector from the QuantumCircuit
        quantum_circuit_var = find_quantum_circuit_variable(user_code)
        state_code = (f"{user_code}\n"
                      "simulator = Aer.get_backend('statevector_simulator')\n"
                      f"job = simulator.run({quantum_circuit_var}, shots=10)\n"
                      "player_state = job.result().get_statevector()\n"
                      "tmptext = '$'+state_to_latex(player_state)+'$'\n"
                      "state_fig = plt.figure(dpi=100)\n"
                      "wx = state_fig.add_subplot(111)\n"
                      "wx.text(0.5, 0.5, tmptext, fontsize=14, horizontalalignment='center',verticalalignment='center', transform=wx.transAxes)\n"
                      "wx.axis('off')")

        exec(state_code, globals(), locals())
        state = plt.gcf()
        state.set_size_inches((3.15, 0.8))

        if canvas1:
            canvas1.get_tk_widget().destroy()
        canvas1 = FigureCanvasTkAgg(state, player_state)
        canvas1.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        canvas1.draw()

    except Exception as e:
        tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")


def find_quantum_circuit_variable(codetext):
    lines = codetext.split("\n")
    for line in lines:
        if "QuantumCircuit(" in line:
            var_name = line.split("=")[0].strip()
            return var_name
    return None

def on_closing():
    plt.close('all')  # Close all matplotlib plots
    root.destroy()    # Close the tkinter window


def check():
    # Function to check something
    print("Checking...")


rules_code = ttk.Frame(root, padding=(3, 3, 12, 12), width=500, height=450)
rules_code.grid(column=0, row=0, sticky='nsew')

target_game = ttk.Frame(root, padding=(3, 3, 12, 12), width=500, height=450)
target_game.grid(column=1, row=0, sticky='nsew')

rules_code.columnconfigure('all', weight=1)
target_game.columnconfigure('all', weight=1)

# Panels for adding rules
rules = ttk.Frame(rules_code, padding=5, borderwidth=5)
rules.grid(column=0, row=0, sticky='nsew')

rule_heading = ttk.LabelFrame(rules, text='How to play this game:')
rule_heading.grid(column=0, row=0, sticky='new', columnspan=2)
ttk.Label(rule_heading, text='Use your keyboard to move close to the door.').grid(column=0, row=0, sticky='nsw',
                                                                                  columnspan=2)
ttk.Label(rule_heading, text='Create the quantum circuit which gives you the target state').grid(column=0, row=1,
                                                                                                 sticky='nsw',
                                                                                                 columnspan=2)
rules.columnconfigure('all', weight=1)

# Panel for player code
code = ttk.Frame(rules_code)
code.grid(column=0, row=1, sticky='news')

code.columnconfigure('all', weight=1)

ttk.Label(code, text='Build your quantum circuit below', font='TkHeadingFont', padding=(20, 1, 1, 5)).grid(column=0, row=0, sticky='ws')



code_text = tk.Text(code, width=40, height=10)
code_text.grid(column=0, row=1, sticky='new', columnspan=2, padx=(10, 2))

simulate_button = ttk.Button(code, text='Simulate', command=simulate)
simulate_button.grid(column=0, row=2)

check_button = ttk.Button(code, text='Check!', command=check)
check_button.grid(column=1, row=2)

canvas, canvas1 = None, None
plot_area = tk.Canvas(code, width=450, height=300, relief="sunken", borderwidth=3)
plot_area.grid(column=0, row=3, columnspan=2, sticky='nsew', pady=10, padx=(10, 2))
plot_area.grid_anchor('center')

player_state = tk.Canvas(code, width=450, height=150, relief="sunken", borderwidth=3)
player_state.grid(column=0, row=4, columnspan=2, sticky='nsew', pady=1, padx=(10, 2))
player_state.grid_anchor('center')


# Target statevector display window
target = ttk.LabelFrame(target_game, text='Target statevector and its qsphere plot')
target.grid(column=1, row=0, sticky='nsew', pady=(10, 5))
target.columnconfigure('all', weight=1)


target_state = tk.Canvas(target, width=450, height=150, relief="sunken", borderwidth=3)
target_state.grid(column=1, row=0, columnspan=2, sticky='nsew', pady=10, padx=(2, 2))
target_state.grid_anchor('center')


qsphere_area = tk.Canvas(target, width=450, height=300, relief="sunken", borderwidth=3)
qsphere_area.grid(column=1, row=1, columnspan=2, sticky='nsew', pady=10, padx=(2, 2))
qsphere_area.grid_anchor('center')


# Lab cartoon
lab_image = ttk.Frame(target_game)
lab_image.grid(column=1, row=1, columnspan=2, sticky='nsew', pady=10, padx=(2, 2))

cartoon = tk.Canvas(lab_image, width=450, height=150, borderwidth=3)
cartoon.grid(column=1, row=2, columnspan=2, sticky='nsew', pady=10, padx=(2, 2))

# Bind the closing event of the tkinter window
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()

