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

        
class Cage:
    def __init__(self, cells=None, op=None, goal=None):
        self.cells = [] if cells==None else cells
        self.op = op
        self.goal = goal
        if cells is not None: self.assign_cages()

    def assign_cages(self):
        for cell in self.cells:
            cell.cage = self

    def check_constraint(self):
        if self.op == '+': return self.check_add()
        if self.op == '-': return self.check_subtract()
        if self.op == '*': return self.check_multiply()
        if self.op == '/': return self.check_divide()
        if self.op == '=': return self.cells[0].val == self.goal
    
    def check_add(self):
        res = sum([c.val for c in self.cells])
        return res <= self.goal

    def check_subtract(self):
        v1 = self.cells[0].val
        v2 = self.cells[1].val
        #cage still empty
        if v1 == 0 or v2 == 0: return True
        return abs(v1-v2) == self.goal

    def check_multiply(self):
        res = prod([c.val for c in self.cells if c.val!=0])
        return res <= self.goal

    def check_divide(self):
        v1 = self.cells[0].val
        v2 = self.cells[1].val
        maxi, mini = max(v1,v2), min(v1,v2)
        #cage still empty
        if v1 == 0 or v2 == 0: return True
        if maxi % mini != 0: return False
        return maxi // mini == self.goal

    
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

    def show_cages(self):
        '''Shows the empty KenKen board with the cage constraints'''
        j=0
        i=0
        for roww in self.board:
            col=[]
            for element in roww:
                
                col.append(str(element.cage.goal)+element.cage.op)

                e=tk.Entry(window,width=20, fg='blue',
                            font=('Arial',16,'bold'))
                e.grid(row=i, column=j)
                    
                e.insert(tk.END, col[j])  
                j+=1
            j=0 
            i+=1 

    def get_empty(self):
        '''Get the next empty cell in board'''
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j].val == 0: return self.board[i][j]
        return None

    def forward_check(self, var_domains, show=False):
        '''Solves the KenKen board with backtracking with forward checking algorithm'''

        for i in var_domains:
            for j in i:
                if len(j) == 0:
                    return False
        current = var_domains.copy()
        X = self.get_empty()
        if X is None: return True
        for v in current[X.cooridnates[0]][X.cooridnates[1]]:
            X.val = v
            post_domain = self.update_domains(var_domains=current, X=X)
            if show: self.show_board()
            result = self.forward_check(var_domains=post_domain.copy(), show=show)
            if result:
                return True
            X.val = 0
        return False

    def is_valid(self, cell):
        '''Checks if the number in the cell is valid'''
        condition = True
        i, j = cell.cooridnates
        row = [self.board[i][x].val for x in range(self.size) if x != j]
        col = [self.board[x][j].val for x in range(self.size) if x != i]
        elements = row + col
        condition &= (elements.count(cell.val) == 0)
        condition &= cell.cage.check_constraint()
        return condition

    def show_board(self,Button1,Button2,Button3,Checkbutton1,Checkbutton2,kenken,cells_domains):
        '''Prints the board with the values in it'''
        if Checkbutton1.get():
            s = kenken.backtrack()
        elif  Checkbutton2.get():
            s = kenken.forward_check(var_domains=cells_domains, show=False)
        j=0
        i=0
        for roww in self.board:
            col=[]

            for element in roww:
                col.append('('+str(element.cage.goal)+element.cage.op+') '+str(element.val))
                # col.append(element.val)
                e=tk.Entry(window,width=20, fg='blue',
                            font=('Arial',16,'bold'))
                e.grid(row=i, column=j)
                    
                e.insert(tk.END, col[j])
                
                j+=1
            j=0 
            i+=1   
        Button1.grid_remove()
        Button2.grid_remove()
        Button3.grid_remove()







        
def ken_ken(n):
 kenken = KenKen(n-1)
 kenken.show_cages()
 cells_domains =[]
 for i in range(n-1):
    cells_domains.append([])
    for j in range(n-1):
        cells_domains[i].append(set(range(1, (n-1)+1)))
 Checkbutton1 = tk.IntVar()  
 Checkbutton2 = tk.IntVar()  
 Button1 = tk.Checkbutton(window, text = "BT", 
                      variable=Checkbutton1,
                      onvalue = 1,
                      offvalue = 0,
                      height = 2,
                      width = 10)
 Button2 = tk.Checkbutton(window, text = "FC", 
                      variable=Checkbutton2,
                      onvalue = 1,
                      offvalue = 0,
                      height = 2,
                      width = 10)




 Button3= tk.Button(window, text="Solve", command=lambda: kenken.show_board(Button1,Button2,Button3,Checkbutton1,Checkbutton2,kenken,cells_domains))



 Button1.grid(row=n, column=1)                     
 Button2.grid(row=n+1, column=1)
 Button3.grid(row=n, column=2)


 



def get_value(myentry,mybutton):
  n=int(myentry.get())+1   
  myentry.pack_forget() 
  mybutton.pack_forget()
  ken_ken(n)
  button1= tk.Button(window, text="Generate", command=lambda:  ken_ken(n)).grid(row=n+1, column=2)


  
window = tk.Tk()
myentry = tk.Entry(window, width = 20)
myentry.pack(pady = 5)
mybutton = tk.Button(window, text = "Generate", command=lambda:get_value(myentry,mybutton))
mybutton.pack(pady = 5)
window.title("KenKen")
window.mainloop()