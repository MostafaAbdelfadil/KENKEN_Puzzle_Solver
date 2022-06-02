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
    
class KenKen:
    '''
    KenKen board class.
    call KenKen(n) to randomly generate n x n kenken board
    '''
    def __init__(self, n):
        self.size = n
        self.board = self.generate()

    def generate(self):
        '''Generate a random KenKen board'''
        n = self.size
        #init values
        values = np.ones((n,n), dtype=np.int32)
        board = [] #2d list of cell objects

        #generate latin square
        for i in range(n):
            board.append([])
            for j in range(n):
                values[i][j] = ((i+j) % n) + 1
                board[i].append(Cell(n, i, j))

        
        #shuffle
        np.random.shuffle(values)
        values = values.T
        np.random.shuffle(values)
        self._solution = values
        #cage construction
        cage_ids = np.zeros_like(values, dtype=np.int32) 
        def get_empties(i,j):
            empties = []
            #get possible top
            if i != 0 and  cage_ids[i-1][j] == 0: empties.append((i-1,j))
            #get possible bottom
            if i != self.size-1 and  cage_ids[i+1][j] == 0: empties.append((i+1,j))
            #get possible right
            if j != self.size-1 and cage_ids[i][j+1] == 0: empties.append((i,j+1))
            #get possible left
            if j != 0 and cage_ids[i][j-1] == 0: empties.append((i,j-1))
            return empties
        
        id= 0 #id of cage
        cage_size_range = [1]*2 + [2,3,4]*3 if n > 3 else [1]*2 + [2,3]*3
        while np.count_nonzero(cage_ids == 0) > 0:
            id += 1
            #get first uncaged cell
            idx = np.argmin(cage_ids)
            #convert it to 2d
            i, j = idx // n, idx % n
            cage_ids[i][j] = id
            #get cage size
            cage_size = random.choice(cage_size_range)
            #assign cells to cage
            for _ in range(cage_size-1):
                empties = get_empties(i,j)
                if empties == []: break
                #direction = randint(0,len(empties)-1)
                #i, j = empties[direction]
                i, j = random.choice(empties)
                cage_ids[i][j] = id
        
        #creating cage objects and assigning goals and operations
        unary = '='
        binary = ['-', '/', '+', '*']
        n_ary = ['+', '*']
        cage_objects = []
        for i in range(1,id+1):
            cage_values = values[cage_ids==i]

            if len(cage_values) == 1: 
                cage_objects.append(Cage(op=unary, goal=cage_values[0]))
                continue

            if len(cage_values) == 2:
                op = random.choice(binary)
                cage_objects.append(Cage(op=op))
                #switch operation if division gives remainder
                if op == '-' or (op == '/' and max(cage_values) % min(cage_values) != 0):
                    cage_objects[-1].op = '-'
                    cage_objects[-1].goal = abs(cage_values[0] - cage_values[1])
                elif op == '+':
                    cage_objects[-1].goal = sum(cage_values)
                elif op == '/':
                    cage_objects[-1].goal = max(cage_values) // min(cage_values)
                else:
                    cage_objects[-1].goal = int(np.prod(cage_values))
                continue
            
            op = random.choice(n_ary)
            if op == '+': cage_objects.append(Cage(op=op, goal=np.sum(cage_values)))
            else: cage_objects.append(Cage(op=op, goal=int(np.prod(cage_values))))

        #assigning cells to cages and cages to cells
        for i in range(n):
            for j in range(n):
                t = cage_ids[i][j]-1
                board[i][j].cage = cage_objects[cage_ids[i][j]-1]
                cage_objects[cage_ids[i][j]-1].cells.append(board[i][j])
        
        return board

    def backtrack(self, show=False):
        '''Solves the KenKen board with backtracking algorithm'''
        X = self.get_empty()
        if X is None: return True
        for v in X.domain:
            X.val = v
            if show: self.show_board()
            if self.is_valid(X):
                result = self.backtrack(show=show)
                if result: return True
            X.val = 0
        return False
