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
# ==============================================================================
# main.py
#
# Ponto de entrada principal da aplicação.
# Este script inicia a interface gráfica do resolvedor de N-Puzzle.
# ==============================================================================

from gui import PuzzleGUI

if __name__ == "__main__":
    app = PuzzleGUI()
    app.mainloop()
