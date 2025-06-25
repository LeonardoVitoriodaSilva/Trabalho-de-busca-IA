# ==============================================================================
# RESOLVEDOR DE N-PUZZLE COM INTERFACE GRÁFICA
#
# Autor: Leonardo Vitorio e Mateus Vital
# Disciplina: Inteligência Artificial
#
# Este script implementa uma solução para o problema do N-Puzzle (8, 15, 24)
# utilizando algoritmos de busca cega e heurística, com uma interface
# gráfica construída em Tkinter.
# ==============================================================================

import time
import random
import tkinter as tk
from tkinter import ttk, font
from collections import deque
import heapq
import threading

# --- ESTRUTURA DE DADOS PARA O NÓ DA ÁRVORE DE BUSCA ---
# A classe Node é a base para todos os nossos algoritmos de busca.
# Cada nó representa um estado do tabuleiro e mantém informações essenciais
# para a busca, como o estado pai (para reconstruir o caminho), a ação
# que levou a este estado, e os custos associados.

class Node:
    """
    Representa um nó na árvore de busca.
    - state: A configuração (tupla) atual do tabuleiro.
    - parent: O nó que gerou o nó atual.
    - action: A ação (ex: 'UP', 'DOWN') que levou ao estado atual.
    - cost: O custo do caminho desde o nó inicial (profundidade, ou g(n)).
    - heuristic: O valor heurístico estimado até o objetivo (h(n)).
    """
    def __init__(self, state, parent=None, action=None, cost=0, heuristic=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.heuristic = heuristic

    # Método de comparação para a fila de prioridade (heapq) do A*.
    # Ele compara os nós com base em f(n) = g(n) + h(n).
    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

    # Método para verificar se dois nós representam o mesmo estado.
    def __eq__(self, other):
        return self.state == other.state

# --- FUNÇÕES AUXILIARES E HEURÍSTICA ---
# Este bloco contém funções de suporte que são usadas em todo o programa,
# desde a geração do tabuleiro até o cálculo da heurística.

def get_goal_state(n):
    """Gera o estado final (resolvido) para um puzzle de tamanho n x n."""
    total_tiles = n * n
    goal = list(range(1, total_tiles))
    goal.append(0)  # O 0 representa o espaço vazio no final.
    return tuple(goal) # Usamos tuplas para que os estados possam ser usados como chaves em dicionários/sets.

def get_possible_moves(state, n):
    """Retorna uma lista de movimentos possíveis ('UP', 'DOWN', etc.) para o espaço vazio."""
    empty_index = state.index(0)
    row, col = divmod(empty_index, n) # Encontra a posição (linha, coluna) do espaço vazio.
    moves = []
    if row > 0: moves.append('UP')
    if row < n - 1: moves.append('DOWN')
    if col > 0: moves.append('LEFT')
    if col < n - 1: moves.append('RIGHT')
    return moves

def apply_move(state, move, n):
    """Aplica um movimento a um estado e retorna o novo estado resultante."""
    empty_index = state.index(0)
    new_state = list(state)
    
    # Encontra o índice da peça a ser trocada com o espaço vazio.
    if move == 'UP': swap_index = empty_index - n
    elif move == 'DOWN': swap_index = empty_index + n
    elif move == 'LEFT': swap_index = empty_index - 1
    elif move == 'RIGHT': swap_index = empty_index + 1
    
    # Realiza a troca.
    new_state[empty_index], new_state[swap_index] = new_state[swap_index], new_state[empty_index]
    return tuple(new_state)

def manhattan_distance(state, goal, n):
    """
    Calcula a heurística da Distância de Manhattan.
    É a soma das distâncias (vertical + horizontal) de cada peça
    de sua posição atual até sua posição final.
    É uma heurística admissível, ou seja, nunca superestima o custo real.
    """
    distance = 0
    for i, value in enumerate(state):
        if value != 0: # Ignoramos o espaço vazio.
            goal_index = goal.index(value)
            current_row, current_col = divmod(i, n)
            goal_row, goal_col = divmod(goal_index, n)
            distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    return distance

def reconstruct_path(node):
    """
    Percorre a árvore de "pais" a partir do nó final para reconstruir
    o caminho da solução.
    """
    path = []
    while node:
        path.append({'state': node.state, 'action': node.action})
        node = node.parent
    return list(reversed(path)) # Invertemos para ter o caminho do início ao fim.

def shuffle_board(goal_state, n):
    """
    Embaralha o tabuleiro realizando movimentos aleatórios a partir do estado final.
    Isso garante que todo puzzle gerado seja solucionável.
    """
    temp_state = goal_state
    shuffle_count = n * n * 15 # Número de movimentos aleatórios.
    for _ in range(shuffle_count):
        move = random.choice(get_possible_moves(temp_state, n))
        temp_state = apply_move(temp_state, move, n)
    return temp_state

# --- ALGORITMOS DE BUSCA ---
# Aqui estão as implementações dos quatro algoritmos de busca.

def breadth_first_search(initial_state, goal_state, n):
    """Busca em Largura (BFS): Usa uma fila (FIFO) para explorar a árvore nível por nível."""
    frontier = deque([Node(initial_state)])
    explored = {initial_state}
    expanded_nodes = 0
    while frontier:
        node = frontier.popleft() # Pega o primeiro da fila.
        expanded_nodes += 1
        if node.state == goal_state: return reconstruct_path(node), expanded_nodes
        for move in get_possible_moves(node.state, n):
            neighbor_state = apply_move(node.state, move, n)
            if neighbor_state not in explored:
                explored.add(neighbor_state)
                frontier.append(Node(neighbor_state, node, move, node.cost + 1))
    return None, expanded_nodes

def depth_first_search(initial_state, goal_state, n):
    """Busca em Profundidade (DFS): Usa uma pilha (LIFO) para explorar um caminho até o fim."""
    frontier = [Node(initial_state)] # A lista funciona como uma pilha com .pop() e .append().
    explored = set()
    expanded_nodes = 0
    max_depth = n * n * n * 2 # Limite para evitar caminhos infinitos em puzzles grandes.
    while frontier:
        node = frontier.pop() # Pega o último da pilha.
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
    """Busca A* (A-Star): Usa uma fila de prioridade para expandir o nó com menor f(n) = g(n) + h(n)."""
    h = manhattan_distance(initial_state, goal_state, n)
    frontier = [(h, Node(initial_state, heuristic=h))] # A fila de prioridade (heap) armazena (prioridade, nó).
    explored = {initial_state: 0} # Armazena o custo para chegar a cada estado explorado.
    expanded_nodes = 0
    while frontier:
        _, node = heapq.heappop(frontier) # Pega o nó com menor prioridade (menor f(n)).
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
    """Busca Gulosa (Greedy Best-First): Similar ao A*, mas prioriza apenas pela heurística h(n)."""
    h = manhattan_distance(initial_state, goal_state, n)
    frontier = [(h, Node(initial_state, heuristic=h))]
    explored = set()
    expanded_nodes = 0
    while frontier:
        _, node = heapq.heappop(frontier) # Pega o nó com menor heurística.
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


# --- CLASSE DA INTERFACE GRÁFICA (VERSÃO MELHORADA) ---
# Esta classe gerencia toda a parte visual e a interação com o usuário usando a biblioteca Tkinter.
# Foi reestruturada para ter uma aparência mais moderna e organizada.

class PuzzleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        # Configuração inicial da janela principal.
        self.title("Resolvedor de N-Puzzle")
        self.geometry("650x800")
        
        # Paleta de cores para a interface.
        self.COLORS = {
            "bg": "#2E2E2E",
            "bg_light": "#3C3C3C",
            "fg": "#E0E0E0",
            "primary": "#007ACC",
            "success": "#28A745",
            "error": "#DC3545",
            "info": "#17A2B8",
            "tile_empty": "#4A4A4A",
        }
        self.configure(bg=self.COLORS["bg"])

        # Variáveis de estado da aplicação.
        self.n = 3
        self.goal_state = get_goal_state(self.n)
        self.current_state = self.goal_state
        self.tile_widgets = []
        self.is_busy = False # Flag para desabilitar botões durante o processamento.

        # --- Estilos ---
        self.style = ttk.Style(self)
        self.style.theme_use('clam') # Tema mais moderno
        self.style.configure("TFrame", background=self.COLORS["bg"])
        self.style.configure("TLabel", background=self.COLORS["bg"], foreground=self.COLORS["fg"], font=('Segoe UI', 10))
        self.style.configure("TLabelframe", background=self.COLORS["bg"], bordercolor=self.COLORS["primary"])
        self.style.configure("TLabelframe.Label", background=self.COLORS["bg"], foreground=self.COLORS["fg"], font=('Segoe UI', 11, 'bold'))
        self.style.configure("TButton", padding=8, relief="flat", font=('Segoe UI', 10, 'bold'), background=self.COLORS["primary"], foreground="white")
        self.style.map("TButton", background=[('active', self.COLORS["info"])])
        self.style.configure("TCombobox", padding=5)

        # --- Layout Principal ---
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Secção de Configurações ---
        settings_frame = ttk.Labelframe(main_frame, text="Configurações", padding="15")
        settings_frame.pack(fill=tk.X)
        
        # Controles dentro da secção
        settings_grid = ttk.Frame(settings_frame)
        settings_grid.pack(fill=tk.X)
        settings_grid.columnconfigure(1, weight=1)
        settings_grid.columnconfigure(3, weight=1)

        ttk.Label(settings_grid, text="Tamanho:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.size_var = tk.StringVar(value=f"{self.n}x{self.n}")
        size_menu = ttk.Combobox(settings_grid, textvariable=self.size_var, values=["3x3", "4x4", "5x5"], state="readonly")
        size_menu.grid(row=0, column=1, padx=5, sticky="ew")
        size_menu.bind("<<ComboboxSelected>>", self.change_size)

        ttk.Label(settings_grid, text="Algoritmo:").grid(row=0, column=2, padx=(20, 5), sticky="w")
        self.algorithms = { 'A* (A-Star)': a_star_search, 'Greedy Best-First': greedy_search, 'Busca em Largura (BFS)': breadth_first_search, 'Busca em Profundidade (DFS)': depth_first_search }
        self.algo_var = tk.StringVar(value='A* (A-Star)')
        algo_menu = ttk.Combobox(settings_grid, textvariable=self.algo_var, values=list(self.algorithms.keys()), state="readonly")
        algo_menu.grid(row=0, column=3, padx=5, sticky="ew")

        # --- Botões de Ação ---
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=15)
        self.solve_button = ttk.Button(buttons_frame, text="Resolver", command=self.solve)
        self.solve_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5,0))
        self.shuffle_button = ttk.Button(buttons_frame, text="Embaralhar", command=self.shuffle)
        self.shuffle_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(0,5))
        
        # --- Tabuleiro ---
        self.board_frame = tk.Frame(main_frame, bg=self.COLORS["bg_light"], relief="sunken", borderwidth=2)
        self.board_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # --- Secção de Resultados e Status ---
        results_frame = ttk.Labelframe(main_frame, text="Status", padding="15")
        results_frame.pack(fill=tk.X)
        self.status_label = ttk.Label(results_frame, text="Bem-vindo! Escolha as opções e embaralhe.", font=('Segoe UI', 11, 'italic'))
        self.status_label.pack(fill=tk.X)
        self.progress_bar = ttk.Progressbar(results_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        self.results_label = ttk.Label(results_frame, text="", justify=tk.LEFT, font=('Courier New', 10))
        self.results_label.pack(fill=tk.X, pady=5)
        
        self.center_window()
        self.create_board_widgets()
        self.update_board_display()

    def center_window(self):
        """Centraliza a janela principal no ecrã."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_board_widgets(self):
        """Cria ou recria os widgets (labels) para cada peça do tabuleiro."""
        for widget in self.board_frame.winfo_children():
            widget.destroy() # Limpa widgets antigos ao mudar de tamanho.
        self.tile_widgets = []
        
        font_size = max(12, 40 - 7 * self.n) # Tamanho da fonte se ajusta ao tamanho do puzzle.
        tile_font = font.Font(family='Segoe UI', size=font_size, weight='bold')
        
        for i in range(self.n * self.n):
            tile_label = tk.Label(self.board_frame, text="", font=tile_font, relief="raised", borderwidth=2, anchor="center")
            self.tile_widgets.append(tile_label)
            row, col = divmod(i, self.n)
            self.board_frame.grid_rowconfigure(row, weight=1) # Faz as células expandirem.
            self.board_frame.grid_columnconfigure(col, weight=1)
            tile_label.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
            
    def update_board_display(self):
        """Atualiza o texto e a cor de cada peça na tela com base no estado atual."""
        for i, value in enumerate(self.current_state):
            widget = self.tile_widgets[i]
            if value == 0:
                widget.config(text="", bg=self.COLORS["tile_empty"], relief="flat")
            else:
                hue = (value * 15) % 360
                bg_color = f'#%02x%02x%02x' % self.hsv_to_rgb(hue/360, 0.6, 0.9)
                fg_color = self.COLORS["fg"]
                widget.config(text=str(value), bg=bg_color, fg=fg_color, relief="raised")

    def change_size(self, event=None):
        """Chamada quando o usuário muda o tamanho do puzzle no menu."""
        if self.is_busy: return
        choice = self.size_var.get()
        self.n = int(choice[0])
        self.goal_state = get_goal_state(self.n)
        self.current_state = self.goal_state
        self.create_board_widgets()
        self.update_board_display()
        if self.n == 5:
            self.update_status(f"Aviso: 5x5 pode ser muito lento para resolver!", 'info')
        else:
            self.update_status(f"Tamanho alterado para {self.n}x{self.n}. Embaralhe o tabuleiro.", 'info')

    def set_busy(self, busy_status):
        """Desabilita/habilita os controles da interface para evitar ações do usuário durante o processamento."""
        self.is_busy = busy_status
        state = tk.DISABLED if busy_status else tk.NORMAL
        
        # Desabilita botões e menus
        self.shuffle_button.config(state=state)
        self.solve_button.config(state=state)
        for w in self.winfo_children()[0].winfo_children()[0].winfo_children()[0].winfo_children():
             if isinstance(w, ttk.Combobox):
                 w.config(state=state)

        # Controla a barra de progresso
        if busy_status:
            self.progress_bar.start(10)
        else:
            self.progress_bar.stop()

    def update_status(self, message, status_type='info'):
        """Atualiza a mensagem na label de status com cores diferentes."""
        color = self.COLORS.get(status_type, self.COLORS["info"])
        self.status_label.config(text=message, foreground=color)
        self.update_idletasks() # Força a atualização da UI imediatamente.

    def shuffle(self):
        """Inicia o embaralhamento do tabuleiro."""
        if self.is_busy: return
        self.update_status("A embaralhar...", 'info')
        self.results_label.config(text="") # Limpa resultados antigos.
        self.current_state = shuffle_board(self.goal_state, self.n)
        self.update_board_display()
        self.update_status("Tabuleiro pronto. Clique em 'Resolver'.", 'success')

    def solve(self):
        """Inicia o processo de resolução do puzzle."""
        if self.is_busy: return
        if self.current_state == self.goal_state:
            self.update_status("O tabuleiro já está resolvido!", 'success')
            return
            
        self.set_busy(True)
        self.update_status("A resolver... Isto pode demorar um momento.", 'info')
        self.results_label.config(text="")
        
        # O algoritmo de busca é executado em uma thread separada para não congelar a interface.
        solver_func = self.algorithms[self.algo_var.get()]
        thread = threading.Thread(target=self.run_search, args=(solver_func, self.current_state, self.goal_state, self.n), daemon=True)
        thread.start()

    def run_search(self, solver_func, initial_state, goal_state, n):
        """Função que executa a busca na thread secundária."""
        start_time = time.time()
        result, expanded_nodes = solver_func(initial_state, goal_state, n)
        end_time = time.time()
        
        # Após a conclusão, agenda a função 'on_search_complete' para ser executada na thread principal da GUI.
        # Isso é crucial para atualizar a UI de forma segura.
        self.after(0, self.on_search_complete, result, expanded_nodes, end_time - start_time)

    def on_search_complete(self, path, expanded_nodes, duration):
        """Executada na thread principal após a busca terminar. Processa os resultados."""
        self.set_busy(False)
        if path:
            self.update_status("Solução encontrada! A animar o caminho...", 'success')
            results_text = (
                f"Tempo de execução: {duration:.4f} s\n"
                f"Custo do caminho: {len(path) - 1} movimentos\n"
                f"Nós expandidos: {expanded_nodes:,}" # Formata o número com vírgulas.
            )
            self.results_label.config(text=results_text)
            self.animate_solution(path) # Inicia a animação da solução.
        else:
            self.update_status("Não foi possível encontrar uma solução.", 'error')

    def animate_solution(self, path):
        """Anima a solução passo a passo, atualizando o tabuleiro a cada movimento."""
        if not path: # Se o caminho terminou.
            self.update_status("Animação concluída!", 'success')
            self.set_busy(False) # Libera os controles.
            return
        
        self.set_busy(True) # Garante que nada possa ser clicado durante a animação.
        step = path.pop(0)
        self.current_state = step['state']
        self.update_board_display()
        
        # Agenda a próxima chamada a esta função após um pequeno intervalo (150ms).
        self.after(150, self.animate_solution, path)

    def hsv_to_rgb(self, h, s, v):
        """Função auxiliar para converter cores do espaço HSV para RGB."""
        import colorsys
        return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


# --- PONTO DE ENTRADA DO PROGRAMA ---
# Este é o ponto inicial que cria a instância da nossa interface gráfica e a executa.
if __name__ == "__main__":
    app = PuzzleGUI()
    app.mainloop() # Inicia o loop de eventos do Tkinter.
