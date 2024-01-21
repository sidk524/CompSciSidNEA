from abc import ABC, abstractmethod
import random
import pygame as pg
import math

class Cell:
    def __init__(self, maxConnections, ID):
        """
        Initializes a Cell object.

        Args:
            maxConnections (int): The maximum number of connections a cell can have.
            ID (str): The unique identifier for the cell.
        """
        self.__connections = []
        self.__maxConnections = maxConnections
        self.__id = ID
        self.__parent = None

    def addConnection(self, cell):
        """
        Adds a connection between this cell and another cell.

        Args:
            cell (Cell): The cell to be connected.

        Notes:
            - The connection will only be added if the maximum number of connections has not been reached.
            - The connection will only be added if the other cell is not already connected to this cell.
            - The connection will only be added if the other cell has a different ID than this cell.
        """
        if len(self.__connections) < self.__maxConnections and not (cell in self.__connections) and self.getID() != cell.getID():
            self.__connections.append(cell)
            cell.addConnection(self)
       

    def removeConnection(self, cell):
        """
        Removes a connection between this cell and another cell.

        Args:
            cell (Cell): The cell to be disconnected.
        """
        if cell in self.__connections:
            self.__connections.remove(cell)
            cell.removeConnection(self)

    def checkConnection(self, cell):
        """
        Checks if there is a connection between this cell and another cell.

        Args:
            cell (Cell): The cell to check for connection.

        Returns:
            bool: True if there is a connection, False otherwise.
        """
        if cell in self.__connections:
            return True
        else:
            return False     

    def setParent(self, cell):  
        """
        Sets the parent cell of this cell.

        Args:
            cell (Cell): The parent cell.
        """
        self.__parent = cell

    def getParent(self):
        """
        Gets the parent cell of this cell.

        Returns:
            Cell: The parent cell.
        """
        return self.__parent
    
    def getID(self):
        """
        Gets the ID of this cell.

        Returns:
            tuple: The ID of the cell.
        """
        return tuple(map(int, (self.__id)))
    
    def getConnections(self):
        """
        Gets the connections of this cell.

        Returns:
            list: The list of connected cells.
        """
        return self.__connections

    def __str__(self):
        """
        Returns a string representation of this cell.

        Returns:
            str: The string representation of the cell.
        """
        return str(self.__id)

    def __repr__(self):
        """
        Returns a string representation of this cell.

        Returns:
            str: The string representation of the cell.
        """
        return str(self.__id)
        

class Maze:
    MAZETYPES = ["square", "hexagonal", "triangular", "octagonal"]
    def __init__(self, mazeType, gen_algorithm, solve_algorithm, mazeWidth, mazeHeight, mazeGrid=None):
        """
        Initializes the Maze object.

        Args:
            mazeType (int): The type of maze to generate.
            gen_algorithm (str): The name of the maze generation algorithm.
            solve_algorithm (str): The name of the maze solving algorithm.
            mazeWidth (int): The width of the maze.
            mazeHeight (int): The height of the maze.
            mazeGrid (dict, optional): The grid representation of the maze. Defaults to None.
        """
        self.__type = self.MAZETYPES[mazeType-1]
        self.__mazeWidth = mazeWidth
        self.__mazeHeight = mazeHeight
        self.__gen_algorithm_name = gen_algorithm
        self.__solve_algorithm_name = solve_algorithm
        self.__AlgorithmFactory = AlgorithmFactory(self.__gen_algorithm_name, self.__solve_algorithm_name)
        self.__genAlgorithm = self.__AlgorithmFactory.getGenAlgorithm()
        self.__solveAlgorithm = self.__AlgorithmFactory.getSolveAlgorithm()
        self.__gridFromOpponent = mazeGrid

    def initialiseMaze(self):
        """
        Initializes the maze grid based on the specified maze type.

        Parameters:
        - self: The Maze object.

        Returns:
        - None
        """
        if self.__type == "square":
            # Create a square grid
            self.__grid = dict()
            for y in range(self.__mazeHeight):
                self.__grid[y] = []
                for x in range(self.__mazeWidth):
                    self.__grid[y].append(Cell(4, (x,y)))

        elif self.__type == "hexagonal":
            # Create a hexagonal grid
            self.__grid = dict()
            for y in range(self.__mazeHeight):
                self.__grid[y] = []
                if y % 2 == 0:
                    # Even rows have full width
                    for x in range(self.__mazeWidth):
                        self.__grid[y].append(Cell(6, (x,y)))
                else:
                    # Odd rows have width-1
                    for x in range(self.__mazeWidth-1):
                        self.__grid[y].append(Cell(6, (x,y)))

        elif self.__type == "triangular":
            # Create a triangular grid
            self.__grid = dict()
            for y in range(self.__mazeHeight):
                self.__grid[y] = []
                for x in range(self.__mazeWidth):
                    self.__grid[y].append(Cell(3, (x,y)))
    
    def getSolveAlgorithmName(self):
        """
        Returns the name of the solve algorithm used in the maze.

        Parameters:
        - self: The Maze object.

        Returns:
        - str: The name of the solve algorithm.
        """
        return self.__solve_algorithm_name
    
    def getGenAlgorithmName(self):
        """
        Returns the name of the generation algorithm used in the maze.

        Parameters:
        - self: The Maze object.

        Returns:
        - str: The name of the generation algorithm.
        """
        return self.__gen_algorithm_name

    def generate(self):
        """
        Generates the maze by initializing the maze, generating the grid, and finding a valid path.

        Parameters:
        - self: The Maze object.

        Returns:
        - None
        """
        self.initialiseMaze()  # Initialize the maze
        print(self.__gridFromOpponent)

        if self.__gridFromOpponent == None:
            self.__grid = self.__genAlgorithm.generate(self)  # Generate the grid using the generation algorithm
            self.__curr = self.__solveAlgorithm.findValidPath(self)  # Find a valid path using the solve algorithm
            gen = 0
            while self.__curr == False:
                self.__genAlgorithm.generate(self)  # Regenerate the grid
                self.__curr = self.__solveAlgorithm.findValidPath(self)  # Find a valid path
                gen += 1
            print(gen)
        else:
            self.__grid = self.__gridFromOpponent  # Use the grid provided by the opponent
            self.__curr = self.__solveAlgorithm.findValidPath(self)  # Find a valid path

        self.__validPath, self.__programStates = self.__curr
        self.__algorithm_route = [s[0] for s in self.__programStates]  # Extract the algorithm route from the program states
        self.__algorithm_route_ids = [i.getID() for i in self.__algorithm_route]  # Extract the IDs of the cells in the algorithm route


    class Maze:
        def getHint(self, current_cell):
            """
            Returns the hint for the given current cell.

            Parameters:
            - current_cell (Cell): The current cell for which the hint is needed.

            Returns:
            - str: The hint for the current cell.

            """
            # Iterate through the algorithm route IDs
            for n, i in enumerate(self.__algorithm_route_ids):
                # Check if the current cell ID matches the algorithm route ID
                if i == current_cell.getID():
                    # Return the hint for the next cell in the algorithm route
                    return self.__algorithm_route[n+1]
            
    def getNeighbours(self, cell):
        """
        Returns a list of neighboring cells for the given cell.

        Parameters:
        - cell: The cell for which to find neighbors.

        Returns:
        - List of neighboring cells.
        """
        self.__neighbours = []
        self.__x = cell.getID()[0]
        self.__y = cell.getID()[1]
        
        # Determine the potential neighbors based on the maze type
        if self.__type == "square":
            self.__potential_neighbours = [(self.__x + 1, self.__y), (self.__x - 1, self.__y), (self.__x, self.__y + 1), (self.__x, self.__y - 1)]
        elif self.__type == "hexagonal":
            self.__potential_neighbours = [(self.__x + 1, self.__y), (self.__x - 1, self.__y), (self.__x, self.__y + 1), (self.__x, self.__y - 1), (self.__x + 1, self.__y - 1), (self.__x - 1, self.__y + 1), (self.__x + 1, self.__y + 1), (self.__x - 1, self.__y - 1)]
        elif self.__type == "triangular":
            self.__potential_neighbours = [(self.__x + 1, self.__y), (self.__x - 1, self.__y), (self.__x, self.__y + 1), (self.__x, self.__y - 1), (self.__x + 1, self.__y - 1), (self.__x - 1, self.__y + 1), (self.__x + 1, self.__y + 1), (self.__x - 1, self.__y - 1)]
            
        # Check if each potential neighbor is valid and add it to the list of neighbors
        for i in self.__potential_neighbours:
            if i[0] >= 0 and i[1] >= 0 and i[1] < self.__mazeHeight and i[0] < len(self.__grid[i[1]]):
                self.__potential_neighbour = self.__grid[i[1]][i[0]]
                if self.__potential_neighbour in cell.getConnections():
                    self.__neighbours.append(self.__potential_neighbour)
        
        return self.__neighbours
        

    def getDistanceMap(self, cell):
        """
        Returns a dictionary containing the distances from the given cell to all other cells in the maze.
        Uses breadth-first search to find the shortest path to each cell.

        Parameters:
        - cell: The starting cell.

        Returns:
        - dict: A dictionary where the keys are the cell IDs and the values are the distances from the starting cell.
        """

        finalCoord = cell.getID()
        distances = dict()

        # Iterate through all cells in the maze
        for y in range(self.__mazeHeight):
            for x in range(len(self.getGrid()[y])):
                currCell = self.__grid[y][x]
                currCell.setParent(None)

                # Skip the current cell if it is the final coordinate
                if currCell.getID() == finalCoord:
                    continue

                self.__queue = [currCell]
                self.__visitedCells = []

                # Perform breadth-first search to find the shortest path to the final coordinate
                while len(self.__queue) > 0:
                    self.__currentCell = self.__queue.pop(0)
                    self.__visitedCells.append(self.__currentCell)

                    # Check if the current cell is the final coordinate
                    if self.__currentCell.getID() == finalCoord:
                        path_length = 0
                        path_cell = self.__currentCell

                        # Calculate the path length by traversing the parent cells
                        while path_cell is not None:
                            path_length += 1
                            path_cell = path_cell.getParent()

                        distances[currCell.getID()] = path_length - 1
                        break
                    else:
                        self.__neighbours = self.getNeighbours(self.__currentCell)

                        # Add unvisited neighbors to the queue
                        if len(self.__neighbours) > 0:
                            for i in self.__neighbours:
                                if not (i in self.__visitedCells) and not (i in self.__queue):
                                    i.setParent(self.__currentCell)
                                    self.__queue.append(i)

        return distances

 
    def getProgramState(self, current_cell):
        """
        Returns the program state associated with the given current cell.

        Parameters:
        - current_cell (Cell): The current cell to retrieve the program state for.

        Returns:
        - program_state (tuple): A tuple containing the program state information.
                                    The tuple structure is (maze_state, algorithm_state).

        Note:
        - maze_state: The state of the maze.
        - algorithm_state: The state of the solving algorithm.
        ```
        """
        for s in self.__programStates:
            if s[0].getID() == current_cell.getID():
                return s[1], s[2]

    def getSolution(self):
        """
        Returns the valid path solution of the maze.

        Returns:
        - valid_path (list): A list of cell IDs representing the valid path solution of the maze.

        """
        return self.__validPath

    def getAlgorithmRouteIDs(self):
        """
        Returns the IDs of the algorithm route.

        Returns:
        - algorithm_route_ids (list): A list of algorithm route IDs.

        """
        return self.__algorithm_route_ids
    
    def getAlgorithmRoute(self):
        """
        Returns the algorithm route.

        Returns:
        - algorithm_route (list): A list of algorithm route.
        """
        return self.__algorithm_route

    def getMazeType(self):
        """
        Returns the type of the maze.

        Returns:
        - type (str): The type of the maze.

        Example usage:
        """
        return self.__type
    
    def getMazeWidth(self):
        """
        Returns the width of the maze.

        Returns:
        - mazeWidth (int): The width of the maze.

        """
        return self.__mazeWidth
    
    def getMazeHeight(self):
        """
        Returns the height of the maze.

        Returns:
        - mazeHeight (int): The height of the maze.
        """
        return self.__mazeHeight
    
    def getGrid(self):
        """
        Returns the grid of the maze.

        Returns:
        - grid (list): A list representing the maze grid.
        """
        return self.__grid
    
    def solve_step(self, clicked_cell_id, current_cell):
        """
        Performs a step in the solving algorithm.

        Parameters:
        - clicked_cell_id (int): The ID of the clicked cell.
        - current_cell (Cell): The current cell.

        Returns:
        - result (bool): True if the step was successful, False otherwise.

        """
        return self.__solveAlgorithm.solve_step(self, clicked_cell_id, current_cell)

class AlgorithmFactory():
    solvingAlgorithms = ["breadth_first", "depth_first", "manual"]
    generatingAlgorithms = ["sidewinder", "binary_tree"]
    
    def __init__(self, genName, solveName):
        """
        Initializes an instance of AlgorithmFactory.

        Parameters:
        - genName (str): The name of the generation algorithm.
        - solveName (str): The name of the solving algorithm.
        """
        self.__genName = genName
        self.__solveName = solveName
        
    def getGenAlgorithm(self):
        """
        Returns the generation algorithm based on the specified name.

        Returns:
        - genAlgorithm (GenAlgorithm): The generation algorithm instance.

        Raises:
        - Exception: If the specified algorithm type is invalid.
        """
        if not (self.__genName in AlgorithmFactory.generatingAlgorithms):
            raise Exception("Invalid algorithm type")
        elif self.__genName == "sidewinder":
            self.__genAlgorithm = Sidewinder()
        elif self.__genName == "binary_tree":
            self.__genAlgorithm = BinaryTree()
        return self.__genAlgorithm
    
    def getSolveAlgorithm(self):
        """
        Returns the solving algorithm based on the specified name.

        Returns:
        - solveAlgorithm (SolveAlgorithm): The solving algorithm instance.

        Raises:
        - Exception: If the specified algorithm type is invalid.
        """
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
    """
    Abstract base class for generation algorithms.
    """

    @abstractmethod
    def generate(self, maze):
        """
        Generates a maze using the specified algorithm.

        Parameters:
        - maze (Maze): The maze instance to generate.

        Raises:
        - NotImplementedError: If the method is not implemented by the subclass.
        """
        pass


class SolveAlgorithm(ABC):
    
    @abstractmethod
    def findValidPath(self, maze):
        pass

    @abstractmethod
    def solve_step(self, maze, clicked_cell_id, current_cell):
        pass

    def getNeighbours(self, cell, maze):
        """
        Returns a list of neighboring cells for the given cell.

        Parameters:
        - cell: The cell for which to find neighbors.

        Returns:
        - List of neighboring cells.
        """
        self.__neighbours = []
        self.__x = cell.getID()[0]
        self.__y = cell.getID()[1]
        self.__maze = maze
        
        # Determine the potential neighbors based on the maze type
        if self.__maze.getMazeType() == "square":
            self.__potential_neighbours = [(self.__x + 1, self.__y), (self.__x - 1, self.__y), (self.__x, self.__y + 1), (self.__x, self.__y - 1)]
        elif self.__maze.getMazeType() == "hexagonal":
            self.__potential_neighbours = [(self.__x + 1, self.__y), (self.__x - 1, self.__y), (self.__x, self.__y + 1), (self.__x, self.__y - 1), (self.__x + 1, self.__y - 1), (self.__x - 1, self.__y + 1), (self.__x + 1, self.__y + 1), (self.__x - 1, self.__y - 1)]
        elif self.__maze.getMazeType() == "triangular":
            self.__potential_neighbours = [(self.__x + 1, self.__y), (self.__x - 1, self.__y), (self.__x, self.__y + 1), (self.__x, self.__y - 1), (self.__x + 1, self.__y - 1), (self.__x - 1, self.__y + 1), (self.__x + 1, self.__y + 1), (self.__x - 1, self.__y - 1)]
            
        # Check if each potential neighbor is valid and add it to the list of neighbors
        for i in self.__potential_neighbours:
            if i[0] >= 0 and i[1] >= 0 and i[1] < self.__maze.getMazeHeight() and i[0] < len(self.__maze.getGrid()[i[1]]):
                self.__potential_neighbour = self.__maze.getGrid()[i[1]][i[0]]
                if self.__potential_neighbour in cell.getConnections():
                    self.__neighbours.append(self.__potential_neighbour)
        
        return self.__neighbours

class Manual(SolveAlgorithm):
    """
    A class representing the manual solve algorithm.

    Attributes:
    - name: The name of the algorithm.

    Methods:
    - __init__(): Initializes the Manual object.
    - findValidPath(maze): Finds a valid path using the "sidewinder" and "breadth_first" algorithms.
    - solve_step(maze, clicked_cell_id, current_cell): Performs a step in the solving process.
    """

    name = "manual"

    def __init__(self):
        """
        Initializes the Manual object.
        """
        pass

    def findValidPath(self, maze):
        """
        Finds a valid path using the "sidewinder" and "breadth_first" algorithms.

        Parameters:
        - maze: The maze object.

        Returns:
        - The valid path found by the algorithm.
        """
        return AlgorithmFactory("sidewinder", "breadth_first").getSolveAlgorithm().findValidPath(maze)

    def solve_step(self, maze, clicked_cell_id, current_cell):
        """
        Performs a step in the solving process.

        Parameters:
        - maze: The maze object.
        - clicked_cell_id: The ID of the clicked cell.
        - current_cell: The current cell object.

        Returns:
        - The result of the step:
          - "invalid_move" if the move is invalid.
          - "end" if the end of the maze is reached.
          - The next cell object if the move is valid.
        """
        # Set the instance variables
        self.__maze = maze
        self.__clicked_cell_id = tuple(map(int, clicked_cell_id))
        self.__current_cell = current_cell

        # Get the neighbors of the current cell
        self.__cell_neighbours = self.getNeighbours(self.__current_cell, self.__maze)

        # Check if the clicked cell is within the maze boundaries
        if self.__clicked_cell_id[0] < 0 or self.__clicked_cell_id[0] >= len(self.__maze.getGrid()[self.__clicked_cell_id[1]]) or self.__clicked_cell_id[1] < 0 or self.__clicked_cell_id[1] >= self.__maze.getMazeHeight():
            return "invalid_move"

        # Check if the end of the maze is reached
        if self.__clicked_cell_id == (len(self.__maze.getGrid()[self.__maze.getMazeHeight() - 1]) - 1, self.__maze.getMazeHeight()-1) and self.__clicked_cell_id in [i.getID() for i in self.__cell_neighbours]:
            return "end"
        # Check if the clicked cell is a valid move
        elif self.__maze.getGrid()[self.__clicked_cell_id[1]][self.__clicked_cell_id[0]] in self.__cell_neighbours:
            return self.__maze.getGrid()[self.__clicked_cell_id[1]][self.__clicked_cell_id[0]]
        else:
            return "invalid_move"


class DepthFirst(SolveAlgorithm):
    """
    A class representing the depth-first solve algorithm.

    Attributes:
    - name: The name of the algorithm.

    Methods:
    - __init__(): Initializes the DepthFirst object.
    """

    name = "depth_first"

    def __init__(self):
        """
        Initializes the DepthFirst object.
        """
        pass
    def findValidPath(self, maze):
        """
        Finds a valid path in the maze using a depth-first search algorithm.

        Parameters:
        - maze: The maze object to search for a valid path.

        Returns:
        - path: A list of cells representing the valid path from the start to the end of the maze.
        - visitedCells: A list of visited cells during the search process.

        """
        self.__maze = maze
        self.__stack = [self.__maze.getGrid()[0][0]]  # Start the search from the top-left cell
        self.__visitedCells = []  # List to store visited cells
        self.__potentialPaths = []  # List to store potential paths

        while len(self.__stack) > 0:
            self.__currentCell = self.__stack.pop()  # Get the current cell from the stack
            self.__neighbours = self.getNeighbours(self.__currentCell, self.__maze)  # Get the neighbours of the current cell

            self.__visitedCells.append([self.__currentCell, self.__neighbours, self.__stack.copy()])  # Store the visited cell, its neighbours, and the current stack

            if self.__currentCell.getID() == (len(self.__maze.getGrid()[self.__maze.getMazeHeight() - 1]) - 1, self.__maze.getMazeHeight()-1):
                # If the current cell is the bottom-right cell, a valid path is found
                path = []
                self.__currentCell = self.__maze.getGrid()[self.__maze.getMazeHeight() - 1][-1]  # Start from the bottom-right cell
                while self.__currentCell != None:
                    path.append(self.__currentCell)  # Add the current cell to the path
                    self.__currentCell = self.__currentCell.getParent()  # Move to the parent cell
                return path, self.__visitedCells  # Return the valid path and the visited cells

            else:
                if len(self.__neighbours) > 0:
                    for i in self.__neighbours:
                        if not(i in [c[0] for c in self.__visitedCells]):
                            i.setParent(self.__currentCell)  # Set the parent of the neighbour cell to the current cell
                            self.__stack.append(i)  # Add the neighbour cell to the stack

        return False  # If no valid path is found, return False

    def solve_step(self, maze, clicked_cell_id, current_cell):
        """
        Performs a step in the solving process.

        Parameters:
        - maze: The maze object.
        - clicked_cell_id: The ID of the clicked cell.
        - current_cell: The current cell.

        Returns:
        - "end" if the clicked cell is the end of the algorithm route.
        - The clicked cell if it is the next cell in the algorithm route.
        - "wrong_move" if the clicked cell is not the next cell in the algorithm route.
        - "invalid_move" if the clicked cell is outside the maze boundaries.

        """
        self.__maze = maze
        self.__clicked_cell_id = tuple(map(int, clicked_cell_id))
        self.__current_cell = current_cell
        
        # Check if the clicked cell is within the maze boundaries
        if not(self.__clicked_cell_id[0] < 0 or self.__clicked_cell_id[0] >= len(self.__maze.getGrid()[self.__clicked_cell_id[1]]) or self.__clicked_cell_id[1] < 0 or self.__clicked_cell_id[1] >= self.__maze.getMazeHeight()):
            self.__algorithm_route_current_cell_index = self.__maze.getAlgorithmRoute().index(self.__current_cell)
            
            # Check if the clicked cell is in the algorithm route
            if self.__clicked_cell_id in self.__maze.getAlgorithmRouteIDs():
                # Check if the clicked cell is the end of the algorithm route
                if self.__maze.getAlgorithmRouteIDs().index(self.__clicked_cell_id) == len(self.__maze.getAlgorithmRoute())-1 and self.__algorithm_route_current_cell_index == len(self.__maze.getAlgorithmRoute())-2:
                    return "end"
                # Check if the clicked cell is the next cell in the algorithm route
                elif self.__maze.getAlgorithmRouteIDs()[self.__algorithm_route_current_cell_index+1] == self.__clicked_cell_id:
                    return self.__maze.getGrid()[self.__clicked_cell_id[1]][self.__clicked_cell_id[0]]
                else:
                    return "wrong_move"
            else:
                return "wrong_move"
        else:
            return "invalid_move"
class BreadthFirst(SolveAlgorithm):
    """
    A class representing the breadth-first solve algorithm.

    Attributes:
    - name: The name of the algorithm.

    Methods:
    - __init__(): Initializes the BreadthFirst object.
    """

    name = "breadth_first"

    def __init__(self):
        """
        Initializes the BreadthFirst object.
        """
        pass
    def findValidPath(self, maze):
        """
        Finds a valid path in the maze using a breadth-first search algorithm.

        Parameters:
        - maze: The maze object to search for a valid path.

        Returns:
        - path: A list of cells representing the valid path from the start to the end of the maze.
        - visitedCells: A list of visited cells during the search process.
        """

        self.__maze = maze
        self.__queue = [self.__maze.getGrid()[0][0]]  # Initialize the queue with the start cell
        self.__visitedCells = []  # List to store visited cells during the search process

        while len(self.__queue) > 0:
            self.__currentCell = self.__queue.pop(0)  # Get the current cell from the front of the queue
            self.__neighbours = self.getNeighbours(self.__currentCell, self.__maze)  # Get the neighbours of the current cell

            self.__visitedCells.append([self.__currentCell, self.__neighbours, self.__queue.copy()])  # Store the current cell, its neighbours, and the current state of the queue

            if self.__currentCell.getID() == (len(self.__maze.getGrid()[self.__maze.getMazeHeight() - 1]) - 1, self.__maze.getMazeHeight() - 1):
                # If the current cell is the end cell, construct the path from the end cell to the start cell
                path = []
                self.__currentCell = self.__maze.getGrid()[self.__maze.getMazeHeight() - 1][-1]
                while self.__currentCell != None:
                    path.append(self.__currentCell)
                    self.__currentCell = self.__currentCell.getParent()
                return path, self.__visitedCells
            else:
                if len(self.__neighbours) > 0:
                    for i in self.__neighbours:
                        if not(i in [c[0] for c in self.__visitedCells]) and not (i in self.__queue):
                            i.setParent(self.__currentCell)  # Set the parent of the neighbour cell to the current cell
                            self.__queue.append(i)  # Add the neighbour cell to the queue
        return False  # If no valid path is found, return False

    def solve_step(self, maze, clicked_cell_id, current_cell):
        """
        Performs a step in the maze solving process.

        Parameters:
        - maze: The maze object to solve.
        - clicked_cell_id: The ID of the clicked cell.
        - current_cell: The current cell in the maze solving process.

        Returns:
        - "end" if the clicked cell is the end cell.
        - The next cell to move to if the clicked cell is in the correct path.
        - "wrong_move" if the clicked cell is not in the correct path.
        - "invalid_move" if the clicked cell is outside the maze boundaries.
        """
        self.__maze = maze
        self.__clicked_cell_id = tuple(map(int, clicked_cell_id))
        self.__current_cell = current_cell

        # Check if the clicked cell is within the maze boundaries
        if not(self.__clicked_cell_id[0] < 0 or self.__clicked_cell_id[0] >= len(self.__maze.getGrid()[self.__clicked_cell_id[1]]) or self.__clicked_cell_id[1] < 0 or self.__clicked_cell_id[1] >= self.__maze.getMazeHeight()):
            self.__algorithm_route_current_cell_index = self.__maze.getAlgorithmRoute().index(self.__current_cell)

            # Check if the clicked cell is in the correct path
            if self.__clicked_cell_id in self.__maze.getAlgorithmRouteIDs():
                if self.__maze.getAlgorithmRouteIDs().index(self.__clicked_cell_id) == len(self.__maze.getAlgorithmRoute())-1 and self.__algorithm_route_current_cell_index == len(self.__maze.getAlgorithmRoute())-2:
                    return "end"  # Return "end" if the clicked cell is the end cell
                elif self.__maze.getAlgorithmRouteIDs()[self.__algorithm_route_current_cell_index+1] == self.__clicked_cell_id:
                    return self.__maze.getGrid()[self.__clicked_cell_id[1]][self.__clicked_cell_id[0]]  # Return the next cell to move to
                else:
                    return "wrong_move"  # Return "wrong_move" if the clicked cell is not in the correct path
            else:
                return "wrong_move"  # Return "wrong_move" if the clicked cell is not in the correct path
        else:
            return "invalid_move"  # Return "invalid_move" if the clicked cell is outside the maze boundaries
class Sidewinder(GenAlgorithm):
    """
    A class representing the sidewinder generation algorithm.

    Attributes:
    - name: The name of the algorithm.

    Methods:
    - __init__(): Initializes the Sidewinder object.
    - generate(maze): Generates a maze using the sidewinder algorithm.
    """

    name = "sidewinder"

    def __init__(self):
        """
        Initializes the Sidewinder object.
        """
        pass
    def generate(self, maze):
        """
        Generates a maze using the Sidewinder algorithm.

        Args:
        - maze: The maze object to generate.

        Returns:
        - The generated maze grid.
        """
        self.__maze = maze
        self.__current_run = []

        for y in range(self.__maze.getMazeHeight()):
            self.__current_run = []

            for x in range(len(self.__maze.getGrid()[y])):
                cell = self.__maze.getGrid()[y][x]
                self.__current_run.append(cell)
                end_run = False
                connect_left = False

                if x == len(self.__maze.getGrid()[y]) - 1 and self.__maze.getMazeType() != "hexagonal":
                    # If it's the last cell in the row, end the run
                    end_run = True
                else:
                    # Randomly decide to connect to the left or end the run
                    decision = random.randint(0, 1)
                    if decision == 0:
                        end_run = True
                    else:
                        connect_left = True

                if self.__maze.getMazeType() == "square":
                    if end_run and y != 0:
                        chosen_cell = random.choice(self.__current_run)
                        chosen_cell.addConnection(self.__maze.getGrid()[y-1][chosen_cell.getID()[0]])
                        self.__current_run = []  # Clear the current run
                    elif (connect_left and x < self.__maze.getMazeWidth()-1) or (y == 0 and x < self.__maze.getMazeWidth()-1):  # Not the leftmost cell and decided to connect left
                        cell.addConnection(self.__maze.getGrid()[y][x+1])

                elif self.__maze.getMazeType() == "hexagonal":
                    if end_run and y != 0:
                        chosen_cell = random.choice(self.__current_run)
                        if chosen_cell.getID()[0] >= len(self.__maze.getGrid()[chosen_cell.getID()[1]-1]) and chosen_cell.getID()[0] != 0 and chosen_cell.getID()[1] != 0:
                            chosen_cell.addConnection(self.__maze.getGrid()[chosen_cell.getID()[1]][len(self.__maze.getGrid()[chosen_cell.getID()[1]-1])])
                        elif chosen_cell.getID()[0] == 0:
                            chosen_cell.addConnection(self.__maze.getGrid()[chosen_cell.getID()[1]-1][0])
                        else:
                            x_offset = random.randint(0, 1)
                            if y % 2 == 0 and not(chosen_cell.getID()[0] == 0 and x_offset == 1):
                                chosen_cell.addConnection(self.__maze.getGrid()[chosen_cell.getID()[1]-1][chosen_cell.getID()[0]+(-1*x_offset)])
                            else:
                                chosen_cell.addConnection(self.__maze.getGrid()[chosen_cell.getID()[1]-1][chosen_cell.getID()[0] + x_offset])
                        self.__current_run = []
                    elif (connect_left and x != 0) or (y == 0 and x != 0): # if not the leftmost cell and decided to connect left
                        cell.addConnection(self.__maze.getGrid()[y][x-1])

                elif self.__maze.getMazeType() == "triangular":
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
                            self.__maze.getGrid()[self.__y][self.__x+1].addConnection(self.__maze.getGrid()[self.__y-1][self.__x+1])
                        self.__current_run = []
                    elif (connect_left and x < len(self.__maze.getGrid()[y]) - 1) or (y == 0 and x < len(self.__maze.getGrid()[y]) - 1):
                        cell.addConnection(self.__maze.getGrid()[y][x+1])
                    else:
                        print("Here")

        return self.__maze.getGrid()
 
        
class BinaryTree(GenAlgorithm):
    """
    A class representing the binary tree generation algorithm.

    Attributes:
    - name: The name of the algorithm.

    Methods:
    - __init__(): Initializes the BinaryTree object.
    - generate(maze): Generates a maze using the binary tree algorithm.
    """

    name = "binary_tree"

    def __init__(self):
        """
        Initializes the BinaryTree object.
        """
        pass

    def generate(self, maze):
        """
        Generates a maze using the binary tree algorithm.

        Args:
        - maze: The maze object to generate.

        Returns:
        None
        """
    
        self.__maze = maze

        # Iterate through each cell in the maze
        for y in range(self.__maze.getMazeHeight()):
            for x in range(len(self.__maze.getGrid()[y])):
                cell = self.__maze.getGrid()[y][x]

                # If the cell is at the leftmost column, do nothing
                if x == 0:
                    continue

                # If the cell is at the topmost row, connect it to the cell on its left
                elif y == 0:
                    cell.addConnection(self.__maze.getGrid()[y][x-1])
                    continue    

                else:
                    # Randomly decide whether to connect the cell to the cell on its left or above
                    decision = random.randint(0, 1)

                # Connect cells based on the maze type
                if self.__maze.getMazeType() == "square":
                    if decision == 0:
                        cell.addConnection(self.__maze.getGrid()[y][x-1])
                    else:
                        cell.addConnection(self.__maze.getGrid()[y-1][x])
                    
                elif self.__maze.getMazeType() == "hexagonal":
                    if decision == 0:
                        cell.addConnection(self.__maze.getGrid()[y][x-1])
                    else:
                        if y % 2 == 0 and x == len(self.__maze.getGrid()[y-1]):
                            cell.addConnection(self.__maze.getGrid()[y-1][x-1])
                        else:
                            cell.addConnection(self.__maze.getGrid()[y-1][x])
                
                elif self.__maze.getMazeType() == "triangular":
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
                            self.__maze.getGrid()[y][x-1].addConnection(self.__maze.getGrid()[y-1][x-1])

        return self.__maze.getGrid()
