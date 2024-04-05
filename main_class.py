import tkinter as tk
from tkinter import ttk
from ctypes import windll
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from qiskit import QuantumCircuit, transpile, assemble, Aer
from qiskit.quantum_info import Statevector
from qiskit.visualization.state_visualization import state_to_latex

windll.shcore.SetProcessDpiAwareness(1)


class PrepareTheState:
    def __init__(self, root):
        self.root = root
        self.root.title("Quantum Escape the Room")
        self.root.geometry("1000x900")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_window()

    def on_closing(self):
        plt.close('all')
        self.root.destroy()

    def create_window(self):
        self.rules_code = ttk.Frame(self.root, padding=(3, 3, 12, 12), width=500, height=450)
        self.rules_code.grid(column=0, row=0, sticky='nsew')

        self.target_game = ttk.Frame(self.root, padding=(3, 3, 12, 12), width=500, height=450)
        self.target_game.grid(column=1, row=0, sticky='nsew')

        self.create_rules_panel()
        self.create_player_code_panel()
        self.create_target_statevector_qsphere_panel()
        self.cartoon_game_panel()

    def create_rules_panel(self):
        rules = ttk.Frame(self.rules_code, borderwidth=5)
        rules.grid(column=0, row=0, sticky='nsew')

        rule_heading = ttk.LabelFrame(self.rules_code, text='How to play this game:')
        rule_heading.grid(column=0, row=0, sticky='new', columnspan=2, pady=(10, 5), padx=(10, 2))
        ttk.Label(rule_heading, text='Use your keyboard to move close to the door.').grid(column=0, row=0, sticky='nsw', columnspan=2)
        ttk.Label(rule_heading, text='Create the quantum circuit which gives you the target state').grid(column=0, row=1, sticky='nsw', columnspan=2)
        rules.columnconfigure('all', weight=1)

    def create_player_code_panel(self):
        code = ttk.Frame(self.rules_code)
        code.grid(column=0, row=1, sticky='news')
        code.columnconfigure('all', weight=1)

        ttk.Label(code, text='Build your quantum circuit below', font='TkHeadingFont', padding=(20, 1, 1, 5)).grid(column=0, row=0, sticky='ws')

        self.code_text = tk.Text(code, width=40, height=10)
        self.code_text.grid(column=0, row=1, sticky='new', columnspan=2, padx=(10, 2))

        simulate_button = ttk.Button(code, text='Simulate', command=self.simulate)
        simulate_button.grid(column=0, row=2)

        check_button = ttk.Button(code, text='Check!')
        check_button.grid(column=1, row=2)

        # self.canvas, self.canvas1 = None, None
        self.plot_area = tk.Canvas(code, width=450, height=300, relief="sunken", borderwidth=3)
        self.plot_area.grid(column=0, row=3, columnspan=2, sticky='nsew', pady=10, padx=(10, 2))
        self.plot_area.grid_anchor('center')

        self.player_state = tk.Canvas(code, width=450, height=150, relief="sunken", borderwidth=3)
        self.player_state.grid(column=0, row=4, columnspan=2, sticky='nsew', pady=1, padx=(10, 2))
        self.player_state.grid_anchor('center')

    def simulate(self):
        try:
            # Draw the QuantumCircuit
            local_namespace = {}
            self.user_code = self.code_text.get("1.0", "end-1c")
            exec(self.user_code, globals(), local_namespace)
            figure = plt.gcf()
            figure.set_size_inches((3.15, 2))

            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().destroy()

            self.canvas = FigureCanvasTkAgg(figure, self.plot_area)
            self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            self.canvas.draw()

            # Write the state vector in LaTeX format
            qcir = local_namespace.get(f'{self.find_quantumcircuit_variable(self.user_code)}')
            simulator = Aer.get_backend('statevector_simulator')
            job = simulator.run(qcir, shots=10)
            player_state = job.result().get_statevector()
            player_state_latex = state_to_latex(player_state)

            self.display_statevector(player_state_latex)

            state = plt.gcf()
            state.set_size_inches((3.15, 0.8))

            if hasattr(self, 'canvas1'):
                self.canvas1.get_tk_widget().destroy()

            self.canvas1 = FigureCanvasTkAgg(state, self.player_state)
            self.canvas1.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            self.canvas1.draw()


        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def find_quantumcircuit_variable(self, player_input):
        lines = player_input.split("\n")
        for line in lines:
            if "QuantumCircuit(" in line:
                var_name = line.split("=")[0].strip()
                return var_name

    def display_statevector(self, latex_statevector):
        tmptext = '$' + latex_statevector + '$'
        state_fig = plt.figure(dpi=100)
        ax = state_fig.add_subplot(111)
        ax.text(0.5, 0.5, tmptext, fontsize=14, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        ax.axis('off')

    def create_target_statevector_qsphere_panel(self):
        target = ttk.LabelFrame(self.target_game, text='Target statevector and its qsphere plot')
        target.grid(column=1, row=0, sticky='nsew', pady=(10, 5))
        target.columnconfigure('all', weight=1)

        target_state = tk.Canvas(target, width=450, height=150, relief="sunken", borderwidth=3)
        target_state.grid(column=1, row=0, columnspan=2, sticky='nsew', pady=10, padx=(2, 2))
        target_state.grid_anchor('center')

        qsphere_area = tk.Canvas(target, width=450, height=300, relief="sunken", borderwidth=3)
        qsphere_area.grid(column=1, row=1, columnspan=2, sticky='nsew', pady=10, padx=(2, 2))
        qsphere_area.grid_anchor('center')

    def cartoon_game_panel(self):
        lab_image = ttk.Frame(self.target_game)
        lab_image.grid(column=1, row=1, columnspan=2, sticky='nsew', pady=10, padx=(2, 2))



def main():
    root = tk.Tk()
    test = PrepareTheState(root)
    root.mainloop()


if __name__ == "__main__":
    main()

