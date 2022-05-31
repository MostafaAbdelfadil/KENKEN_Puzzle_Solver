from ast import Constant
from math import prod
from xml import dom
import numpy as np
from random import randint
import random
import tkinter as tk
class Cell:
    def __init__(self, n, i, j, val=0):
        self.domain = set(range(1, n+1))
        self.val = val
        self.cooridnates = (i, j)
        self.cage = None

    def childs(self, board):
        childs = []
        row, col = self.cooridnates
        for j in range(len(board)):
            if (j != col) and (board[row][j] not in childs):
                childs.append(board[row][j])
        
        for j in range(len(board)):
            if (j != row) and (board[j][col] not in childs):
                childs.append(board[j][col])

        for cell in self.cage.cells:
            if (cell != self) and (cell not in childs):
                childs.append(cell)

        return childs
