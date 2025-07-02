# ==============================================================================
# algorithms.py
#
# Implementa os algoritmos de busca para resolver o N-Puzzle.
# ==============================================================================

from collections import deque
import heapq
from node import Node
from utils import get_possible_moves, apply_move, manhattan_distance, reconstruct_path

def breadth_first_search(initial_state, goal_state, n, heuristic_func=None):
    """Busca em Largura (BFS): Usa uma fila (FIFO) para explorar a árvore nível por nível."""
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

def depth_first_search(initial_state, goal_state, n, heuristic_func=None):
    """Busca em Profundidade (DFS): Usa uma pilha (LIFO) para explorar um caminho até o fim."""
    frontier = [Node(initial_state)]
    explored = set()
    expanded_nodes = 0
    max_depth = n * n * 2
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

def depth_limited_search(node, goal_state, n, limit, expanded_nodes_ref):
    """Função auxiliar para o IDS: realiza uma busca em profundidade com um limite."""
    expanded_nodes_ref[0] += 1
    if node.state == goal_state:
        return reconstruct_path(node)
    elif limit == 0:
        return 'cutoff'
    else:
        cutoff_occurred = False
        for move in get_possible_moves(node.state, n):
            child_state = apply_move(node.state, move, n)
            child_node = Node(child_state, node, move, node.cost + 1)
            result = depth_limited_search(child_node, goal_state, n, limit - 1, expanded_nodes_ref)
            if result == 'cutoff':
                cutoff_occurred = True
            elif result is not None:
                return result
        return 'cutoff' if cutoff_occurred else None

def iterative_deepening_search(initial_state, goal_state, n, heuristic_func=None):
    """Busca com Aprofundamento Iterativo (IDS)."""
    expanded_nodes = 0
    for depth in range(100):
        expanded_nodes_ref = [0]
        root_node = Node(initial_state)
        result = depth_limited_search(root_node, goal_state, n, depth, expanded_nodes_ref)
        expanded_nodes += expanded_nodes_ref[0]
        if result != 'cutoff':
            return result, expanded_nodes
    return None, expanded_nodes

def a_star_search(initial_state, goal_state, n, heuristic_func=manhattan_distance):
    """Busca A* (A-Star): Usa uma fila de prioridade para expandir o nó com menor f(n) = g(n) + h(n)."""
    h = heuristic_func(initial_state, goal_state, n)
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
                h_val = heuristic_func(neighbor_state, goal_state, n)
                heapq.heappush(frontier, (new_cost + h_val, Node(neighbor_state, node, move, new_cost, h_val)))
    return None, expanded_nodes

def greedy_search(initial_state, goal_state, n, heuristic_func=manhattan_distance):
    """Busca Gulosa (Greedy Best-First): Similar ao A*, mas prioriza apenas pela heurística h(n)."""
    h = heuristic_func(initial_state, goal_state, n)
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
                h_val = heuristic_func(neighbor_state, goal_state, n)
                heapq.heappush(frontier, (h_val, Node(neighbor_state, node, move, node.cost + 1, h_val)))
    return None, expanded_nodes
