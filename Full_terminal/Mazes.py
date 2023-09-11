from abc import ABC, abstractmethod
import random
import pygame as pg
import math

# Initilise a flipped dictionary during initialisation of the maze


class Cell:
    def __init__(self,  maxConnections, ID):
        self.connections = []
        self.maxConnections = maxConnections
        self.id = ID
        self.parent = None
        self.camefrom = None


    def addConnection(self, cell):
        if len(self.connections) < self.maxConnections and not (cell in self.connections):
            self.connections.append(cell)
            return cell.addConnection(self)
        else:
            return False
    
    def removeConnection(self, cell):
        if cell in self.connections:
            self.connections.remove(cell)
            return cell.removeConnection(self)
             
        else:
            return False
    
    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return str(self.id)
        

class Maze:
    MAZETYPES = ["square", "hexagonal", "triangular", "octagonal"]
    def __init__(self, mazeType, size, gen_algorithm, solve_algorithm):
        
        self.type = self.MAZETYPES[mazeType-1]

        self.size = size
        
        self.gen_algorithm_name = gen_algorithm
        self.solve_algorithm_name = solve_algorithm
        self.genAlgorithm = genAlgorithm(gen_algorithm)
        self.solveAlgorithm = solveAlgorithm(solve_algorithm)

    def generate(self):
        self.initialiseMaze()
        self.grid = self.genAlgorithm.generate(self)
        self.validPath, self.algorithm_route = self.solveAlgorithm.findValidPath(self)
        self.algorithm_route_ids = [i.id for i in self.algorithm_route]
        print(self.algorithm_route)
        

    def solve_step(self, clicked_cell_id, current_cell):
        return self.solveAlgorithm.solve_step(self, clicked_cell_id, current_cell)
    
    def initialiseMaze(self):
        if self.type == "square":
            self.grid = dict()
            for y in range(self.size):
                self.grid[y] = []
                for x in range(self.size):
                    self.grid[y].append(Cell(4, (x,y)))
        elif self.type == "hexagonal":
            self.grid = dict()
            for y in range(self.size):
                self.grid[y] = []
                if y % 2 == 0:
                    for x in range(self.size):
                        self.grid[y].append(Cell(6, (x,y)))
                else:
                    for x in range(self.size-1):
                        self.grid[y].append(Cell(6, (x,y)))
        elif self.type == "triangular":
            self.grid = dict()
            self.flipped_grid = dict()
            for y in range(self.size):
                self.grid[y] = []
                for x in range(self.size):
                    self.grid[y].append(Cell(3, (x,y)))
        

class Algorithm(ABC):
    solvingAlgorithms = ["breadth_first", "depth_first", "manual"]
    generatingAlgorithms = ["sidewinder", "binary_tree"]
    def __init__(self, name):
        self.name = name

class genAlgorithm(Algorithm):
    def __init__(self, name):
        super().__init__(name)

        if not (name in genAlgorithm.generatingAlgorithms):
            raise Exception("Invalid algorithm type")
        else:
            if self.name == "sidewinder":
                self.algorithm = sidewinder()
            elif self.name == "binary_tree":
                self.algorithm = binary_tree()
    def generate(self, maze):
        return self.algorithm.generate(maze)
    

class solveAlgorithm(Algorithm):
    
        def __init__(self, name):
            super().__init__(name)

            if not (name in solveAlgorithm.solvingAlgorithms):
                raise Exception("Invalid algorithm type")
            else:
                if self.name == "breadth_first":
                    self.algorithm = breadthFirst()
                elif self.name == "depth_first":
                    self.algorithm = depthFirst()
                elif self.name == "manual":
                    self.algorithm = manual()

        def solve(self, maze):
            return self.algorithm.solve(maze)
        
        def solve_step(self, maze, clicked_cell_id, current_cell):
            return self.algorithm.solve_step(maze, clicked_cell_id, current_cell)
        
        def findValidPath(self, maze):
            return self.algorithm.findValidPath(maze)

        def getNeighbours(self, cell):
            self.neighbours = []
            self.x = cell.id[0]
            self.y = cell.id[1]
            if self.maze.type == "square":
                self.potential_neighbours = [ (self.x + 1, self.y), (self.x - 1, self.y), (self.x, self.y + 1), (self.x, self.y - 1)]
                for i in self.potential_neighbours:
                    if i[0] >= 0 and i[0] < self.maze.size and i[1] >= 0 and i[1] < self.maze.size:
                        self.potential_neighbour = self.maze.grid[i[1]][i[0]]
                        if self.potential_neighbour in cell.connections:
                            self.neighbours.append(self.potential_neighbour)
                return self.neighbours
            elif self.maze.type == "hexagonal":
                self.potential_neighbours = [ (self.x + 1, self.y), (self.x - 1, self.y), (self.x, self.y + 1), (self.x, self.y - 1), (self.x + 1, self.y - 1), (self.x - 1, self.y + 1)]
                for i in self.potential_neighbours:
                    if i[0] >= 0 and i[1] >= 0 and i[1] < self.maze.size and i[0] < len(self.maze.grid[i[1]]):
                            self.potential_neighbour = self.maze.grid[i[1]][i[0]]
                            if self.potential_neighbour in cell.connections:
                                self.neighbours.append(self.potential_neighbour)
                return self.neighbours

class manual(solveAlgorithm):
    name = "manual"
    def __init__(self):
        pass

    def findValidPath(self, maze):
        return [], []
    
    def solve_step(self, maze, clicked_cell_id, current_cell):
        self.maze = maze
        self.clicked_cell_id = clicked_cell_id
        self.current_cell = current_cell
        if self.maze.type == "square":
            self.cell_neighbours = self.getNeighbours(self.current_cell)
            if self.clicked_cell_id[0] < 0 or self.clicked_cell_id[0] >= self.maze.size or self.clicked_cell_id[1] < 0 or self.clicked_cell_id[1] >= self.maze.size:
                return "invalid_move"
            if self.clicked_cell_id == (self.maze.size - 1, self.maze.size - 1) and self.clicked_cell_id in [ i.id for i in self.cell_neighbours]:
                return "end"
            elif self.maze.grid[self.clicked_cell_id[1]][self.clicked_cell_id[0]] in self.cell_neighbours:
                return self.maze.grid[self.clicked_cell_id[1]][self.clicked_cell_id[0]]
            else:
                return "invalid_move"
        elif self.maze.type == "hexagonal":
            self.cell_neighbours = self.getNeighbours(self.current_cell)
            if self.clicked_cell_id[0] < 0 or self.clicked_cell_id[0] >= len(self.maze.grid[self.clicked_cell_id[1]]) or self.clicked_cell_id[1] < 0 or self.clicked_cell_id[1] >= self.maze.size:
                return "invalid_move"
            if self.clicked_cell_id == (len(self.maze.grid[self.maze.size - 1]) - 1, self.maze.size - 1) and self.clicked_cell_id in [ i.id for i in self.cell_neighbours]:
                return "end"
            elif self.maze.grid[self.clicked_cell_id[1]][self.clicked_cell_id[0]] in self.cell_neighbours:
                return self.maze.grid[self.clicked_cell_id[1]][self.clicked_cell_id[0]]
            else:
                return "invalid_move"
        elif self.maze.type == "triangular":
            self.cell_neighbours = self.getNeighbours(self.current_cell)
            if self.clicked_cell_id[0] < 0 or self.clicked_cell_id[0] >= self.maze.size or self.clicked_cell_id[1] < 0 or self.clicked_cell_id[1] >= self.maze.size:
                return "invalid_move"
            if self.clicked_cell_id == (self.maze.size - 1, self.maze.size - 1) and self.clicked_cell_id in [ i.id for i in self.cell_neighbours]:
                return "end"
            elif self.maze.grid[self.clicked_cell_id[1]][self.clicked_cell_id[0]] in self.cell_neighbours:
                return self.maze.grid[self.clicked_cell_id[1]][self.clicked_cell_id[0]]
            else:
                return "invalid_move"


class depthFirst(solveAlgorithm):
    name = "depth_first"
    def __init__(self):
        pass
    def findValidPath(self, maze):
        self.maze = maze
        if self.maze.type == "square":
            self.stack = [self.maze.grid[0][0]]
            self.visitedCells = []
            while len(self.stack) > 0:
                self.currentCell = self.stack.pop()
                self.visitedCells.append(self.currentCell)
                if self.currentCell.id == (self.maze.size - 1, self.maze.size - 1):
                    path = []
                    self.currentCell = self.maze.grid[self.maze.size - 1][self.maze.size - 1]
                    while self.currentCell != None:
                        path.append(self.currentCell)
                        self.currentCell = self.currentCell.parent
                    return path, self.visitedCells
                else:
                    self.neighbours = self.getNeighbours(self.currentCell)
                    if len(self.neighbours) > 0:
                        for i in self.neighbours:
                            if not (i in self.visitedCells):
                                i.parent = self.currentCell
                                self.stack.append(i)
            raise Exception("No valid path found")
        elif self.maze.type == "hexagonal":
            self.stack = [self.maze.grid[0][0]]
            self.visitedCells = []
            while len(self.stack) > 0:
                self.currentCell = self.stack.pop()
                self.visitedCells.append(self.currentCell)
                if self.currentCell.id == (len(self.maze.grid[self.maze.size - 1]) - 1, self.maze.size - 1):
                    path = []
                    self.currentCell = self.maze.grid[self.maze.size - 1][len(self.maze.grid[self.maze.size - 1]) - 1]
                    while self.currentCell != None:
                        path.append(self.currentCell)
                        self.currentCell = self.currentCell.parent
                    return path, self.visitedCells
                else:
                    self.neighbours = self.getNeighbours(self.currentCell)
                    if len(self.neighbours) > 0:
                        for i in self.neighbours:
                            if not (i in self.visitedCells):
                                i.parent = self.currentCell
                                self.stack.append(i)

            raise Exception("No valid path found")
        

    def solve_step(self, maze, clicked_cell_id, current_cell):
        
        self.maze = maze
        self.clicked_cell_id = clicked_cell_id
        self.current_cell = current_cell
        if self.maze.type == "square":
            print(self.clicked_cell_id, self.maze.size)
            if not(self.clicked_cell_id[0] < 0 or self.clicked_cell_id[0] >= self.maze.size or self.clicked_cell_id[1] < 0 or self.clicked_cell_id[1] >= self.maze.size): # check if the clicked cell is in the maze
                self.algorithm_route_current_cell_index = self.maze.algorithm_route.index(self.current_cell)
                if self.clicked_cell_id in self.maze.algorithm_route_ids: # check if the clicked cell is in the algorithm route
                    if self.maze.algorithm_route_ids.index(self.clicked_cell_id) == len(self.maze.algorithm_route)-1 and self.algorithm_route_current_cell_index == len(self.maze.algorithm_route)-2:
                        return "end"
                    elif self.maze.algorithm_route_ids[self.algorithm_route_current_cell_index+1] == self.clicked_cell_id:
                        return self.maze.grid[self.clicked_cell_id[1]][self.clicked_cell_id[0]]     
                    else:
                        return "wrong_move"
                else:
                    return "wrong_move"
            else:
                return "invalid_move"                      
        elif self.maze.type == "hexagonal":
            if not(self.clicked_cell_id[0] < 0 or self.clicked_cell_id[0] >= len(self.maze.grid[self.clicked_cell_id[1]]) or self.clicked_cell_id[1] < 0 or self.clicked_cell_id[1] >= self.maze.size):
                self.algorithm_route_current_cell_index = self.maze.algorithm_route.index(self.current_cell)
                if self.clicked_cell_id in self.maze.algorithm_route_ids:
                    if self.maze.algorithm_route_ids.index(self.clicked_cell_id) == len(self.maze.algorithm_route)-1 and self.algorithm_route_current_cell_index == len(self.maze.algorithm_route)-2:
                        return "end"
                    elif self.maze.algorithm_route_ids[self.algorithm_route_current_cell_index+1] == self.clicked_cell_id:
                        return self.maze.grid[self.clicked_cell_id[1]][self.clicked_cell_id[0]]     
                    else:
                        return "wrong_move"
                else:
                    return "wrong_move"
            else:
                return "invalid_move"   
            

    
class breadthFirst(solveAlgorithm):
    name = "breadth_first"
    def __init__(self):
        pass

    def findValidPath(self, maze):
        self.maze = maze
        if self.maze.type == "square":
            self.queue = [self.maze.grid[0][0]]
            self.visitedCells = []
            while len(self.queue) > 0:
                self.currentCell = self.queue.pop(0)
                self.visitedCells.append(self.currentCell)
                if self.currentCell.id == (self.maze.size - 1, self.maze.size - 1):
                    path = []
                    self.currentCell = self.maze.grid[self.maze.size - 1][self.maze.size - 1]
                    while self.currentCell != None:
                        path.append(self.currentCell)
                        self.currentCell = self.currentCell.parent
                    return path, self.visitedCells
                else:
                    self.neighbours = self.getNeighbours(self.currentCell)
                    if len(self.neighbours) > 0:
                        for i in self.neighbours:
                            if not (i in self.visitedCells):
                                i.parent = self.currentCell
                                self.queue.append(i)
            raise Exception("No valid path found")        
        
        elif self.maze.type == "hexagonal":
            self.queue = [self.maze.grid[0][0]]
            self.visitedCells = []
            while len(self.queue) > 0:
                self.currentCell = self.queue.pop(0)
                self.visitedCells.append(self.currentCell)
                if self.currentCell.id == (len(self.maze.grid[self.maze.size - 1]) - 1, self.maze.size - 1):
                    path = []
                    self.currentCell = self.maze.grid[self.maze.size - 1][len(self.maze.grid[self.maze.size - 1]) - 1]
                    while self.currentCell != None:
                        path.append(self.currentCell)
                        self.currentCell = self.currentCell.parent
                    return path, self.visitedCells
                else:
                    self.neighbours = self.getNeighbours(self.currentCell)
                    if len(self.neighbours) > 0:
                        for i in self.neighbours:
                            if not (i in self.visitedCells):
                                i.parent = self.currentCell
                                self.queue.append(i)

            raise Exception("No valid path found")

    def solve_step(self, maze, clicked_cell_id, current_cell):
        self.maze = maze
        self.clicked_cell_id = clicked_cell_id
        self.current_cell = current_cell
        if self.maze.type == "square":
            if not(self.clicked_cell_id[0] < 0 or self.clicked_cell_id[0] >= self.maze.size or self.clicked_cell_id[1] < 0 or self.clicked_cell_id[1] >= self.maze.size):
                self.algorithm_route_current_cell_index = self.maze.algorithm_route.index(self.current_cell)
                if self.clicked_cell_id in self.maze.algorithm_route_ids:
                    if self.maze.algorithm_route_ids.index(self.clicked_cell_id) == len(self.maze.algorithm_route)-1 and self.algorithm_route_current_cell_index == len(self.maze.algorithm_route)-2:
                        return "end"
                    elif self.maze.algorithm_route_ids[self.algorithm_route_current_cell_index+1] == self.clicked_cell_id:
                        return self.maze.grid[self.clicked_cell_id[1]][self.clicked_cell_id[0]]     
                    else:
                        return "wrong_move"
                else:
                    return "wrong_move"
            else:
                return "invalid_move"
        elif self.maze.type == "hexagonal":
            print(self.clicked_cell_id)
            if not(self.clicked_cell_id[0] < 0 or self.clicked_cell_id[0] >= len(self.maze.grid[self.clicked_cell_id[1]]) or self.clicked_cell_id[1] < 0 or self.clicked_cell_id[1] >= self.maze.size):
                self.algorithm_route_current_cell_index = self.maze.algorithm_route.index(self.current_cell)
                if self.clicked_cell_id in self.maze.algorithm_route_ids:
                    if self.maze.algorithm_route_ids.index(self.clicked_cell_id) == len(self.maze.algorithm_route)-1 and self.algorithm_route_current_cell_index == len(self.maze.algorithm_route)-2:
                        return "end"
                    elif self.maze.algorithm_route_ids[self.algorithm_route_current_cell_index+1] == self.clicked_cell_id:
                        return self.maze.grid[self.clicked_cell_id[1]][self.clicked_cell_id[0]]     
                    else:
                        return "wrong_move"
                else:
                    return "wrong_move"
            else:
                return "invalid_move"
        
class sidewinder(genAlgorithm):
    name = "sidewinder"
    def __init__(self):
        pass

    def generate(self, maze):
        self.maze = maze
        if self.maze.type == "square":
            
            self.current_run = []
            for y in range(0, self.maze.size):
                self.current_run = []
                for x in range(self.maze.size):
                    cell = self.maze.grid[y][x]
                    self.current_run.append(cell)
                    end_run = False
                    connect_left = False
                    
                    if x == self.maze.size - 1:
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
                        chosen_cell = random.choice(self.current_run)
                        chosen_cell.addConnection(self.maze.grid[y-1][chosen_cell.id[0]])
                        self.current_run = []  # Clear the current run
                    elif (connect_left and x < self.maze.size - 1) or (y == 0 and x < self.maze.size - 1):  # Not the leftmost cell and decided to connect left
                        cell.addConnection(self.maze.grid[y][x+1])

            return self.maze.grid
        elif self.maze.type == "hexagonal":
            self.maze = maze
            self.current_run = []
            for y in range(self.maze.size):
                self.current_run = []
                for x in range(len(self.maze.grid[y])):
                    cell = self.maze.grid[y][x]
                    self.current_run.append(cell)
                    end_run = False
                    connect_left = False
                    
                    if x == len(self.maze.grid[y]) - 1:
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
                        chosen_cell = random.choice(self.current_run)
                        if chosen_cell.id[0] >= len(self.maze.grid[chosen_cell.id[1]-1]):
                            chosen_cell.addConnection(self.maze.grid[chosen_cell.id[1]-1][len(self.maze.grid[y-1])-1])
                        elif chosen_cell.id[0] == 0:
                            chosen_cell.addConnection(self.maze.grid[chosen_cell.id[1]-1][0])
                        else:
                            if y % 2 == 0:
                                chosen_cell.addConnection(self.maze.grid[chosen_cell.id[1]-1][chosen_cell.id[0]])
                            else:
                                chosen_cell.addConnection(self.maze.grid[chosen_cell.id[1]-1][chosen_cell.id[0]])
                        self.current_run = []
                    elif (connect_left and x < len(self.maze.grid[y]) - 1) or (y == 0 and x < len(self.maze.grid[y]) - 1): # if not the leftmost cell and decided to connect left

                        cell.addConnection(self.maze.grid[y][x+1])
            return self.maze.grid
        elif self.maze.type == "triangular":
            self.maze = maze
            self.current_run = []
            for y in range(self.maze.size):
                self.current_run = []
                for x in range(len(self.maze.grid[y])):
                    cell = self.maze.grid[y][x]
                    self.current_run.append(cell)
                    end_run = False
                    connect_left = False
                    if x == len(self.maze.grid[y]) - 1:
                        end_run = True
                    else:
                        decision = random.randint(0, 1)
                        if decision == 0:
                            end_run = True
                        else:
                            connect_left = True
                    if end_run and y != 0:
                        self.x, self.y = random.choice(self.current_run).id
                        # if ((self.x) % 2 == 1 and (self.y)%2 == 0) or ((self.x) % 2 == 0 and (self.y)%2 == 1):
                        #     self.x -= 1
                        self.maze.grid[self.y][self.x].addConnection(self.maze.grid[self.y-1][self.x])
                        self.current_run = []
                    elif (connect_left and x < len(self.maze.grid[y]) - 1) or (y == 0 and x < len(self.maze.grid[y]) - 1):
                        cell.addConnection(self.maze.grid[y][x+1])
            return self.maze.grid
        
    
class binary_tree(genAlgorithm):
    name = "binary_tree"
    def __init__(self):
        pass
    def generate(self, maze):
        self.maze = maze
        if self.maze.type == "square":
            for y in range(self.maze.size):
                for x in range(self.maze.size):
                    cell = self.maze.grid[y][x]
                    if y == 0 and x == 0:
                        pass
                    elif y == 0:
                        cell.addConnection(self.maze.grid[y][x-1])
                    elif x == 0:
                        cell.addConnection(self.maze.grid[y-1][x])
                    else:
                        decision = random.randint(0, 1)
                        if decision == 0:
                            cell.addConnection(self.maze.grid[y][x-1])
                        else:
                            cell.addConnection(self.maze.grid[y-1][x])
            return self.maze.grid
        elif self.maze.type == "hexagonal":
            for y in range(self.maze.size):
                for x in range(len(self.maze.grid[y])):
                    cell = self.maze.grid[y][x]
                    if y == 0 and x == 0:
                        pass
                    elif y == 0:
                        cell.addConnection(self.maze.grid[y][x-1])
                    elif x == 0:
                        cell.addConnection(self.maze.grid[y-1][x])
                    else:
                        decision = random.randint(0, 1)
                        if decision == 0:
                            cell.addConnection(self.maze.grid[y][x-1])
                        else:
                            if y % 2 == 0 and x == len(self.maze.grid[y-1]):
                                cell.addConnection(self.maze.grid[y-1][x-1])
                            else:
                                cell.addConnection(self.maze.grid[y-1][x])
            return self.maze.grid
     


