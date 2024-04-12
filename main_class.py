import tkinter as tk
from tkinter import ttk
from ctypes import windll
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from qiskit import QuantumCircuit, Aer
from qiskit.visualization import plot_state_qsphere
from qiskit.visualization.state_visualization import state_to_latex
from statevectors import statevector_easy

windll.shcore.SetProcessDpiAwareness(1)


class PrepareTheState:
    def __init__(self, root):
        self.root = root
        self.root.title("Quantum Escape the Room")
        # self.root.geometry("1000x900")
        # self.root.resizable(0,0)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.dpi = self.root.winfo_fpixels('1i')

        self.create_window()

    def on_closing(self):
        plt.close('all')
        self.root.destroy()

    def create_window(self):
        self.rules_code = ttk.Frame(self.root, padding=(3, 3, 12, 12))
        self.rules_code.grid(column=0, row=0, sticky='nsew')

        self.target_game = ttk.Frame(self.root, padding=(3, 3, 12, 12))
        self.target_game.grid(column=2, row=0, sticky='nsew')

        self.create_rules_panel()
        self.create_player_code_panel()
        self.create_initial_target_qsphere_panel()
        self.get_statevecs_from_dict()

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

        ttk.Label(code, text='Build your quantum circuit below', font='TkHeadingFont', padding=(20, 1, 1, 5)).grid(column=0, row=0, sticky='news')

        self.code_text = tk.Text(code, width=40, height=10)
        self.code_text.grid(column=0, row=1, sticky='new', columnspan=2, padx=(10, 2))

        button_frame = ttk.Frame(code, width=500)
        button_frame.grid(column=0, row=2, sticky='new', columnspan=2, padx=(10, 2))

        simulate_button = ttk.Button(button_frame, text='Simulate', command=self.simulate)
        simulate_button.grid(column=0, row=0, padx=(70, 70))

        check_button = ttk.Button(button_frame, text='Check!')
        check_button.grid(column=1, row=0, padx=(70, 70))

        self.plot_area = tk.Canvas(code, width=500, height=300, relief="sunken", borderwidth=3)
        self.plot_area.grid(column=0, row=3, columnspan=2, sticky='nsew', pady=10, padx=(10, 2))
        self.plot_area.grid_anchor('center')
        self.plot_area.grid_propagate(False)

        self.player_state = tk.Canvas(code, width=500, height=500, relief="sunken", borderwidth=3)
        self.player_state.grid(column=0, row=4, columnspan=2, sticky='nsew', pady=(1, 5), padx=(10, 2))
        self.player_state.grid_anchor('center')
        self.player_state.grid_propagate(False)

    def simulate(self):
        try:
            # Draw the QuantumCircuit
            local_namespace = {}
            self.user_code = self.code_text.get("1.0", "end-1c")
            exec(self.user_code, globals(), local_namespace)
            figure = plt.gcf()
            figure.tight_layout()
            figure.set_size_inches((480 / self.dpi, 290 / self.dpi))

            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().destroy()

            self.canvas = FigureCanvasTkAgg(figure, self.plot_area)
            self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            self.canvas.draw()

            # Write the state vector in LaTeX format
            qcir = local_namespace.get(f'{self.find_quantumcircuit_variable(self.user_code)}')
            player_state = self.run_circuit(qcir)
            qsph = self.plot_qsphere(player_state)


            ## This will give statevector in latex format
            # player_state_latex = state_to_latex(player_state)
            # self.display_statevector(player_state_latex)
            # state = plt.gcf()

            qsph.set_size_inches((480 / self.dpi, 480 / self.dpi))

            if hasattr(self, 'canvas1'):
                self.canvas1.get_tk_widget().destroy()

            self.canvas1 = FigureCanvasTkAgg(qsph, self.player_state)
            self.canvas1.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            self.canvas1.draw()

        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")


    def plot_qsphere(self, statevec):
        qsphere = plot_state_qsphere(statevec)
        qsphere.tight_layout()

        # Adjust font size for all text elements in the qsphere
        for text in qsphere.findobj(match=plt.Text):
            text.set_fontsize(8)  # Set font size as per your preference

        return qsphere

    def find_quantumcircuit_variable(self, player_input):
        lines = player_input.split("\n")
        for line in lines:
            if "QuantumCircuit(" in line:
                var_name = line.split("=")[0].strip()
                return var_name

    def run_circuit(self, qc):
        simulator = Aer.get_backend('statevector_simulator')
        job = simulator.run(qc, shots=10)
        player_state = job.result().get_statevector()
        return player_state

    def display_statevector(self, latex_statevector):
        tmptext = '$' + latex_statevector + '$'
        state_fig = plt.figure(dpi=100)
        ax = state_fig.add_subplot(111)
        ax.text(0.5, 0.5, tmptext, fontsize=10, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        ax.axis('off')

    def create_initial_target_qsphere_panel(self):
        # Initial statevector as a qsphere
        initial = ttk.LabelFrame(self.target_game, text='Initial statevector qsphere plot')
        initial.grid(column=0, row=0, sticky='nsew', pady=(10, 5))
        initial.columnconfigure('all', weight=1)

        self.initial_qsphere = tk.Canvas(initial, width=500, height=500, relief="sunken", borderwidth=3)
        self.initial_qsphere.grid(column=0, row=0, columnspan=2, sticky='nsew', pady=10, padx=(2, 2))
        self.initial_qsphere.grid_anchor('center')

        # Target statevector as a qsphere that the player needs to prepare
        target = ttk.LabelFrame(self.target_game, text='Target statevector qsphere plot')
        target.grid(column=1, row=0, sticky='nsew', pady=(10, 5), padx=(5, 5))
        target.columnconfigure('all', weight=1)

        self.target_qsphere = tk.Canvas(target, width=500, height=500, relief="sunken", borderwidth=3)
        self.target_qsphere.grid(column=0, row=0, columnspan=2, sticky='nsew', pady=10, padx=(2, 2))
        self.target_qsphere.grid_anchor('center')

    def get_statevecs_from_dict(self):
        # Plot initial statevector on the qsphere
        init_statevec_qsphere = self.plot_qsphere(statevector_easy[1][0])
        init_statevec_qsphere.set_size_inches((480 / self.dpi, 480 / self.dpi))

        if hasattr(self, 'canvas_init_statevec'):
            self.canvas_init_statevec.get_tk_widget().destroy()

        self.canvas_init_statevec = FigureCanvasTkAgg(init_statevec_qsphere, self.initial_qsphere)
        self.canvas_init_statevec.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.canvas_init_statevec.draw()

        # Plot target statevector on the qsphere
        target_statevec_qsphere = self.plot_qsphere(statevector_easy[1][1])
        target_statevec_qsphere.set_size_inches((480 / self.dpi, 480 / self.dpi))

        if hasattr(self, 'canvas_tar_statevec'):
            self.canvas_tar_statevec.get_tk_widget().destroy()

        self.canvas_tar_statevec = FigureCanvasTkAgg(target_statevec_qsphere, self.target_qsphere)
        self.canvas_tar_statevec.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.canvas_tar_statevec.draw()




    def cartoon_game_panel(self):
        lab_image = tk.Canvas(self.target_game, height=600, relief='sunken', borderwidth=3)
        lab_image.grid(column=1, row=1, columnspan=3, sticky='sew', pady=10, padx=(2, 2))

        red_PC = tk.PhotoImage(file="Room_with_red_PC.gif")
        lab_image.create_image(350, 300, image=red_PC, anchor='center')




def main():
    root = tk.Tk()
    test = PrepareTheState(root)
    root.mainloop()


if __name__ == "__main__":
    main()

