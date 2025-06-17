import time
import random
import tkinter as tk
from tkinter import ttk, font
from collections import deque
import heapq
import threading

# --- ESTRUTURA DE DADOS PARA O NÓ DA ÁRVORE DE BUSCA (Inalterada) ---

class Node:
    """
    Representa um nó na árvore de busca.
    """
    def __init__(self, state, parent=None, action=None, cost=0, heuristic=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.heuristic = heuristic

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

    def __eq__(self, other):
        return self.state == other.state

# --- FUNÇÕES AUXILIARES E HEURÍSTICA (Inalteradas) ---

def get_goal_state(n):
    total_tiles = n * n
    goal = list(range(1, total_tiles))
    goal.append(0)
    return tuple(goal)

def get_possible_moves(state, n):
    empty_index = state.index(0)
    row, col = divmod(empty_index, n)
    moves = []
    if row > 0: moves.append('UP')
    if row < n - 1: moves.append('DOWN')
    if col > 0: moves.append('LEFT')
    if col < n - 1: moves.append('RIGHT')
    return moves

def apply_move(state, move, n):
    empty_index = state.index(0)
    new_state = list(state)
    if move == 'UP': swap_index = empty_index - n
    elif move == 'DOWN': swap_index = empty_index + n
    elif move == 'LEFT': swap_index = empty_index - 1
    elif move == 'RIGHT': swap_index = empty_index + 1
    new_state[empty_index], new_state[swap_index] = new_state[swap_index], new_state[empty_index]
    return tuple(new_state)

def manhattan_distance(state, goal, n):
    distance = 0
    for i, value in enumerate(state):
        if value != 0:
            goal_index = goal.index(value)
            current_row, current_col = divmod(i, n)
            goal_row, goal_col = divmod(goal_index, n)
            distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    return distance

def reconstruct_path(node):
    path = []
    while node:
        path.append({'state': node.state, 'action': node.action})
        node = node.parent
    return list(reversed(path))

def shuffle_board(goal_state, n):
    temp_state = goal_state
    shuffle_count = n * n * 15
    for _ in range(shuffle_count):
        move = random.choice(get_possible_moves(temp_state, n))
        temp_state = apply_move(temp_state, move, n)
    return temp_state

# --- ALGORITMOS DE BUSCA (Inalterados) ---

def breadth_first_search(initial_state, goal_state, n):
    frontier = deque([Node(initial_state)])
    explored = {initial_state}
    expanded_nodes = 0
    while frontier:
        node = frontier.popleft()
        expanded_nodes += 1
        if node.state == goal_state: return reconstruct_path(node), expanded_nodes
        for move in get_possible_moves(node.state, n):
            neighbor_state = apply_move(node.state, move, n)
            if neighbor_state not in explored:
                explored.add(neighbor_state)
                frontier.append(Node(neighbor_state, node, move, node.cost + 1))
    return None, expanded_nodes

def depth_first_search(initial_state, goal_state, n):
    frontier = [Node(initial_state)]
    explored = set()
    expanded_nodes = 0
    max_depth = n * n * n * 2
    while frontier:
        node = frontier.pop()
        expanded_nodes += 1
        if node.state in explored: continue
        explored.add(node.state)
        if node.state == goal_state: return reconstruct_path(node), expanded_nodes
        if node.cost > max_depth: continue
        for move in reversed(get_possible_moves(node.state, n)):
            neighbor_state = apply_move(node.state, move, n)
            frontier.append(Node(neighbor_state, node, move, node.cost + 1))
    return None, expanded_nodes

def a_star_search(initial_state, goal_state, n):
    h = manhattan_distance(initial_state, goal_state, n)
    frontier = [(h, Node(initial_state, heuristic=h))]
    explored = {initial_state: 0}
    expanded_nodes = 0
    while frontier:
        _, node = heapq.heappop(frontier)
        expanded_nodes += 1
        if node.state == goal_state: return reconstruct_path(node), expanded_nodes
        for move in get_possible_moves(node.state, n):
            neighbor_state = apply_move(node.state, move, n)
            new_cost = node.cost + 1
            if neighbor_state not in explored or new_cost < explored[neighbor_state]:
                explored[neighbor_state] = new_cost
                h_val = manhattan_distance(neighbor_state, goal_state, n)
                heapq.heappush(frontier, (new_cost + h_val, Node(neighbor_state, node, move, new_cost, h_val)))
    return None, expanded_nodes

def greedy_search(initial_state, goal_state, n):
    h = manhattan_distance(initial_state, goal_state, n)
    frontier = [(h, Node(initial_state, heuristic=h))]
    explored = set()
    expanded_nodes = 0
    while frontier:
        _, node = heapq.heappop(frontier)
        expanded_nodes += 1
        if node.state in explored: continue
        explored.add(node.state)
        if node.state == goal_state: return reconstruct_path(node), expanded_nodes
        for move in get_possible_moves(node.state, n):
            neighbor_state = apply_move(node.state, move, n)
            if neighbor_state not in explored:
                h_val = manhattan_distance(neighbor_state, goal_state, n)
                heapq.heappush(frontier, (h_val, Node(neighbor_state, node, move, node.cost + 1, h_val)))
    return None, expanded_nodes


# --- CLASSE DA INTERFACE GRÁFICA ---

class PuzzleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Resolvedor de N-Puzzle")
        self.geometry("600x750")
        self.configure(bg="#f0f0f0")

        self.n = 3
        self.goal_state = get_goal_state(self.n)
        self.current_state = self.goal_state
        self.tile_widgets = []
        self.is_busy = False

        # Estilos
        self.style = ttk.Style(self)
        self.style.configure("TButton", padding=6, relief="flat", font=('Helvetica', 10, 'bold'))
        self.style.configure("TLabel", background="#f0f0f0", font=('Helvetica', 10))
        self.style.configure("Header.TLabel", font=('Helvetica', 16, 'bold'))

        # --- Layout Principal ---
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de Controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 20))

        # Dropdown de Tamanho
        ttk.Label(controls_frame, text="Tamanho:").pack(side=tk.LEFT, padx=(0, 5))
        self.size_var = tk.StringVar(value=f"{self.n}x{self.n}")
        size_menu = ttk.OptionMenu(controls_frame, self.size_var, f"{self.n}x{self.n}", "3x3", "4x4", command=self.change_size)
        size_menu.pack(side=tk.LEFT, padx=5)

        # Dropdown de Algoritmo
        self.algorithms = {
            'A* (A-Star)': a_star_search,
            'Greedy Best-First': greedy_search,
            'Busca em Largura (BFS)': breadth_first_search,
            'Busca em Profundidade (DFS)': depth_first_search
        }
        ttk.Label(controls_frame, text="Algoritmo:").pack(side=tk.LEFT, padx=(20, 5))
        self.algo_var = tk.StringVar(value='A* (A-Star)')
        algo_menu = ttk.OptionMenu(controls_frame, self.algo_var, 'A* (A-Star)', *self.algorithms.keys())
        algo_menu.pack(side=tk.LEFT, padx=5)

        # Botões
        self.shuffle_button = ttk.Button(controls_frame, text="Embaralhar", command=self.shuffle)
        self.shuffle_button.pack(side=tk.RIGHT)
        self.solve_button = ttk.Button(controls_frame, text="Resolver", command=self.solve)
        self.solve_button.pack(side=tk.RIGHT, padx=5)
        
        # Frame do Tabuleiro
        self.board_frame = tk.Frame(main_frame, bg="#cccccc")
        self.board_frame.pack(fill=tk.BOTH, expand=True)
        
        # Área de Status e Resultados
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.X, pady=(20, 0))
        self.status_label = ttk.Label(results_frame, text="Bem-vindo! Escolha as opções e embaralhe.", font=('Helvetica', 11, 'italic'))
        self.status_label.pack()
        self.results_label = ttk.Label(results_frame, text="", justify=tk.LEFT, font=('Courier', 10))
        self.results_label.pack(pady=5)

        self.create_board_widgets()
        self.update_board_display()

    def create_board_widgets(self):
        # Limpa widgets antigos
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        self.tile_widgets = []
        
        # Cria novos widgets
        for i in range(self.n * self.n):
            tile_label = tk.Label(self.board_frame, text="", font=font.Font(size=24, weight='bold'), relief="raised", borderwidth=1)
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
        self.update_status(f"Tamanho mudado para {self.n}x{self.n}. Embaralhe o tabuleiro.")

    def set_busy(self, busy_status):
        self.is_busy = busy_status
        state = tk.DISABLED if busy_status else tk.NORMAL
        for child in self.winfo_children(): # Desabilita todos os widgets
             if isinstance(child, ttk.Frame):
                for sub_child in child.winfo_children():
                    if isinstance(sub_child, ttk.Frame):
                         for sub_sub_child in sub_child.winfo_children():
                              if 'state' in sub_sub_child.config():
                                   sub_sub_child.config(state=state)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.update_idletasks() # Força a atualização da UI

    def shuffle(self):
        if self.is_busy: return
        self.update_status("Embaralhando...")
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
        self.update_status("Resolvendo... Isso pode levar um momento.")
        self.results_label.config(text="")
        
        # Executa a busca em uma thread separada para não congelar a GUI
        solver_func = self.algorithms[self.algo_var.get()]
        thread = threading.Thread(target=self.run_search, args=(solver_func, self.current_state, self.goal_state, self.n))
        thread.start()

    def run_search(self, solver_func, initial_state, goal_state, n):
        start_time = time.time()
        result, expanded_nodes = solver_func(initial_state, goal_state, n)
        end_time = time.time()
        
        # Agenda a atualização da UI na thread principal
        self.after(0, self.on_search_complete, result, expanded_nodes, end_time - start_time)

    def on_search_complete(self, path, expanded_nodes, duration):
        if path:
            self.update_status("Solução encontrada! Animando o caminho...")
            results_text = (
                f"Tempo de execução: {duration:.4f} s\n"
                f"Custo do caminho: {len(path) - 1} movimentos\n"
                f"Nós expandidos: {expanded_nodes}"
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

        step = path.pop(0)
        self.current_state = step['state']
        self.update_board_display()
        
        # Agenda o próximo passo da animação
        self.after(200, self.animate_solution, path)

    # Função auxiliar para cores
    def hsv_to_rgb(self, h, s, v):
        import colorsys
        return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


if __name__ == "__main__":
    app = PuzzleGUI()
    app.mainloop()
