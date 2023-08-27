import pygame as pg
import Mazes
import time
from abc import ABC, abstractmethod

class UI():
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0 , 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    HOVER_COLOUR = (200, 200, 200)
    TITLE_DICT = {"sidewinder": "Sidewinder", "binary tree": "Binary Tree", "depth_first": "Depth First Search", "breadth_first": "Breadth First Search", "manual": "Manual solve"}
    

   

    INSTRUCTIONS = {
        "Breadth First Search": "Breadth First Search is a search algorithm that traverses the maze by exploring all of the neighbour cells of the current cell before moving on to the next cell.",
        "Depth First Search": "Depth First Search is a search algorithm that traverses the maze by exploring the first neighbour cell of the current cell before moving on to the next cell.",
        "Manual solve": "Manual solve allows the user to solve the maze themselves. Use the arrow keys to move the cell around the maze. The cell can only move to a cell that is connected to it. Have fun!",
    }
    PSUEDOCODE = {
        "Breadth First Search": "1. Add the starting cell to the queue\n2. While the queue is not empty:\n\t3. Remove the first cell from the queue\n\t4. If the cell is the end cell, return the path\n\t5. For each neighbour of the cell:\n\t\t6. If the neighbour has not been visited:\n\t\t\t7. Add the neighbour to the queue\n\t\t\t8. Set the neighbour's parent to be the current cell\n9. Return that no path exists",
        "Depth First Search": "1. Add the starting cell to the stack\n2. While the stack is not empty:\n\t3. Remove the first cell from the stack\n\t4. If the cell is the end cell, return the path\n\t5. For each neighbour of the cell:\n\t\t6. If the neighbour has not been visited:\n\t\t\t7. Add the neighbour to the stack\n\t\t\t8. Set the neighbour's parent to be the current cell\n9. Return that no path exists",
        "Manual solve": ""
    }

    def __init__(self):
        pass

    
        
    def render_multiline_text(self, font, text, x, y, color, spacing=1):
        lines = text.split('\n')
        currY = y
        
        for line in lines:
            # Handle tabs by adding additional spacing
            num_tabs = line.count('\t')
            currX = x + num_tabs * 40  # 40 is the additional space for each tab. Adjust as needed.
            line = line.replace('\t', '')  # Remove tab characters from the line

            # Render the line
            self.screen.blit(font.render(line, True, color), (currX, currY))
            
            # Move the Y position down for the next line
            currY += font.size(line)[1] + spacing

    def render_text(self, font, words, x, y, color, spacing=4):
        currX, currY = x, y
        # if the x goes off the screen, move to the next line, words should not be cut off
        for word in words:
            word_width, word_height = font.size(word)
            if currX + word_width > self.width:
                currY += font.size(word)[1] 
                currX = x
            self.screen.blit(font.render(word, True, color), (currX, currY))
            currX += word_width + spacing
            

    def render_instructions(self):
        self.instructions_font = pg.font.SysFont('Arial', 20)
        self.instructions_text = self.INSTRUCTIONS[self.title_text].split(" ")
        self.render_text(self.instructions_font, self.instructions_text, self.maze_width + 10, 100, self.BLACK)
        self.psuedocode_font = pg.font.SysFont('Arial', 20)
        self.psuedocode_text = self.PSUEDOCODE[self.title_text]
        self.render_multiline_text(self.psuedocode_font, self.psuedocode_text, self.maze_width + 10, 300, self.BLACK)

    def cell_hover(self):
        self.mouse_pos_x, self.mouse_pos_y = pg.mouse.get_pos()
        
        if self.mouse_pos_x < self.maze_width and self.mouse_pos_y < self.maze_height and self.mouse_pos_x > 0 and self.mouse_pos_y > 0:
            try:
                self.cell_width = self.maze_width // self.maze.size
                self.cell_height = self.maze_height // self.maze.size
                self.cell_x = self.mouse_pos_x // self.cell_width
                self.cell_y = self.mouse_pos_y // self.cell_height
                self.cell = self.maze.grid[self.cell_y][self.cell_x]
                pg.draw.rect(self.screen, self.HOVER_COLOUR , (self.cell_x * self.cell_width, self.cell_y * self.cell_height, self.cell_width, self.cell_height), 2)
                pg.mouse.set_cursor(*pg.cursors.broken_x)
            except:
                pass
            
    def displaySide(self):
        pg.draw.rect(self.screen, (200, 200, 200), (self.maze_width, 0, self.side_width, self.side_height))
        self.title_font = pg.font.SysFont('Arial', 30)
        
        self.title_text = self.TITLE_DICT[self.maze.solve_algorithm_name]

        # center align in the side panel
        self.render_text(self.title_font, [self.title_text], self.maze_width + self.side_width//2 - self.title_font.size(self.title_text)[0]//2, 50, self.BLACK)       
        self.render_instructions()

    def highlightVisitedCells(self):
        for cell in self.token_visited_cells_coords:
            pg.draw.rect(self.screen, self.YELLOW, (cell[0], cell[1], self.cell_width - self.cell_width*0.2, self.cell_height - self.cell_height*0.2), 2)

    def displayMaze(self):
        self.screen.fill(self.WHITE)
        self.cell_width = self.maze_width // self.maze.size
        self.cell_height = self.maze_height // self.maze.size
        
        for y in range(self.maze.size):
            for x in range(self.maze.size):
                cell = self.maze.grid[y][x]
                
                if y == 0 or self.maze.grid[y-1][x] not in cell.connections:
                    pg.draw.line(self.screen, self.BLACK, (x *  self.cell_width, y *  self.cell_height), 
                                                ((x+1) *  self.cell_width, y *  self.cell_height))
              
                if x == 0 or not(str(self.maze.grid[y][x-1]) in [str(i) for i in cell.connections]):
                    pg.draw.line(self.screen, self.RED, (x *  self.cell_width, y *  self.cell_height), 
                                                (x *  self.cell_width, (y+1) *  self.cell_height))
        
        pg.draw.circle(self.screen, self.GREEN, (self.current_cell.id[0] * self.cell_width + self.cell_width//2, self.current_cell.id[1] * self.cell_height + self.cell_height//2), self.cell_width//4)
        self.token_visited_cells_coords.append((self.current_cell.id[0] * self.cell_width + self.cell_width*0.1, self.current_cell.id[1] * self.cell_height + self.cell_height*0.1))
        self.highlightVisitedCells()
        
    def pygameLoop(self):
        pg.init()
        self.screen = pg.display.set_mode((self.width, self.height))
        self.running = True
        self.screen.fill(self.WHITE)
        self.current_cell = self.maze.grid[0][0]
        self.token_visited_cells_coords = []
        while self.running:
            
            self.displayMaze()  
            self.displaySide()
            self.cell_hover()
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    
                    if event.key == pg.K_LEFT:
                        self.solve_step_return_value = self.maze.solve_step((self.current_cell.id[0]-1, self.current_cell.id[1]), self.current_cell)
                    elif event.key == pg.K_RIGHT:
                        self.solve_step_return_value = self.maze.solve_step((self.current_cell.id[0]+1, self.current_cell.id[1]), self.current_cell)
                    elif event.key == pg.K_UP:
                        self.solve_step_return_value = self.maze.solve_step((self.current_cell.id[0], self.current_cell.id[1]-1), self.current_cell)
                    elif event.key == pg.K_DOWN:
                        self.solve_step_return_value = self.maze.solve_step((self.current_cell.id[0], self.current_cell.id[1]+1), self.current_cell)
                    elif event.key == pg.K_SPACE:
                        self.solve_step_return_value = self.maze.solve_step("space", self.current_cell)
                    if self.solve_step_return_value == "end":
                        print("Congratulations! You solved the maze!")
                        self.running = False
                    elif self.solve_step_return_value == "invalid_move":
                        print("Invalid move!")
                    elif self.solve_step_return_value == "wrong_move":
                        print("Wrong move!")

                    else:
                        self.current_cell = self.solve_step_return_value
                elif event.type == pg.MOUSEBUTTONDOWN:
                    x, y = pg.mouse.get_pos()
                    if x < self.maze_width:
                        self.solve_step_return_value = self.maze.solve_step((x//self.cell_width, y//self.cell_height), self.current_cell)
                        if self.solve_step_return_value == "end":
                            self.current_cell = self.maze.grid[self.maze.size-1][self.maze.size-1]
                            self.displayMaze()
                            pg.display.flip()
                            print("Congratulations! You solved the maze!")

                            self.running = False
                        elif self.solve_step_return_value == "invalid_move":
                            print("Invalid move!")
                        elif self.solve_step_return_value == "wrong_move":
                            print("Wrong move!")
                        else:
                            self.current_cell = self.solve_step_return_value
            self.screen.fill(self.WHITE)


        pg.quit()


    def run(self):
        pass


class TerminalUI(UI):

    def __init__(self):
        self.maze = None
        self.width, self.height = 1200, 1000

        self.maze_width, self.maze_height = 2*(self.width//3), self.height
        self.side_width, self.side_height = self.width - self.maze_width, self.height
    
    def Hello_world(self):
        print("Hello world!")
    
    def run(self):
        self.gen_algorithms = ["sidewinder", "binary_tree"]
        self.solve_algorithms = ["depth_first", "breadth_first", "manual"]

        genAlgorithm = input("Please choose an algorithm to generate the maze, 1 for sidewinder, 2 for binary tree: ")
        if genAlgorithm != "1" and genAlgorithm != "2":
            genAlgorithm = input("Please input a valid option, 1 for sidewinder, 2 for binary tree: ")
        
        solveAlgorithm = input("Please choose an algorithm to solve the maze, 1 for DFS, 2 for BFS, 3 for solving manually: ")
        if solveAlgorithm not in ["1", "2", "3"]:
            solveAlgorithm = input("Please input a valid option, 1 for DFS, 2 for BFS, 3 for manual solving: ")
        
        mazeSize = input("Please input the size of the square maze: ")
        if not mazeSize.isdigit() or int(mazeSize) < 3 or int(mazeSize) > 100:
            mazeSize = input("Please input a valid size, between 3 and 100: ")

        self.maze = Mazes.Maze(mazeType="square", size=int(mazeSize), gen_algorithm=self.gen_algorithms[int(genAlgorithm)-1], solve_algorithm=self.solve_algorithms[int(solveAlgorithm)-1])

        self.maze.generate()
        
        self.pygameLoop()

    

