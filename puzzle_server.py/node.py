# ==============================================================================
# node.py
#
# Define a estrutura de dados para um nó na árvore de busca.
# ==============================================================================

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
