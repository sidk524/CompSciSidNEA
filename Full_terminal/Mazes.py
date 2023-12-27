from abc import ABC, abstractmethod
import random
import pygame as pg
import math

# Initilise a flipped dictionary during initialisation of the maze


class Cell:
    def __init__(self,  maxConnections, ID):
        self.__connections = []
        self.__maxConnections = maxConnections
        self.__id = ID
        self.__parent = None


    def addConnection(self, cell):
        if len(self.__connections) < self.__maxConnections and not (cell in self.__connections):
            self.__connections.append(cell)
            cell.addConnection(self)
       
    
    def removeConnection(self, cell):
        if cell in self.__connections:
            self.__connections.remove(cell)
            cell.removeConnection(self)
         
        
    def setParent(self, cell):  
        self.__parent = cell

    def getParent(self):
        return self.__parent
    
    def getID(self):
        return tuple(map(int, (self.__id)))
    
    def getConnections(self):
        return self.__connections

    def __str__(self):
        return str(self.__id)

    def __repr__(self):
        return str(self.__id)
        

class Maze:
    MAZETYPES = ["square", "hexagonal", "triangular", "octagonal"]
    def __init__(self, mazeType, size, gen_algorithm, solve_algorithm):

        self.__type = self.MAZETYPES[mazeType-1]
        self.__size = size
        
        self.__gen_algorithm_name = gen_algorithm
        self.__solve_algorithm_name = solve_algorithm
        self.__AlgorithmFactory = AlgorithmFactory(self.__gen_algorithm_name, self.__solve_algorithm_name)
        self.__genAlgorithm = self.__AlgorithmFactory.getGenAlgorithm()
        self.__solveAlgorithm = self.__AlgorithmFactory.getSolveAlgorithm()


    def initialiseMaze(self):
            if self.__type == "square":
                self.__grid = dict()
                for y in range(self.__size):
                    self.__grid[y] = []
                    for x in range(self.__size):
                        self.__grid[y].append(Cell(4, (x,y)))

            elif self.__type == "hexagonal":
                self.__grid = dict()
                for y in range(self.__size):
                    self.__grid[y] = []
                    if y % 2 == 0:
                        for x in range(self.__size):
                            self.__grid[y].append(Cell(6, (x,y)))
                    else:
                        for x in range(self.__size-1):
                            self.__grid[y].append(Cell(6, (x,y)))
            elif self.__type == "triangular":
                self.__grid = dict()
                self.__flipped_grid = dict()
                for y in range(self.__size):
                    self.__grid[y] = []
                    for x in range(self.__size):
                        self.__grid[y].append(Cell(3, (x,y)))
    
    def getSolveAlgorithmName(self):
        return self.__solve_algorithm_name
    
    

    def generate(self):
        self.initialiseMaze()
        self.__grid = self.__genAlgorithm.generate(self)
        self.__curr = self.__solveAlgorithm.findValidPath(self)
        gen = 0
        while self.__curr == False:
            self.__genAlgorithm.generate(self)
            self.__curr = self.__solveAlgorithm.findValidPath(self)
            gen += 1
        print(gen)
        self.__validPath, self.__algorithm_route = self.__curr
        self.__algorithm_route_ids = [i.getID() for i in self.__algorithm_route]
       

    def getAlgorithmRouteIDs(self):
        return self.__algorithm_route_ids
    
    def getAlgorithmRoute(self):
        return self.__algorithm_route

    def getMazeType(self):
        return self.__type
    
    def getMazeSize(self):
        return self.__size
    
    def getGrid(self):
        return self.__grid
    
    def solve_step(self, clicked_cell_id, current_cell):
        return self.__solveAlgorithm.solve_step(self, clicked_cell_id, current_cell)
    
   

class AlgorithmFactory():
    solvingAlgorithms = ["breadth_first", "depth_first", "manual"]
    generatingAlgorithms = ["sidewinder", "binary_tree"]
    def __init__(self, genName, solveName):
        self.__genName = genName
        self.__solveName = solveName
        
    def getGenAlgorithm(self):
        if not (self.__genName in AlgorithmFactory.generatingAlgorithms):
            raise Exception("Invalid algorithm type")
        elif self.__genName == "sidewinder":
            self.__genAlgorithm = Sidewinder()
        elif self.__genName == "binary_tree":
            self.__genAlgorithm = BinaryTree()
        return self.__genAlgorithm
    
    def getSolveAlgorithm(self):
        if not (self.__solveName in AlgorithmFactory.solvingAlgorithms):
            raise Exception("Invalid algorithm type")
        elif self.__solveName == "breadth_first":
            self.__solveAlgorithm = BreadthFirst()
        elif self.__solveName == "depth_first":
            self.__solveAlgorithm = DepthFirst()
        elif self.__solveName == "manual":
            self.__solveAlgorithm = Manual()

        return self.__solveAlgorithm

class GenAlgorithm(ABC):
    @abstractmethod
    def generate(self, maze):
        pass


class SolveAlgorithm(ABC):
    
    @abstractmethod
    def findValidPath(self, maze):
        pass

    @abstractmethod
    def solve_step(self, maze, clicked_cell_id, current_cell):
        pass

    def getNeighbours(self, cell, maze):
            self.__neighbours = []
            self.__x = cell.getID()[0]
            self.__y = cell.getID()[1]
            self.__maze = maze
            if self.__maze.getMazeType() == "square":
                self.__potential_neighbours = [ (self.__x + 1, self.__y), (self.__x - 1, self.__y), (self.__x, self.__y + 1), (self.__x, self.__y - 1)]
                for i in self.__potential_neighbours:
                    if i[0] >= 0 and i[0] < self.__maze.getMazeSize() and i[1] >= 0 and i[1] < self.__maze.getMazeSize():
                        self.__potential_neighbour = self.__maze.getGrid()[i[1]][i[0]]
                        if self.__potential_neighbour in cell.getConnections():
                            self.__neighbours.append(self.__potential_neighbour)
                return self.__neighbours
            elif self.__maze.getMazeType() == "hexagonal":
                self.__potential_neighbours = [ (self.__x + 1, self.__y), (self.__x - 1, self.__y), (self.__x, self.__y + 1), (self.__x, self.__y - 1), (self.__x + 1, self.__y - 1), (self.__x - 1, self.__y + 1)]
                for i in self.__potential_neighbours:
                    if i[0] >= 0 and i[1] >= 0 and i[1] < self.__maze.getMazeSize() and i[0] < len(self.__maze.getGrid()[i[1]]):
                            self.__potential_neighbour = self.__maze.getGrid()[i[1]][i[0]]
                            if self.__potential_neighbour in cell.getConnections():
                                self.__neighbours.append(self.__potential_neighbour)
                return self.__neighbours
            elif self.__maze.getMazeType() == "triangular":
                self.__potential_neighbours = [ (self.__x + 1, self.__y), (self.__x - 1, self.__y), (self.__x, self.__y + 1), (self.__x, self.__y - 1)]
                for i in self.__potential_neighbours:
                    if i[0] >= 0 and i[1] >= 0 and i[1] < self.__maze.getMazeSize() and i[0] < len(self.__maze.getGrid()[i[1]]):
                            self.__potential_neighbour = self.__maze.getGrid()[i[1]][i[0]]
                            if self.__potential_neighbour in cell.getConnections():
                                self.__neighbours.append(self.__potential_neighbour)
                return self.__neighbours

class Manual(SolveAlgorithm):
    name = "manual"
    def __init__(self):
        pass

    def findValidPath(self, maze):
        return AlgorithmFactory("sidewinder", "depth_first").getSolveAlgorithm().findValidPath(maze)

    def solve_step(self, maze, clicked_cell_id, current_cell):
        self.__maze = maze
        self.__clicked_cell_id = tuple(map(int, clicked_cell_id))
        self.__current_cell = current_cell
        if self.__maze.getMazeType() == "square":
            self.__cell_neighbours = self.getNeighbours(self.__current_cell, self.__maze)
            if self.__clicked_cell_id[0] < 0 or self.__clicked_cell_id[0] >= self.__maze.getMazeSize() or self.__clicked_cell_id[1] < 0 or self.__clicked_cell_id[1] >= self.__maze.getMazeSize():
                return "invalid_move"
            if self.__clicked_cell_id == (self.__maze.getMazeSize() - 1, self.__maze.getMazeSize() - 1) and self.__clicked_cell_id in [ i.getID() for i in self.__cell_neighbours]:
                return "end"
            elif self.__maze.getGrid()[self.__clicked_cell_id[1]][self.__clicked_cell_id[0]] in self.__cell_neighbours:
                return self.__maze.getGrid()[self.__clicked_cell_id[1]][self.__clicked_cell_id[0]]
            else:
                return "invalid_move"
        elif self.__maze.getMazeType() == "hexagonal":
            self.__cell_neighbours = self.getNeighbours(self.__current_cell, self.__maze)
            if self.__clicked_cell_id[0] < 0 or self.__clicked_cell_id[0] >= len(self.__maze.getGrid()[self.__clicked_cell_id[1]]) or self.__clicked_cell_id[1] < 0 or self.__clicked_cell_id[1] >= self.__maze.getMazeSize():
                return "invalid_move"
            if self.__clicked_cell_id == (len(self.__maze.getGrid()[self.__maze.getMazeSize() - 1]) - 1, self.__maze.getMazeSize() - 1) and self.__clicked_cell_id in [ i.getID() for i in self.__cell_neighbours]:
                return "end"
            elif self.__maze.getGrid()[self.__clicked_cell_id[1]][self.__clicked_cell_id[0]] in self.__cell_neighbours:
                return self.__maze.getGrid()[self.__clicked_cell_id[1]][self.__clicked_cell_id[0]]
            else:
                return "invalid_move"
        elif self.__maze.getMazeType() == "triangular":
            self.__cell_neighbours = self.getNeighbours(self.__current_cell, self.__maze)

            if self.__clicked_cell_id[0] < 0 or self.__clicked_cell_id[0] >= self.__maze.getMazeSize() or self.__clicked_cell_id[1] < 0 or self.__clicked_cell_id[1] >= self.__maze.getMazeSize():
                return "invalid_move"
            if self.__clicked_cell_id == (len(self.__maze.getGrid()[self.__maze.getMazeSize() - 1]) - 1, self.__maze.getMazeSize() - 1) and self.__clicked_cell_id in [ i.getID() for i in self.__cell_neighbours]:
                return "end"
            elif self.__maze.getGrid()[self.__clicked_cell_id[1]][self.__clicked_cell_id[0]] in self.__cell_neighbours:
                return self.__maze.getGrid()[self.__clicked_cell_id[1]][self.__clicked_cell_id[0]]
            else:
                return "invalid_move"

class DepthFirst(SolveAlgorithm):
    name = "depth_first"
    def __init__(self):
        pass
    def findValidPath(self, maze):
        self.__maze = maze
        if self.__maze.getMazeType() == "square":
            self.__stack = [self.__maze.getGrid()[0][0]]
            self.__visitedCells = []
            while len(self.__stack) > 0:
                    self.__currentCell = self.__stack.pop()
                    self.__visitedCells.append(self.__currentCell)
                    if self.__currentCell.getID() == (len(self.__maze.getGrid()[self.__maze.getMazeSize() - 1]) - 1, self.__maze.getMazeSize() - 1):
                        path = []
                        self.__currentCell = self.__maze.getGrid()[self.__maze.getMazeSize() - 1][self.__maze.getMazeSize() - 1]
                        while self.__currentCell != None:
                            path.append(self.__currentCell)
                            self.__currentCell = self.__currentCell.getParent()
                        return path, self.__visitedCells
                    else:
                        self.__neighbours = self.getNeighbours(self.__currentCell, self.__maze)
                        if len(self.__neighbours) > 0:
                            for i in self.__neighbours:
                                if not (i in self.__visitedCells):
                                    i.setParent(self.__currentCell)
                                    self.__stack.append(i)
        elif self.__maze.getMazeType() == "hexagonal":
            self.__stack = [self.__maze.getGrid()[0][0]]
            self.__visitedCells = []
            while len(self.__stack) > 0:
                self.__currentCell = self.__stack.pop()
                self.__visitedCells.append(self.__currentCell)
                if self.__currentCell.getID() == (len(self.__maze.getGrid()[self.__maze.getMazeSize() - 1]) - 1, self.__maze.getMazeSize() - 1):
                    path = []
                    self.__currentCell = self.__maze.getGrid()[self.__maze.getMazeSize() - 1][len(self.__maze.getGrid()[self.__maze.getMazeSize() - 1]) - 1]
                    while self.__currentCell != None:
                        path.append(self.__currentCell)
                        self.__currentCell = self.__currentCell.getParent()
                    return path, self.__visitedCells
                else:
                    self.__neighbours = self.getNeighbours(self.__currentCell, self.__maze)
                    if len(self.__neighbours) > 0:
                        for i in self.__neighbours:
                            if not (i in self.__visitedCells):
                                i.setParent(self.__currentCell)
                                self.__stack.append(i)
        elif self.__maze.getMazeType() == "triangular":
            self.__stack = [self.__maze.getGrid()[0][0]]
            self.__visitedCells = []
            while len(self.__stack) > 0:
                self.__currentCell = self.__stack.pop()
                self.__visitedCells.append(self.__currentCell)
                if self.__currentCell.getID() == (len(self.__maze.getGrid()[self.__maze.getMazeSize() - 1]) - 1, self.__maze.getMazeSize() - 1):
                    path = []
                    self.__currentCell = self.__maze.getGrid()[self.__maze.getMazeSize() - 1][len(self.__maze.getGrid()[self.__maze.getMazeSize() - 1]) - 1]
                    while self.__currentCell != None:
                        path.append(self.__currentCell)
                        self.__currentCell = self.__currentCell.getParent()
                    return path, self.__visitedCells
                else:
                    self.__neighbours = self.getNeighbours(self.__currentCell, self.__maze)
                    if len(self.__neighbours) > 0:
                        for i in self.__neighbours:
                            if not (i in self.__visitedCells):
                                i.setParent(self.__currentCell)
                                self.__stack.append(i)
        return False        

    def solve_step(self, maze, clicked_cell_id, current_cell):
        
        self.__maze = maze
        self.__clicked_cell_id = tuple(map(int, clicked_cell_id))
        self.__current_cell = current_cell
        if self.__maze.getMazeType() == "square":
            if not(self.__clicked_cell_id[0] < 0 or self.__clicked_cell_id[0] >= self.__maze.getMazeSize() or self.__clicked_cell_id[1] < 0 or self.__clicked_cell_id[1] >= self.__maze.getMazeSize()): # check if the clicked cell is in the maze
                self.__algorithm_route_current_cell_index = self.__maze.getAlgorithmRoute().index(self.__current_cell)
                if self.__clicked_cell_id in self.__maze.getAlgorithmRouteIDs(): # check if the clicked cell is in the algorithm route
                    if self.__maze.getAlgorithmRouteIDs().index(self.__clicked_cell_id) == len(self.__maze.getAlgorithmRoute())-1 and self.__algorithm_route_current_cell_index == len(self.__maze.getAlgorithmRoute())-2:
                        return "end"
                    elif self.__maze.getAlgorithmRouteIDs()[self.__algorithm_route_current_cell_index+1] == self.__clicked_cell_id:
                        return self.__maze.getGrid()[self.__clicked_cell_id[1]][self.__clicked_cell_id[0]]     
                    else:
                        return "wrong_move"
                else:
                    return "wrong_move"
            else:
                return "invalid_move"                      
        elif self.__maze.getMazeType() == "hexagonal":
            if not(self.__clicked_cell_id[0] < 0 or self.__clicked_cell_id[0] >= len(self.__maze.getGrid()[self.__clicked_cell_id[1]]) or self.__clicked_cell_id[1] < 0 or self.__clicked_cell_id[1] >= self.__maze.getMazeSize()):
                self.__algorithm_route_current_cell_index = self.__maze.getAlgorithmRoute().index(self.__current_cell)
                if self.__clicked_cell_id in self.__maze.getAlgorithmRouteIDs():
                    if self.__maze.getAlgorithmRouteIDs().index(self.__clicked_cell_id) == len(self.__maze.getAlgorithmRoute())-1 and self.__algorithm_route_current_cell_index == len(self.__maze.getAlgorithmRoute())-2:
                        return "end"
                    elif self.__maze.getAlgorithmRouteIDs()[self.__algorithm_route_current_cell_index+1] == self.__clicked_cell_id:
                        return self.__maze.getGrid()[self.__clicked_cell_id[1]][self.__clicked_cell_id[0]]     
                    else:
                        return "wrong_move"
                else:
                    return "wrong_move"
            else:
                return "invalid_move"
        elif self.__maze.getMazeType() == "triangular":
            if not(self.__clicked_cell_id[0] < 0 or self.__clicked_cell_id[0] >= self.__maze.getMazeSize() or self.__clicked_cell_id[1] < 0 or self.__clicked_cell_id[1] >= self.__maze.getMazeSize()):
                self.__algorithm_route_current_cell_index = self.__maze.getAlgorithmRoute().index(self.__current_cell)
                if self.__clicked_cell_id in self.__maze.getAlgorithmRouteIDs():
                    if self.__maze.getAlgorithmRouteIDs().index(self.__clicked_cell_id) == len(self.__maze.getAlgorithmRoute())-1 and self.__algorithm_route_current_cell_index == len(self.__maze.getAlgorithmRoute())-2:
                        return "end"
                    elif self.__maze.getAlgorithmRouteIDs()[self.__algorithm_route_current_cell_index+1] == self.__clicked_cell_id:
                        return self.__maze.getGrid()[self.__clicked_cell_id[1]][self.__clicked_cell_id[0]]     
                    else:
                        return "wrong_move"
                else:
                    return "wrong_move"
            else:
                return "invalid_move"
            

    
class BreadthFirst(SolveAlgorithm):
    name = "breadth_first"
    def __init__(self):
        pass
    def findValidPath(self, maze):
        self.__maze = maze
        if self.__maze.getMazeType() == "square":
            self.__queue = [self.__maze.getGrid()[0][0]]
            self.__visitedCells = []
            while len(self.__queue) > 0:
                self.__currentCell = self.__queue.pop(0)
                self.__visitedCells.append(self.__currentCell)
                if self.__currentCell.getID() == (self.__maze.getMazeSize() - 1, self.__maze.getMazeSize() - 1):
                    path = []
                    self.__currentCell = self.__maze.getGrid()[self.__maze.getMazeSize() - 1][self.__maze.getMazeSize() - 1]
                    while self.__currentCell != None:
                        path.append(self.__currentCell)
                        self.__currentCell = self.__currentCell.getParent()
                    return path, self.__visitedCells
                else:
                    self.__neighbours = self.getNeighbours(self.__currentCell, self.__maze)
                    if len(self.__neighbours) > 0:
                        for i in self.__neighbours:
                            if not (i in self.__visitedCells):
                                i.setParent(self.__currentCell)
                                self.__queue.append(i)
            return False      
        
        elif self.__maze.getMazeType() == "hexagonal":
            self.__queue = [self.__maze.getGrid()[0][0]]
            self.__visitedCells = []
            while len(self.__queue) > 0:
                self.__currentCell = self.__queue.pop(0)
                self.__visitedCells.append(self.__currentCell)
                if self.__currentCell.getID() == (len(self.__maze.getGrid()[self.__maze.getMazeSize() - 1]) - 1, self.__maze.getMazeSize() - 1):
                    path = []
                    self.__currentCell = self.__maze.getGrid()[self.__maze.getMazeSize() - 1][len(self.__maze.getGrid()[self.__maze.getMazeSize() - 1]) - 1]
                    while self.__currentCell != None:
                        path.append(self.__currentCell)
                        self.__currentCell = self.__currentCell.getParent()
                    return path, self.__visitedCells
                else:
                    self.__neighbours = self.getNeighbours(self.__currentCell, self.__maze)
                    if len(self.__neighbours) > 0:
                        for i in self.__neighbours:
                            if not (i in self.__visitedCells):
                                i.setParent(self.__currentCell)
                                self.__queue.append(i)

            return False

    def solve_step(self, maze, clicked_cell_id, current_cell):
        self.__maze = maze
        self.__clicked_cell_id = tuple(map(int, clicked_cell_id))
        self.__current_cell = current_cell
        if self.__maze.getMazeType() == "square":
            if not(self.__clicked_cell_id[0] < 0 or self.__clicked_cell_id[0] >= self.__maze.getMazeSize() or self.__clicked_cell_id[1] < 0 or self.__clicked_cell_id[1] >= self.__maze.getMazeSize()):
                self.__algorithm_route_current_cell_index = self.__maze.getAlgorithmRoute().index(self.__current_cell)
                if self.__clicked_cell_id in self.__maze.getAlgorithmRouteIDs():
                    if self.__maze.getAlgorithmRouteIDs().index(self.__clicked_cell_id) == len(self.__maze.getAlgorithmRoute())-1 and self.__algorithm_route_current_cell_index == len(self.__maze.getAlgorithmRoute())-2:
                        return "end"
                    elif self.__maze.getAlgorithmRouteIDs()[self.__algorithm_route_current_cell_index+1] == self.__clicked_cell_id:
                        return self.__maze.getGrid()[self.__clicked_cell_id[1]][self.__clicked_cell_id[0]]     
                    else:
                        return "wrong_move"
                else:
                    return "wrong_move"
            else:
                return "invalid_move"
        elif self.__maze.getMazeType() == "hexagonal":
            print(self.__clicked_cell_id)
            if not(self.__clicked_cell_id[0] < 0 or self.__clicked_cell_id[0] >= len(self.__maze.getGrid()[self.__clicked_cell_id[1]]) or self.__clicked_cell_id[1] < 0 or self.__clicked_cell_id[1] >= self.__maze.getMazeSize()):
                self.__algorithm_route_current_cell_index = self.__maze.getAlgorithmRoute().index(self.__current_cell)
                if self.__clicked_cell_id in self.__maze.getAlgorithmRouteIDs():
                    if self.__maze.getAlgorithmRouteIDs().index(self.__clicked_cell_id) == len(self.__maze.getAlgorithmRoute())-1 and self.__algorithm_route_current_cell_index == len(self.__maze.getAlgorithmRoute())-2:
                        return "end"
                    elif self.__maze.getAlgorithmRouteIDs()[self.__algorithm_route_current_cell_index+1] == self.__clicked_cell_id:
                        return self.__maze.getGrid()[self.__clicked_cell_id[1]][self.__clicked_cell_id[0]]     
                    else:
                        return "wrong_move"
                else:
                    return "wrong_move"
            else:
                return "invalid_move"
        
class Sidewinder(GenAlgorithm):
    name = "sidewinder"
    def __init__(self):
        pass
    def generate(self, maze):
        self.__maze = maze
        if self.__maze.getMazeType() == "square":
            
            self.__current_run = []
            for y in range(0, self.__maze.getMazeSize()):
                self.__current_run = []
                for x in range(self.__maze.getMazeSize()):
                    cell = self.__maze.getGrid()[y][x]
                    self.__current_run.append(cell)
                    end_run = False
                    connect_left = False
                    
                    if x == self.__maze.getMazeSize() - 1:
                        # If it's the last cell in the row, end the run
                        end_run = True
                    else:
                        # Randomly decide to connect to the left or end the run
                        decision = random.randint(0, 1)
                        if decision == 0:
                            end_run = True
                        else:
                            connect_left = True

                    if end_run and y != 0:
                        chosen_cell = random.choice(self.__current_run)
                        chosen_cell.addConnection(self.__maze.getGrid()[y-1][chosen_cell.getID()[0]])
                        self.__current_run = []  # Clear the current run
                    elif (connect_left and x < self.__maze.getMazeSize() - 1) or (y == 0 and x < self.__maze.getMazeSize() - 1):  # Not the leftmost cell and decided to connect left
                        cell.addConnection(self.__maze.getGrid()[y][x+1])
            return self.__maze.getGrid()
        elif self.__maze.getMazeType() == "hexagonal":
            self.__maze = maze
            self.__current_run = []
            for y in range(self.__maze.getMazeSize()):
                self.__current_run = []
                for x in range(len(self.__maze.getGrid()[y])):
                    cell = self.__maze.getGrid()[y][x]
                    self.__current_run.append(cell)
                    end_run = False
                    connect_left = False
                    
                    if x == len(self.__maze.getGrid()[y]) - 1:
                        # If it's the last cell in the row, end the run
                        end_run = True
                    else:
                        # Randomly decide to connect to the left or end the run
                        decision = random.randint(0, 1)
                        if decision == 0:
                            end_run = True
                        else:
                            connect_left = True

                    if end_run and y != 0:
                        chosen_cell = random.choice(self.__current_run)
                        if chosen_cell.getID()[0] >= len(self.__maze.getGrid()[chosen_cell.getID()[1]-1]):
                            chosen_cell.addConnection(self.__maze.getGrid()[chosen_cell.getID()[1]-1][len(self.__maze.getGrid()[y-1])-1])
                        elif chosen_cell.getID()[0] == 0:
                            chosen_cell.addConnection(self.__maze.getGrid()[chosen_cell.getID()[1]-1][0])
                        else:
                            if y % 2 == 0:
                                chosen_cell.addConnection(self.__maze.getGrid()[chosen_cell.getID()[1]-1][chosen_cell.getID()[0]])
                            else:
                                chosen_cell.addConnection(self.__maze.getGrid()[chosen_cell.getID()[1]-1][chosen_cell.getID()[0]])
                        self.__current_run = []
                    elif (connect_left and x < len(self.__maze.getGrid()[y]) - 1) or (y == 0 and x < len(self.__maze.getGrid()[y]) - 1): # if not the leftmost cell and decided to connect left

                        cell.addConnection(self.__maze.getGrid()[y][x+1])
            return self.__maze.getGrid()
        elif self.__maze.getMazeType() == "triangular":
            self.__maze = maze
            self.__current_run = []
            for y in range(self.__maze.getMazeSize()):
                self.__current_run = []
                for x in range(0, len(self.__maze.getGrid()[y])-1):
                    cell = self.__maze.getGrid()[y][x]
                    self.__current_run.append(cell)
                    end_run = False
                    connect_left = False
                    if x == len(self.__maze.getGrid()[y]) - 1:
                        end_run = True
                    else:
                        decision = random.randint(0, 10)
                        if decision <= 3:
                            end_run = True
                        else:
                            connect_left = True
                    if end_run and y != 0:
                        self.__x, self.__y = random.choice(self.__current_run).getID()
                        
                        flipped = False
                        if self.__x % 2 == 1:
                            flipped = True
                        if self.__y%2 == 1:
                            flipped = not flipped
                        if not flipped:
                            self.__maze.getGrid()[self.__y][self.__x].addConnection(self.__maze.getGrid()[self.__y-1][self.__x])
                        else:
                            cell.addConnection(self.__maze.getGrid()[y][x+1])
                            self.__maze.getGrid()[self.__y][self.__x+1].addConnection(self.__maze.getGrid()[self.__y-1][self.__x+1])
                        self.__current_run = []
                    elif (connect_left and x < len(self.__maze.getGrid()[y]) - 1) or (y == 0 and x < len(self.__maze.getGrid()[y]) - 1):
                        cell.addConnection(self.__maze.getGrid()[y][x+1])
                    else:
                        print("Here")
            return self.__maze.getGrid()
 
        
class BinaryTree(GenAlgorithm):
    name = "binary_tree"
    def __init__(self):
        pass
    def generate(self, maze):
        self.__maze = maze
        if self.__maze.getMazeType() == "square":
            for y in range(self.__maze.getMazeSize()):
                for x in range(self.__maze.getMazeSize()):
                    cell = self.__maze.getGrid()[y][x]
                    if y == 0 and x == 0:
                        pass
                    elif y == 0:
                        cell.addConnection(self.__maze.getGrid()[y][x-1])
                    elif x == 0:
                        cell.addConnection(self.__maze.getGrid()[y-1][x])
                    else:
                        decision = random.randint(0, 1)
                        if decision == 0:
                            cell.addConnection(self.__maze.getGrid()[y][x-1])
                        else:
                            cell.addConnection(self.__maze.getGrid()[y-1][x])
            return self.__maze.getGrid()
        elif self.__maze.getMazeType() == "hexagonal":
            for y in range(self.__maze.getMazeSize()):
                for x in range(len(self.__maze.getGrid()[y])):
                    cell = self.__maze.getGrid()[y][x]
                    if y == 0 and x == 0:
                        pass
                    elif y == 0:
                        cell.addConnection(self.__maze.getGrid()[y][x-1])
                    elif x == 0:
                        cell.addConnection(self.__maze.getGrid()[y-1][x])
                    else:
                        decision = random.randint(0, 1)
                        if decision == 0:
                            cell.addConnection(self.__maze.getGrid()[y][x-1])
                        else:
                            if y % 2 == 0 and x == len(self.__maze.getGrid()[y-1]):
                                cell.addConnection(self.__maze.getGrid()[y-1][x-1])
                            else:
                                cell.addConnection(self.__maze.getGrid()[y-1][x])
            return self.__maze.getGrid()
        elif self.__maze.getMazeType() == "triangular":
            for y in range(self.__maze.getMazeSize()):
                for x in range(len(self.__maze.getGrid()[y])):
                    cell = self.__maze.getGrid()[y][x]
                    if y == 0 and x == 0:
                        pass
                    elif y == 0:
                        cell.addConnection(self.__maze.getGrid()[y][x-1])
                    elif x == 0:
                        cell.addConnection(self.__maze.getGrid()[y-1][x])
                    else:
                        decision = random.randint(0, 1)
                        if decision == 0:
                            cell.addConnection(self.__maze.getGrid()[y][x-1])
                        else:
                            flipped = False
                            self.__x, self.__y = cell.getID()
                            if self.__x % 2 == 1:
                                flipped = True
                            if self.__y%2 == 1:
                                flipped = not flipped
                            if not flipped:
                                cell.addConnection(self.__maze.getGrid()[y-1][x])
                            else:
                                cell.addConnection(self.__maze.getGrid()[y][x-1])
                                self.__maze.getGrid()[y][x-1].addConnection(self.__maze.getGrid()[y-1][x-1])

            return self.__maze.getGrid()
     
