# ==============================================================================
# gui.py
#
# Contém a classe PuzzleGUI, responsável por toda a interface gráfica
# e interação com o usuário, construída com Tkinter.
# ==============================================================================

import time
import tkinter as tk
from tkinter import ttk, font
import threading
from utils import get_goal_state, shuffle_board, manhattan_distance, misplaced_tiles_heuristic
from algorithms import a_star_search, greedy_search, breadth_first_search, depth_first_search, iterative_deepening_search

class PuzzleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Resolvedor de N-Puzzle")
        self.geometry("750x800")
        self.configure(bg="#f0f0f0")

        self.n = 3
        self.goal_state = get_goal_state(self.n)
        self.current_state = self.goal_state
        self.tile_widgets = []
        self.is_busy = False

        self.style = ttk.Style(self)
        self.style.configure("TButton", padding=6, relief="flat", font=('Helvetica', 10, 'bold'))
        self.style.configure("TLabel", background="#f0f0f0", font=('Helvetica', 10))
        self.style.configure("Header.TLabel", font=('Helvetica', 16, 'bold'))

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Frame de Controles ---
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Linha 1 de Controles (Tamanho e Algoritmo)
        line1_frame = ttk.Frame(controls_frame)
        line1_frame.pack(fill=tk.X)
        ttk.Label(line1_frame, text="Tamanho:").pack(side=tk.LEFT, padx=(0, 5))
        self.size_var = tk.StringVar(value=f"{self.n}x{self.n}")
        self.size_menu = ttk.OptionMenu(line1_frame, self.size_var, f"{self.n}x{self.n}", "3x3", "4x4", "5x5", command=self.change_size)
        self.size_menu.pack(side=tk.LEFT, padx=5)

        self.algorithms = {
            'A* (A-Star)': a_star_search,
            'Greedy Best-First': greedy_search,
            'Busca em Largura (BFS)': breadth_first_search,
            'Busca em Profundidade (DFS)': depth_first_search,
            'Aprofundamento Iterativo (IDS)': iterative_deepening_search
        }
        ttk.Label(line1_frame, text="Algoritmo:").pack(side=tk.LEFT, padx=(20, 5))
        self.algo_var = tk.StringVar(value='A* (A-Star)')
        self.algo_menu = ttk.OptionMenu(line1_frame, self.algo_var, 'A* (A-Star)', *self.algorithms.keys(), command=self.on_algo_change)
        self.algo_menu.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Linha 2 de Controles (Heurísticas)
        line2_frame = ttk.Frame(controls_frame)
        line2_frame.pack(fill=tk.X, pady=(10,0))
        self.heuristics = {
            'Distância de Manhattan': manhattan_distance,
            'Peças Fora do Lugar': misplaced_tiles_heuristic
        }
        self.heuristic_label = ttk.Label(line2_frame, text="Heurística:")
        self.heuristic_var = tk.StringVar(value='Distância de Manhattan')
        self.heuristic_menu = ttk.OptionMenu(line2_frame, self.heuristic_var, 'Distância de Manhattan', *self.heuristics.keys())
        
        # Botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 20))
        self.shuffle_button = ttk.Button(buttons_frame, text="Embaralhar", command=self.shuffle)
        self.shuffle_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))
        self.solve_button = ttk.Button(buttons_frame, text="Resolver", command=self.solve)
        self.solve_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5,0))
        
        self.board_frame = tk.Frame(main_frame, bg="#cccccc")
        self.board_frame.pack(fill=tk.BOTH, expand=True)
        
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.X, pady=(20, 0))
        self.status_label = ttk.Label(results_frame, text="Bem-vindo! Escolha as opções e embaralhe.", font=('Helvetica', 11, 'italic'))
        self.status_label.pack()
        self.results_label = ttk.Label(results_frame, text="", justify=tk.LEFT, font=('Courier', 10))
        self.results_label.pack(pady=5)

        self.create_board_widgets()
        self.update_board_display()
        self.on_algo_change()

    def on_algo_change(self, *args):
        """Habilita/desabilita o menu de heurística com base no algoritmo selecionado."""
        algo = self.algo_var.get()
        if algo in ['A* (A-Star)', 'Greedy Best-First']:
            self.heuristic_label.pack(side=tk.LEFT, padx=(0, 5))
            self.heuristic_menu.pack(side=tk.LEFT, expand=True, fill=tk.X)
        else:
            self.heuristic_label.pack_forget()
            self.heuristic_menu.pack_forget()

    def create_board_widgets(self):
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        self.tile_widgets = []
        font_size = max(12, 36 - 6 * self.n)
        for i in range(self.n * self.n):
            tile_label = tk.Label(self.board_frame, text="", font=font.Font(size=font_size, weight='bold'), relief="raised", borderwidth=1)
            self.tile_widgets.append(tile_label)
            row, col = divmod(i, self.n)
            self.board_frame.grid_rowconfigure(row, weight=1)
            self.board_frame.grid_columnconfigure(col, weight=1)
            tile_label.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            
    def update_board_display(self):
        for i, value in enumerate(self.current_state):
            widget = self.tile_widgets[i]
            if value == 0:
                widget.config(text="", bg="#cccccc", relief="flat")
            else:
                hue = (value * 360 / (self.n * self.n)) % 360
                bg_color = f'#%02x%02x%02x' % self.hsv_to_rgb(hue/360, 0.7, 0.95)
                fg_color = f'#%02x%02x%02x' % self.hsv_to_rgb(hue/360, 0.9, 0.4)
                widget.config(text=str(value), bg=bg_color, fg=fg_color, relief="raised")

    def change_size(self, choice):
        if self.is_busy: return
        self.n = int(choice[0])
        self.goal_state = get_goal_state(self.n)
        self.current_state = self.goal_state
        self.create_board_widgets()
        self.update_board_display()
        self.update_status(f"Tamanho alterado para {self.n}x{self.n}. Embaralhe o tabuleiro.")

    def set_busy(self, busy_status):
        self.is_busy = busy_status
        state = tk.DISABLED if busy_status else tk.NORMAL
        self.shuffle_button.config(state=state)
        self.solve_button.config(state=state)
        self.size_menu.config(state=state)
        self.algo_menu.config(state=state)
        self.heuristic_menu.config(state=state)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.update_idletasks()

    def shuffle(self):
        if self.is_busy: return
        self.update_status("A embaralhar...")
        self.results_label.config(text="")
        self.current_state = shuffle_board(self.goal_state, self.n)
        self.update_board_display()
        self.update_status("Tabuleiro pronto. Clique em 'Resolver'.")

    def solve(self):
        if self.is_busy: return
        if self.current_state == self.goal_state:
            self.update_status("O tabuleiro já está resolvido!")
            return
            
        self.set_busy(True)
        self.update_status("A resolver... Isto pode demorar um momento.")
        self.results_label.config(text="")
        
        solver_func = self.algorithms[self.algo_var.get()]
        heuristic_func = self.heuristics.get(self.heuristic_var.get())
        
        thread = threading.Thread(target=self.run_search, args=(solver_func, self.current_state, self.goal_state, self.n, heuristic_func), daemon=True)
        thread.start()

    def run_search(self, solver_func, initial_state, goal_state, n, heuristic_func):
        start_time = time.time()
        result, expanded_nodes = solver_func(initial_state, goal_state, n, heuristic_func)
        end_time = time.time()
        
        self.after(0, self.on_search_complete, result, expanded_nodes, end_time - start_time)

    def on_search_complete(self, path, expanded_nodes, duration):
        if path:
            self.update_status("Solução encontrada! A animar o caminho...")
            results_text = (
                f"Tempo de execução: {duration:.4f} s\n"
                f"Custo do caminho: {len(path) - 1} movimentos\n"
                f"Nós expandidos: {expanded_nodes:,}"
            )
            self.results_label.config(text=results_text)
            self.animate_solution(path)
        else:
            self.update_status("Não foi possível encontrar uma solução.")
            self.set_busy(False)

    def animate_solution(self, path):
        if not path:
            self.update_status("Animação concluída!")
            self.set_busy(False)
            return
        
        self.set_busy(True)
        step = path.pop(0)
        self.current_state = step['state']
        self.update_board_display()
        
        self.after(200, self.animate_solution, path)

    def hsv_to_rgb(self, h, s, v):
        import colorsys
        return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))
