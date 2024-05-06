import tkinter as tk
from tkinter import ttk, font
from tkinter.font import Font
from ctypes import windll
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from qiskit_aer import Aer
from qiskit.compiler import transpile
from qiskit import QuantumCircuit
from qiskit.quantum_info import state_fidelity
from qiskit.visualization import plot_state_qsphere
# from qiskit.visualization.state_visualization import state_to_latex
from qiskit.quantum_info import Statevector
from statevectors import statevector_easy, random_circuit
import numpy as np
import random
import textwrap

windll.shcore.SetProcessDpiAwareness(1)


class PrepareTheState:
    def __init__(self, root):
        self.root = root
        self.root.title('Quantum Master Chef')
        # self.root.geometry("1620x1210")
        self.root.geometry('+300+100')
        self.root.resizable(0, 0)
        tk.font.nametofont('TkDefaultFont').configure(family='Verdana', size=9, weight=font.NORMAL)
        self.StatusFont = Font(family='Verdana', size=12, weight=font.NORMAL)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.dpi = self.root.winfo_fpixels('1i')
        self.design_dpi = 143.858407079646
        global scale
        scale = self.dpi / self.design_dpi

        self.previous_choice = 'easy'  # Keep track of the previous mode
        self.statevec_index_easy = 1
        self.statevec_index_advanced = 1
        self.statevector_advanced = self.advanced_mode_statevector_dict()
        self.show_hint = False
        self.create_window()

    def on_closing(self):
        plt.close('all')
        self.root.destroy()

    def create_window(self):
        self.rules_code = ttk.Notebook(self.root, padding=(10*scale, 10*scale, 12*scale, 12*scale))
        self.rules_code.grid(column=0, row=0, sticky='nsew')

        self.target_game = ttk.Frame(self.root, padding=(3*scale, 3*scale, 5*scale, 5*scale))
        self.target_game.grid(column=2, row=0, sticky='nsew')

        self.create_rules_panel()
        self.create_player_code_panel()
        self.create_initial_target_qsphere_panel()
        self.get_statevecs_from_dict()
        self.status_panel()
        self.hints_panel()
        self.root.iconbitmap('logo_small.ico')

    def create_rules_panel(self):
        rules = ttk.Frame(self.rules_code, borderwidth=5*scale)
        rules.grid(column=0, row=0, sticky='nsew')

        self.rules_code.add(rules, text=' Instructions ', padding=2*scale)

        instructions = ('''
         - On the right side you are given the initial ingredient (initial statevector) and the final dish (target statevector).
        
         - Your goal as a Quantum Chef is to prepare a quantum recipie (quantum circuit) that will use the initial ingredient to prepare the final dish.
         
         - The QSphere plots are interactive so you can rotate them for visual clarity.
        
         - Below is an example of how you can prepare a recipie:
        
        
         from qiskit import QuantumCircuit
         from qiskit.quantum_info import Statevector
        
         qc = QuantumCircuit(2)
         qc.initialize(Statevector.from_label('11'))
         qc.x([0,1])
         qc.draw('mpl')
        
        
         - After you have a trial recipie (circuit), press the 'Simulate' button first. This will show you how your circuit looks and the final statevector that is prepared using your recipie.
        
         - Once you have simulated your recipie, you can go ahead and press the 'Check' button to compare your final statevector with the given final statevector.
        ''')

        deindented_instructions = textwrap.dedent(instructions)

        how_to_play = tk.LabelFrame(rules,  text='How to play the game:', pady=2*scale, padx=10*scale)
        how_to_play.grid(column=0, row=0, sticky='nsew')
        ttk.Label(how_to_play, text=deindented_instructions, wraplength=490 * scale, justify='left', anchor='w').grid(column=0, row=0, sticky='nsew')

        important_points = ('''
        - Only use .draw('mpl') at the end of your quantum circuit so that the game displays your quantum circuit without problems.
        
        - Make sure you use only .initialize() method to initialize your circuit (this is the best way to initialize the circuit).
        
        - For advanced mode, you might want to first build a circuit just for the initial state and then extract the Statevector from that circuit and use it in the final circuit (make sure you only use .draw('mpl') once).
        ''')

        deindented_imp_points = textwrap.dedent(important_points)

        imp_points = tk.LabelFrame(rules, text='Important points to remember:', padx=10*scale)
        imp_points.grid(column=0, row=1, sticky='nsew', pady=(10*scale, 5*scale))
        ttk.Label(imp_points, text=deindented_imp_points, wraplength=490 * scale, justify='left', anchor='w').grid(column=0, row=0, sticky='nsew')


    def create_player_code_panel(self):
        self.code = tk.Frame(self.rules_code)
        self.code.grid(column=0, row=1, sticky='news')

        self.rules_code.add(self.code, text=' Code Here ', padding=2*scale)

        text_heading = ttk.Label(self.code, text='Build your quantum circuit below:', padding=(5*scale, 10*scale, 1*scale, 5*scale))
        text_heading.grid(column=0, row=0, sticky='news')

        text_frame = ttk.Frame(self.code, width=510*scale, height=215*scale)
        text_frame.grid(column=0, row=1, columnspan=2)

        text_frame.columnconfigure(0, weight=9)
        text_frame.columnconfigure(1, weight=1)
        text_frame.rowconfigure(0, weight=10)

        self.code_text = tk.Text(text_frame, wrap='word')
        self.code_text.grid(column=0, row=0, sticky='nsew', padx=(4*scale, 0))

        scrollb = ttk.Scrollbar(text_frame, orient='vertical', command=self.code_text.yview)
        scrollb.grid(column=3, row=0, sticky='nsew')
        self.code_text.configure(yscrollcommand=scrollb.set)

        text_frame.grid_propagate(False)

        button_frame = tk.Frame(self.code, width=500*scale)
        button_frame.grid(column=0, row=2, columnspan=2, sticky='nsew', padx=(4*scale, 4*scale))

        button_frame.columnconfigure([0, 1], weight=1)

        simulate_button = ttk.Button(button_frame, text='Simulate', command=self.simulate)
        simulate_button.grid(column=0, row=0)

        check_button = ttk.Button(button_frame, text='Check!', command=self.check_statevectors)
        check_button.grid(column=1, row=0)

        self.plot_area = tk.Canvas(self.code, width=500*scale, height=300*scale, relief="sunken", borderwidth=3*scale, background='grey95')
        self.plot_area.grid(column=0, row=3, columnspan=2, sticky='nsew', pady=10*scale, padx=(4*scale, 4*scale))
        self.plot_area.grid_anchor('center')
        self.plot_area.grid_propagate(False)

        self.player_state = tk.Canvas(self.code, width=500*scale, height=500*scale, relief="sunken", borderwidth=3*scale, background='grey95')
        self.player_state.grid(column=0, row=4, columnspan=2, sticky='nsew', pady=(1*scale, 5*scale), padx=(4*scale, 4*scale))
        self.player_state.grid_anchor('center')
        self.player_state.grid_propagate(False)

    def simulate(self):
        try:
            # Draw the QuantumCircuit
            local_namespace = {}
            user_code = self.code_text.get("1.0", "end-1c")
            exec(user_code, globals(), local_namespace)

            self.qcir = local_namespace.get(f'{self.find_quantumcircuit_variable(user_code)}')

            ## Here I have maipulated the player circuit to make the initialize gate appear nicer without changing any of player's circuit
            # First, I separate the CircuitInstruction corresponding to 'initialize' and make a quantumcircuit
            # exclusively for the initial state vector
            self.qcir_init = QuantumCircuit(self.qcir.num_qubits, name='init')
            init_list = self.qcir.get_instructions('initialize')

            if init_list:
                self.qcir_init = self.qcir_init.from_instructions(self.qcir.get_instructions('initialize'), qubits=self.qcir.qubits, name='init')
            else:
                self.qcir_init.initialize(Statevector.from_label('0'*self.qcir.num_qubits))


            # Then we create another dummy circuit and transfer all the CircuitInstructions except the 'initialize' from the player circuit to qcir_dummy
            qcir_dummy = QuantumCircuit(self.qcir.num_qubits)
            player_cir_instructions = self.qcir.data

            if init_list:
                player_cir_instructions.pop(0)

            qcir_dummy = qcir_dummy.from_instructions(player_cir_instructions, qubits=self.qcir.qubits, name='player_cir')

            # Lastly, I append the qcir_init and qcir_dummy and decompose just the qcir_dummy. Now the 'initialize' gate looks much nicer and smaller!
            self.qcir_display = QuantumCircuit(self.qcir.num_qubits)
            self.qcir_display.append(self.qcir_init, qargs=self.qcir.qubits)
            self.qcir_display.append(qcir_dummy, qargs=self.qcir.qubits)
            self.qcir_display.decompose(gates_to_decompose='player_cir').draw('mpl')

            figure = plt.gcf()
            figure.tight_layout()
            figure.set_size_inches((470*scale / self.dpi, 280*scale / self.dpi))

            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().destroy()
                self.canvas.figure.clf()
                plt.close(self.canvas.figure)

            self.canvas = FigureCanvasTkAgg(figure, self.plot_area)
            self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5*scale, pady=5*scale)
            self.canvas.draw()

            # Plot the qsphere from player circuit
            player_state = self.run_circuit(self.qcir_display)
            qsph = self.plot_qsphere(player_state)


            ## This will give statevector in latex format
            # player_state_latex = state_to_latex(player_state)
            # self.display_statevector(player_state_latex)
            # state = plt.gcf()

            qsph.set_size_inches((470*scale / self.dpi, 470*scale / self.dpi))

            if hasattr(self, 'canvas1'):
                self.canvas1.get_tk_widget().destroy()
                self.canvas1.figure.clf()
                plt.close(self.canvas1.figure)

            self.canvas1 = FigureCanvasTkAgg(qsph, self.player_state)
            self.canvas1.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5*scale, pady=5*scale)
            self.canvas1.draw()

            self.player_circuit_depth.configure(text=f'Player Circuit Depth: {self.qcir_display.depth()}')

            if self.choice.get() == 'easy':
                self.statevec_fidelity.configure(text=f'State fidelity: {round(state_fidelity(self.run_circuit(self.qcir_display), statevector_easy[self.statevec_index_easy][1], validate=False), 4)}')
            if self.choice.get() == 'advanced':
                self.statevec_fidelity.configure(text=f'State fidelity: {round(state_fidelity(self.run_circuit(self.qcir_display), self.statevector_advanced[self.statevec_index_advanced][1], validate=False), 4)}')

        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def plot_qsphere(self, statevec):
        qsphere = plot_state_qsphere(statevec, show_state_phases=True)
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
        qc = transpile(qc, backend=simulator)
        job = simulator.run(qc, shots=1024)
        player_state = job.result().get_statevector()
        return player_state

    def display_statevector(self, latex_statevector):
        tmptext = '$' + latex_statevector + '$'
        state_fig = plt.figure(dpi=100)
        ax = state_fig.add_subplot(111)
        ax.text(0.5, 0.5, tmptext, fontsize=10, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        ax.axis('off')

    def check_statevectors(self):
        # Check if the player used correct initial statevector
        if self.choice.get() == 'easy':
            try:
                sv_init_player = self.run_circuit(self.qcir_init)
                sv_init_target = statevector_easy[self.statevec_index_easy][0]

                if not Statevector(sv_init_player).equiv(sv_init_target):
                    tk.messagebox.showinfo("Attention", "The initial statevector is not correct! Make sure you are using the proper initial statevector.")
                else:
                    try:
                        sv1 = self.run_circuit(self.qcir_display)
                        sv2 = statevector_easy[self.statevec_index_easy][1]

                        if Statevector(sv1).equiv(sv2):
                            self.plot_area.configure(background='green2')
                            self.player_state.configure(background='green2')
                            self.status_frame.configure(background='green2')
                            self.problem_num_easy.configure(background='green2')
                            self.problem_num_advanced.configure(background='green2')
                            self.statevec_fidelity.configure(background='green2')
                            self.player_circuit_depth.configure(background='green2')
                        else:
                            self.plot_area.configure(background='indianred1')
                            self.player_state.configure(background='indianred1')
                            self.status_frame.configure(background='indianred1')
                            self.problem_num_easy.configure(background='indianred1')
                            self.problem_num_advanced.configure(background='indianred1')
                            self.statevec_fidelity.configure(background='indianred1')
                            self.player_circuit_depth.configure(background='indianred1')

                        return Statevector(sv1).equiv(sv2)
                    except ValueError:
                        tk.messagebox.showinfo("Can't proceed!", "Prepare the given target statevector before proceeding.")

            except ValueError:
                tk.messagebox.showinfo("Attention", "No quantum circuit found!")

        if self.choice.get() == 'advanced':
            try:
                sv_init_player = self.run_circuit(self.qcir_init)
                sv_init_target = self.statevector_advanced[self.statevec_index_advanced][0]

                if not Statevector(sv_init_player).equiv(sv_init_target):
                    tk.messagebox.showinfo("Attention", "The initial statevector is not correct! Make sure you are using the proper initial statevector.")
                else:
                    try:
                        sv1 = self.run_circuit(self.qcir_display)
                        sv2 = self.statevector_advanced[self.statevec_index_advanced][1]

                        if Statevector(sv1).equiv(sv2):
                            self.plot_area.configure(background='green2')
                            self.player_state.configure(background='green2')
                            self.status_frame.configure(background='green2')
                            self.problem_num_easy.configure(background='green2')
                            self.problem_num_advanced.configure(background='green2')
                            self.statevec_fidelity.configure(background='green2')
                            self.player_circuit_depth.configure(background='green2')
                        else:
                            self.plot_area.configure(background='indianred1')
                            self.player_state.configure(background='indianred1')
                            self.status_frame.configure(background='indianred1')
                            self.problem_num_easy.configure(background='indianred1')
                            self.problem_num_advanced.configure(background='indianred1')
                            self.statevec_fidelity.configure(background='indianred1')
                            self.player_circuit_depth.configure(background='indianred1')

                        return Statevector(sv1).equiv(sv2)
                    except ValueError:
                        tk.messagebox.showinfo("Can't proceed!", "Prepare the given target statevector before proceeding.")

            except ValueError:
                tk.messagebox.showinfo("Attention", "No quantum circuit found!")

    def create_initial_target_qsphere_panel(self):
        # Add radio buttons for selecting the difficulty
        radio_button_frame = ttk.Frame(self.target_game, relief='groove', borderwidth=3*scale)
        radio_button_frame.grid(column=0, row=0, columnspan=2, sticky='nsew', padx=(5*scale, 5*scale), pady=(5*scale, 2*scale))

        radio_button_frame.columnconfigure(0, weight=1)
        radio_button_frame.columnconfigure(1, weight=1)

        self.choice = tk.StringVar()
        self.choice.set(value='easy')

        easy = ttk.Radiobutton(radio_button_frame, text='Easy/Practice mode', variable=self.choice, value='easy', command=self.on_radio_button_change)
        easy.grid(column=0, row=0, sticky='ew', padx=(150*scale, 0), pady=(5*scale, 5*scale))

        difficult = ttk.Radiobutton(radio_button_frame, text='Advanced mode', variable=self.choice, value='advanced', command=self.on_radio_button_change)
        difficult.grid(column=1, row=0, sticky='ew', padx=(150*scale, 0), pady=(5*scale, 5*scale))

        # Initial statevector as a qsphere
        initial = ttk.LabelFrame(self.target_game, text='Initial statevector QSphere plot')
        initial.grid(column=0, row=1, sticky='nsw', pady=(10*scale, 5*scale))
        initial.columnconfigure('all', weight=1)

        self.initial_qsphere = tk.Canvas(initial, width=500*scale, height=500*scale, relief="sunken", borderwidth=3*scale)
        self.initial_qsphere.grid(column=0, row=0, columnspan=2, sticky='nsew', pady=10*scale, padx=(2*scale, 0*scale))
        self.initial_qsphere.grid_anchor('center')
        self.initial_qsphere.grid_propagate(False)

        # Target statevector as a qsphere that the player needs to prepare
        target = ttk.LabelFrame(self.target_game, text='Target statevector QSphere plot')
        target.grid(column=1, row=1, pady=(10*scale, 5*scale), padx=(5*scale, 5*scale))
        target.columnconfigure('all', weight=1)

        self.target_qsphere = tk.Canvas(target, width=500*scale, height=500*scale, relief="sunken", borderwidth=3*scale)
        self.target_qsphere.grid(column=0, row=0, columnspan=2, sticky='nsew', pady=10*scale, padx=(2*scale, 0))
        self.target_qsphere.grid_anchor('center')
        self.target_qsphere.grid_propagate(False)

        next_button = ttk.Button(self.target_game, text='Next Question', command=self.get_next_statevector)
        next_button.grid(column=0, row=2, columnspan=2, ipadx=20*scale, ipady=5*scale)
        next_button.grid_anchor('center')

    def status_panel(self):
        # self.target_game.rowconfigure(3, weight=1)  # Set equal weights to rows 3 and 4
        # self.target_game.rowconfigure(4, weight=1)

        # Canvas that indicates progress and status
        status = ttk.Labelframe(self.target_game, text='Status panel')
        status.grid(column=0, row=3, columnspan=4, pady=(0, 5*scale), sticky='new')

        # Add weight to the columns and rows
        status.columnconfigure(0, weight=1)
        status.rowconfigure(0, weight=1)

        self.status_frame = tk.Frame(status, height=210*scale, relief='sunken', borderwidth=3*scale)
        self.status_frame.grid(column=0, row=0, padx=(2*scale, 0), sticky='nsew')
        self.status_frame.grid_propagate(False)

        self.status_frame.columnconfigure([0, 1], weight=1)
        self.status_frame.rowconfigure([0, 1], weight=1)

        # progress_image = tk.PhotoImage(file='/icons/progress.png')
        self.problem_num_easy = ttk.Label(self.status_frame, text=f'Easy Questions Progress: {self.statevec_index_easy} of {len(statevector_easy)}', font=self.StatusFont)
        self.problem_num_easy.grid(column=0, row=0, sticky='nsew', padx=(20*scale, 10*scale))

        self.problem_num_advanced = ttk.Label(self.status_frame, text=f'Advanced Questions Progress: {self.statevec_index_advanced} of {len(self.statevector_advanced)}', font=self.StatusFont)
        self.problem_num_advanced.grid(column=0, row=1, sticky='nsew', padx=(20*scale, 10*scale))

        self.statevec_fidelity = ttk.Label(self.status_frame, text=f'State fidelity: 0', font=self.StatusFont)
        self.statevec_fidelity.grid(column=1, row=0, sticky='nsew', padx=(10*scale, 10*scale))

        self.player_circuit_depth = ttk.Label(self.status_frame, text=f'Player Circuit Depth: 0', font=self.StatusFont)
        self.player_circuit_depth.grid(column=1, row=1, sticky='nsew', padx=(10*scale, 10*scale))



    def hints_panel(self):
        # Canvas that displays hints
        hints = ttk.Labelframe(self.target_game, height=250*scale, text='If you want a hint!')
        hints.grid(column=0, row=4, columnspan=4, pady=(20*scale, 5*scale), sticky='nsew')
        hints.grid_propagate(False)

        # Add weight to the columns and rows
        hints.columnconfigure(0, weight=1)
        hints.rowconfigure(0, weight=1)

        # Create a button in the "Hints" frame
        self.hint_button = tk.Button(hints, text='Click here to reveal the hint', command=self.toggle_hint, font=self.StatusFont, wraplength=1000*scale)
        self.hint_button.grid(column=0, row=0, sticky='nsew', padx=(5*scale, 5*scale), pady=(0, 2*scale))  # Make the button occupy the whole space
        # print(font.families())

    def toggle_hint(self):
        if not self.show_hint:  # Check if the button is visible
            if self.choice.get() == 'easy':
                self.hint_button.configure({'text': statevector_easy[self.statevec_index_easy][2] + str('. Click here again to hide the hint!')})
                self.show_hint = not self.show_hint
            if self.choice.get() == 'advanced':
                self.hint_button.configure({'text': self.statevector_advanced[self.statevec_index_advanced][2] + str('. Click here again to hide the hint!')})
                self.show_hint = not self.show_hint
        else:
            self.hint_button.configure({'text': 'Click here to reveal the hint'})
            self.show_hint = not self.show_hint

    def on_radio_button_change(self):
        # Reset current question solved when changing from easy to advanced
        if self.choice.get() == 'advanced':
            # Check if switching from easy to advanced
            if self.previous_choice == 'easy':
                # Allow switching to the first advanced question
                self.get_statevecs_from_dict()

                if self.show_hint:
                    self.hint_button.invoke()
            self.previous_choice = 'advanced'

        elif self.choice.get() == 'easy':
            # Handle switching from advanced to easy
            if self.previous_choice == 'advanced':
                self.get_statevecs_from_dict()

                if self.show_hint:
                    self.hint_button.invoke()
            self.previous_choice = 'easy'

    def get_statevecs_from_dict(self):
        if self.choice.get() == 'easy':
            # Plot initial statevector on the qsphere from easy statevector dictionary
            init_statevec_qsphere = self.plot_qsphere(statevector_easy[self.statevec_index_easy][0])
            init_statevec_qsphere.set_size_inches((480*scale / self.dpi, 480*scale / self.dpi))

            if hasattr(self, 'canvas_init_statevec'):
                self.canvas_init_statevec.get_tk_widget().destroy()
                self.canvas_init_statevec.figure.clf()
                plt.close(self.canvas_init_statevec.figure)

            self.canvas_init_statevec = FigureCanvasTkAgg(init_statevec_qsphere, self.initial_qsphere)
            self.canvas_init_statevec.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5*scale, pady=5*scale)
            self.canvas_init_statevec.draw()

            # Plot target statevector on the qsphere from easy statevector dictionary
            target_statevec_qsphere = self.plot_qsphere(statevector_easy[self.statevec_index_easy][1])
            target_statevec_qsphere.set_size_inches((480*scale / self.dpi, 480*scale / self.dpi))

            if hasattr(self, 'canvas_tar_statevec'):
                self.canvas_tar_statevec.get_tk_widget().destroy()
                self.canvas_tar_statevec.figure.clf()
                plt.close(self.canvas_tar_statevec.figure)

            self.canvas_tar_statevec = FigureCanvasTkAgg(target_statevec_qsphere, self.target_qsphere)
            self.canvas_tar_statevec.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5*scale, pady=5*scale)
            self.canvas_tar_statevec.draw()

        if self.choice.get() == 'advanced':
            # Plot initial statevector on the qsphere from the advanced statevector dictionary that is generated randomly everytime
            init_statevec_qsphere = self.plot_qsphere(self.statevector_advanced[self.statevec_index_advanced][0])
            init_statevec_qsphere.set_size_inches((480*scale / self.dpi, 480*scale / self.dpi))

            if hasattr(self, 'canvas_init_statevec'):
                self.canvas_init_statevec.get_tk_widget().destroy()
                self.canvas_init_statevec.figure.clf()
                plt.close(self.canvas_init_statevec.figure)

            self.canvas_init_statevec = FigureCanvasTkAgg(init_statevec_qsphere, self.initial_qsphere)
            self.canvas_init_statevec.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5*scale, pady=5*scale)
            self.canvas_init_statevec.draw()

            # Plot target statevector on the qsphere from the advanced statevector dictionary that is generated randomly everytime
            target_statevec_qsphere = self.plot_qsphere(self.statevector_advanced[self.statevec_index_advanced][1])
            target_statevec_qsphere.set_size_inches((480*scale / self.dpi, 480*scale / self.dpi))

            if hasattr(self, 'canvas_tar_statevec'):
                self.canvas_tar_statevec.get_tk_widget().destroy()
                self.canvas_tar_statevec.figure.clf()
                plt.close(self.canvas_tar_statevec.figure)

            self.canvas_tar_statevec = FigureCanvasTkAgg(target_statevec_qsphere, self.target_qsphere)
            self.canvas_tar_statevec.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5*scale, pady=5*scale)
            self.canvas_tar_statevec.draw()

    def get_next_statevector(self):   # Fix this
        if self.choice.get() == 'easy':
            if self.check_statevectors():
                # Reset the color of canvases
                self.plot_area.configure(background='grey95')
                self.player_state.configure(background='grey95')

                # Get the next state vector from the statevectors.py based on the difficulty chosen
                try:
                    self.statevec_index_easy += 1
                    self.get_statevecs_from_dict()

                    self.problem_num_easy.configure(text=f'Easy Questions Progress: {self.statevec_index_easy} of {len(statevector_easy)}')

                    if self.show_hint:
                        self.hint_button.invoke()
                except IndexError:
                    tk.messagebox.showinfo("Good Job!!", f"You have prepared all the quantum state vectors")

            else:
                tk.messagebox.showinfo("Can't proceed!", "Prepare the given target state before proceeding.")

        if self.choice.get() == 'advanced':
            if self.check_statevectors():
                # Reset the color of canvases
                self.plot_area.configure(background='grey95')
                self.player_state.configure(background='grey95')

                # Get the next state vector from the statevectors.py based on the difficulty chosen
                try:
                    self.statevec_index_advanced += 1
                    self.get_statevecs_from_dict()

                    self.problem_num_advanced.configure(text=f'Advanced Questions Progress: {self.statevec_index_advanced} of {len(self.statevector_advanced)}')

                    if self.show_hint:
                        self.hint_button.invoke()
                except IndexError:
                    tk.messagebox.showinfo("Good Job!!", f"You have prepared all the quantum state vectors")

            else:
                tk.messagebox.showinfo("Can't proceed!", "Prepare the given target state before proceeding.")

    def advanced_mode_statevector_dict(self):
        number_of_questions = 5
        advanced_dict = {key: [] for key in range(1, number_of_questions + 1)}

        for i in range(1, number_of_questions + 1):
            random_num_qubits = np.random.randint(2, 4)
            random_depth = np.random.randint(2, 5)

            # Add random (but nice) initial statevectors to the dictionary
            advanced_dict[i].append(self.run_circuit(random_circuit(random_num_qubits, 1)))  # depth=1

            # Add random target statevectors whose random initial state was generated above
            random_target_sv_circuit = random_circuit(random_num_qubits, random_depth, initial_state=advanced_dict[i][0])
            advanced_dict[i].append(self.run_circuit(random_target_sv_circuit))

            # From the random circuit generated for target statevector above extract names of the gates and instructions to create a hint
            random_circ_data = random_target_sv_circuit.data
            gates_list = [random_circ_data[j].operation.name for j in range(len(random_circ_data))]
            random.shuffle(gates_list)
            advanced_dict[i].append("Use the following gates: " + ", ".join(gates_list))

        return advanced_dict



def main():
    root = tk.Tk()
    test = PrepareTheState(root)
    root.mainloop()


if __name__ == "__main__":
    main()

