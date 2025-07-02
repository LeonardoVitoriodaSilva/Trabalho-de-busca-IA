# ==============================================================================
# utils.py
#
# Contém funções auxiliares para a lógica do N-Puzzle, como manipulação
# de estados, cálculo de heurística e reconstrução de caminho.
# ==============================================================================

import random

def get_goal_state(n):
    """Gera o estado final (resolvido) para um puzzle de tamanho n x n."""
    total_tiles = n * n
    goal = list(range(1, total_tiles))
    goal.append(0)
    return tuple(goal)

def get_possible_moves(state, n):
    """Retorna uma lista de movimentos possíveis ('UP', 'DOWN', etc.) para o espaço vazio."""
    empty_index = state.index(0)
    row, col = divmod(empty_index, n)
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
    
    if move == 'UP': swap_index = empty_index - n
    elif move == 'DOWN': swap_index = empty_index + n
    elif move == 'LEFT': swap_index = empty_index - 1
    elif move == 'RIGHT': swap_index = empty_index + 1
    
    new_state[empty_index], new_state[swap_index] = new_state[swap_index], new_state[empty_index]
    return tuple(new_state)

def manhattan_distance(state, goal, n):
    """Calcula a heurística da Distância de Manhattan."""
    distance = 0
    for i, value in enumerate(state):
        if value != 0:
            goal_index = goal.index(value)
            current_row, current_col = divmod(i, n)
            goal_row, goal_col = divmod(goal_index, n)
            distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    return distance

def misplaced_tiles_heuristic(state, goal, n):
    """
    Calcula a heurística do número de peças fora do lugar.
    Conta quantas peças não estão na sua posição final.
    """
    misplaced = 0
    for i in range(len(state)):
        if state[i] != 0 and state[i] != goal[i]:
            misplaced += 1
    return misplaced

def reconstruct_path(node):
    """Reconstrói o caminho da solução a partir do nó final."""
    path = []
    while node:
        path.append({'state': node.state, 'action': node.action})
        node = node.parent
    return list(reversed(path))

def shuffle_board(goal_state, n):
    """Embaralha o tabuleiro a partir do estado final para garantir que seja solucionável."""
    temp_state = goal_state
    shuffle_count = n * n * 15
    for _ in range(shuffle_count):
        move = random.choice(get_possible_moves(temp_state, n))
        temp_state = apply_move(temp_state, move, n)
    return temp_state
