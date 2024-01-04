import typing
from PyQt5.QtCore import Qt
import pygame as pg
import Mazes
import time
from abc import ABC, abstractmethod
import math
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
import sys

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
        self.__maze = None
        
    def render_multiline_text(self, font, text, x, y, color, spacing=1):
        lines = text.split('\n')
        currY = y
        
        for line in lines:
            # Handle tabs by adding additional spacing
            num_tabs = line.count('\t')
            currX = x + num_tabs * 40  # 40 is the additional space for each tab. Adjust as needed.
            line = line.replace('\t', '')  # Remove tab characters from the line

            # Render the line
            self.__screen.blit(font.render(line, True, color), (currX, currY))
            
            # Move the Y position down for the next line
            currY += font.size(line)[1] + spacing

    def render_text(self, font, words, x, y, color, spacing=4):
        currX, currY = x, y
        # if the x goes off the screen, move to the next line, words should not be cut off
        for word in words:
            word_width, word_height = font.size(word)
            if currX + word_width > self.__width:
                currY += font.size(word)[1] 
                currX = x
            self.__screen.blit(font.render(word, True, color), (currX, currY))
            currX += word_width + spacing
            

    def render_instructions(self):
        self.__instructions_font = pg.font.SysFont('Arial', 20)
        self.__instructions_text = self.INSTRUCTIONS[self.__title_text].split(" ")
        self.render_text(self.__instructions_font, self.__instructions_text, self.__maze_width + 10, 100, self.BLACK)
        self.__psuedocode_font = pg.font.SysFont('Arial', 20)
        self.__psuedocode_text = self.PSUEDOCODE[self.__title_text]
        self.render_multiline_text(self.__psuedocode_font, self.__psuedocode_text, self.__maze_width + 10, 300, self.BLACK)
    def is_inside_polygon(self, x, y, poly):
        """Check if a point (x, y) is inside a polygon defined by a list of vertices [(x1, y1), (x2, y2), ...]"""
        n = len(poly)
        inside = False

        p1x, p1y = poly[0]
        for i in range(n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside
    
    def cell_hover(self, clicked=False):
        self.__mouse_pos_x, self.__mouse_pos_y = pg.mouse.get_pos()
        if self.maze.getMazeType() == "square":
            if self.__mouse_pos_x < self.__maze_width and self.__mouse_pos_y < self.__maze_height and self.__mouse_pos_x > 0 and self.__mouse_pos_y > 0:
                try:
                    self.__cell_width = self.__maze_width // self.maze.getMazeSize()
                    self.__cell_height = self.__maze_height // self.maze.getMazeSize()
                    self.__cell_x = self.__mouse_pos_x // self.__cell_width
                    self.__cell_y = self.__mouse_pos_y // self.__cell_height
                    self.__cell = self.maze.getGrid()[self.__cell_y][self.__cell_x]
                    pg.draw.rect(self.__screen, self.HOVER_COLOUR , (self.__cell_x * self.__cell_width, self.__cell_y * self.__cell_height, self.__cell_width, self.__cell_height), 2)
                    pg.mouse.set_cursor(*pg.cursors.broken_x)
                except:
                    pass
        elif self.maze.getMazeType() == "hexagonal":
            for p in self.__points:
                if self.__mouse_pos_x > self.__maze_width and self.__mouse_pos_y > self.__maze_height:
                    break
                if self.is_inside_polygon(self.__mouse_pos_x, self.__mouse_pos_y, p):
                    
                    self.__cell_x = self.__points.index(p)
                    counter = 0
                    flag = False
                    
                    for y in range(self.maze.getMazeSize()):
                        
                        for x in range(len(self.maze.getGrid()[y])):
              
                            if counter == self.__cell_x:
                                self.__cell = self.maze.getGrid()[y][x]
                                

                                flag = True
                                break
                            counter += 1
                        if flag:
                            break                            
                    pg.draw.polygon(self.__screen, self.HOVER_COLOUR, p, 2)
                    pg.mouse.set_cursor(*pg.cursors.broken_x)
                    if clicked:
                        return self.__cell
                    break
        elif self.maze.getMazeType() == "triangular":
            for p in self.__points:
                if self.__mouse_pos_x > self.__maze_width and self.__mouse_pos_y > self.__maze_height:
                    break
                if self.is_inside_polygon(self.__mouse_pos_x, self.__mouse_pos_y, p):
                    
                    self.__cell_x = self.__points.index(p)
                    counter = 0
                    flag = False
                    
                    for y in range(self.maze.getMazeSize()):
                        
                        for x in range(len(self.maze.getGrid()[y])):
              
                            if counter == self.__cell_x:
                                self.__cell = self.maze.getGrid()[y][x]
                                

                                flag = True
                                break
                            counter += 1
                        if flag:
                            break                            
                    pg.draw.polygon(self.__screen, self.HOVER_COLOUR, p, 2)
                    pg.mouse.set_cursor(*pg.cursors.broken_x)
                    if clicked:
                        return self.__cell
                    break
                

    def displaySide(self):
        pg.draw.rect(self.__screen, (200, 200, 200), (self.__maze_width, 0, self.__side_width, self.__side_height))
        self.__title_font = pg.font.SysFont('Arial', 30)
        
        self.__title_text = self.TITLE_DICT[self.maze.getSolveAlgorithmName()]

        # center align in the side panel
        self.render_text(self.__title_font, [self.__title_text], self.__maze_width + self.__side_width//2 - self.__title_font.size(self.__title_text)[0]//2, 50, self.BLACK)       
        self.render_instructions()

    def highlightVisitedCells(self):
        for cell in self.__token_visited_cells_coords:
            if self.maze.getMazeType() == "square":
                pg.draw.rect(self.__screen, self.YELLOW, (cell[0], cell[1], self.__cell_width - self.__cell_width*0.2, self.__cell_height - self.__cell_height*0.2), 2)
            elif self.maze.getMazeType() == "hexagonal":
                self.drawHexagon(cell[0]+self.__cell_width*0.1, cell[1]+self.__cell_width*0.1, self.__cell_side_length - self.__cell_side_length*0.2, self.YELLOW)
            elif self.maze.getMazeType() == "triangular":
                
                self.drawTriangle(cell[0], cell[1], cell[2] - cell[2]*0.2, cell[3], self.YELLOW)

    def drawHexagon(self, x, y, size, color=(0, 0, 0)):
        hexagon_points = []
        for i in range(6):
            angle_deg = 60 * i -30
            angle_rad = math.pi / 180 * angle_deg
            hexagon_points.append((x + size * math.cos(angle_rad), y + size * math.sin(angle_rad)))
        pg.draw.polygon(self.__screen, color, hexagon_points, 2)
        self.__points.append(hexagon_points)



    def draw_hexagon_connection(self, cell1, cell2, x, y, size):
        # draw a white line between the two cells
        self.__cell1_x, self.__cell1_y = x, y
        self.__cell2_x, self.__cell2_y = cell2.getID()
        self.__cell2_x, self.__cell2_y = (self.__cell2_x * self.__cell_width) + (self.__cell_width/2) + self.__maze_width*0.025, self.__cell2_y * self.__cell_height + self.__maze_height*0.025 + self.__cell_width/2
        

        if cell2.getID()[1] % 2 == 1:
            self.__cell2_x += 0.5 * self.__cell_width
        
        #pg.draw.line(self.__screen, self.GREEN, (self.__cell1_x, self.__cell1_y), (self.__cell2_x, self.__cell2_y), 2)

        if int(self.__cell1_y) == int(self.__cell2_y):
           
            self.__start_x = min([self.__cell1_x, self.__cell2_x]) + self.__cell_width/2
            self.__end_x = self.__start_x
            self.__start_y = self.__cell1_y - self.__cell_side_length/2 
            self.__end_y = self.__start_y + self.__cell_side_length 
        else:
            if self.__cell1_y < self.__cell2_y:
                self.__start_x = self.__cell2_x 
                self.__end_x = self.__cell1_x
                self.__start_y = self.__cell2_y - self.__cell_side_length
                self.__end_y = self.__cell1_y + self.__cell_side_length
            else:
                self.__start_x = self.__cell1_x 
                self.__end_x = self.__cell2_x
                self.__start_y = self.__cell1_y - self.__cell_side_length
                self.__end_y = self.__cell2_y + self.__cell_side_length

        pg.draw.line(self.__screen, self.WHITE, (self.__start_x, self.__start_y), (self.__end_x, self.__end_y), 4)

    def get_triangle_base_points(self, x, y):
        
        base_point_1 = [(x * self.__cell_width)  + self.__maze_width*0.025, (y * (self.__cell_height))  + self.__maze_height*0.025]
        base_point_2 = [base_point_1[0]+self.__cell_side_length, (y * (self.__cell_height))  + self.__maze_height*0.025]
        
        flipped = False
        if x % 2 == 1:
            flipped = True
        if y%2 == 1:
            flipped = not flipped
        if flipped:
            base_point_1[1] += self.__cell_height
            base_point_2[1] += self.__cell_height
      

        return base_point_1, base_point_2

    def drawTriangle(self, base_point_1, base_point_2, size, flipped, color=(0, 0, 0)):
        triangle_points = [base_point_1, base_point_2]
        height = math.sqrt((size**2) - ((size/2)**2))
        x = (base_point_1[0] + base_point_2[0])/2
        if flipped:
            y = base_point_1[1] - height
        else:
            y = base_point_1[1] + height
        triangle_points.append((x, y))
        pg.draw.polygon(self.__screen, color, triangle_points, 2)
        self.__points.append(triangle_points)        


    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def draw_triangle_connection(self, cell1, cell2, size):
        if cell1.checkConnection(cell2):

            cell1_base_point_1, cell1_base_point_2 = self.get_triangle_base_points(cell1.getID()[0], cell1.getID()[1])
            cell2_base_point_1, cell2_base_point_2 = self.get_triangle_base_points(cell2.getID()[0], cell2.getID()[1])

            if list(map(int, cell1_base_point_1)) == list(map(int, cell2_base_point_1)):
                line_start = cell1_base_point_1
                line_end = cell1_base_point_2

            elif self.distance(cell1_base_point_1[0], cell1_base_point_1[1], cell2_base_point_2[0], cell2_base_point_2[1] ) < self.distance(cell1_base_point_2[0], cell1_base_point_2[1], cell2_base_point_1[0], cell2_base_point_1[1] ):
                line_start = cell1_base_point_1
                line_end = cell2_base_point_2
            else:
                line_start = cell1_base_point_2
                line_end = cell2_base_point_1
            pg.draw.line(self.__screen, self.WHITE, line_start, line_end, 2)

    def displayMaze(self):
        self.__screen.fill(self.WHITE)
        if self.maze.getMazeType() == "square":
            self.__cell_width = self.__maze_width / self.maze.getMazeSize()
            self.__cell_height = self.__maze_height / self.maze.getMazeSize()

            for y in range(self.maze.getMazeSize()):
                for x in range(self.maze.getMazeSize()):
                    cell = self.maze.getGrid()[y][x]
                    
                    if y == 0 or self.maze.getGrid()[y-1][x] not in cell.getConnections():
                        pg.draw.line(self.__screen, self.BLACK, (x *  self.__cell_width, y *  self.__cell_height), 
                                                    ((x+1) *  self.__cell_width, y *  self.__cell_height))
                
                    if x == 0 or not(str(self.maze.getGrid()[y][x-1]) in [str(i) for i in cell.getConnections()]):
                        pg.draw.line(self.__screen, self.RED, (x *  self.__cell_width, y *  self.__cell_height), 
                                                    (x *  self.__cell_width, (y+1) *  self.__cell_height))
            
            pg.draw.circle(self.__screen, self.GREEN, (self.__current_cell.getID()[0] * self.__cell_width + self.__cell_width/2, self.__current_cell.getID()[1] * self.__cell_height + self.__cell_height/2), self.__cell_width/4)
            self.__token_visited_cells_coords.append((self.__current_cell.getID()[0] * self.__cell_width + self.__cell_width*0.1, self.__current_cell.getID()[1] * self.__cell_height + self.__cell_height*0.1))
            self.highlightVisitedCells()
        elif self.maze.getMazeType() == "hexagonal":
            self.__points = []
            self.__cell_width = ((self.__maze_width*0.95) / self.maze.getMazeSize())
            self.__cell_side_length =  2*((self.__cell_width / 2) / math.tan(math.pi / 3))
            self.__cell_height = (self.__cell_side_length * 2) - (self.__cell_side_length / 2)


            for y in range(self.maze.getMazeSize()):
                for x in range(self.maze.getMazeSize()):
                    if y % 2 == 1 and x == self.maze.getMazeSize() - 1:
                        break
                    cell = self.maze.getGrid()[y][x]
                    self.__curr_x =  (x * self.__cell_width) + (self.__cell_width/2) + self.__maze_width*0.025
                    self.__curr_y = (y * (self.__cell_height)) + (self.__cell_width/2)  + self.__maze_height*0.025
                    if y % 2 == 1:
                        self.__curr_x += 0.5 * self.__cell_width

                    self.drawHexagon(self.__curr_x, self.__curr_y, self.__cell_side_length)
                    self.__cell_connections = cell.getConnections()

                    for c in self.__cell_connections:
                        self.draw_hexagon_connection(self.maze.getGrid()[y][x], c, self.__curr_x, self.__curr_y, self.__cell_side_length)

            self.__circle_x = self.__current_cell.getID()[0] * self.__cell_width + self.__cell_width/2 + self.__maze_width*0.025
            self.__circle_y = self.__current_cell.getID()[1] * self.__cell_height + self.__cell_height/2 + self.__maze_height*0.025
            if self.__current_cell.getID()[1] % 2 == 1:
                self.__circle_x += 0.5 * self.__cell_width
            pg.draw.circle(self.__screen, self.GREEN, (self.__circle_x, self.__circle_y), self.__cell_width/4)
            self.__token_visited_cells_coords.append((self.__circle_x - self.__cell_width*0.1, self.__circle_y - self.__cell_height*0.1))
            
        elif self.maze.getMazeType() == "triangular":
            self.__points = []
            self.__cell_height = ((self.__maze_height*0.95) / (self.maze.getMazeSize()))
            self.__cell_side_length = self.__cell_height / math.sin(math.pi/3)
            self.__cell_width = self.__cell_side_length / 2
            for y in range(self.maze.getMazeSize()):
                for x in range(len(self.maze.getGrid()[y])):
                    self.__flipped = False
                    cell = self.maze.getGrid()[y][x]
                    self.__base_1, self.__base_2 = self.get_triangle_base_points(x, y)
                    if x % 2 == 1:
                        self.__flipped = True
                    if y%2 == 1:
                        self.__flipped = not self.__flipped

                    self.drawTriangle(self.__base_1, self.__base_2, self.__cell_side_length, self.__flipped)
              
                    self.__cell_connections = cell.getConnections()
                    for c in self.__cell_connections:
                         self.draw_triangle_connection(self.maze.getGrid()[y][x], c, self.__cell_side_length)

            self.__circle_x = self.__current_cell.getID()[0] * self.__cell_width + self.__cell_width/2 + self.__maze_width*0.025 + self.__cell_width/2
            self.__circle_y = self.__current_cell.getID()[1] * self.__cell_height + self.__cell_height/2 + self.__maze_height*0.025
            pg.draw.circle(self.__screen, self.GREEN, (self.__circle_x, self.__circle_y), self.__cell_width/4)
            x = (self.__base_1, self.__base_2, self.__cell_side_length, self.__flipped)
            if not x in self.__token_visited_cells_coords:
                self.__token_visited_cells_coords.append(x)
            self.highlightVisitedCells()


    def pygameLoop(self):
        pg.init()
        self.__infoObject = pg.display.Info()

        self.__width, self.__height = self.__infoObject.current_w*0.8, self.__infoObject.current_h*0.8

        self.__maze_width, self.__maze_height = 2*(self.__width//3), self.__height

        self.__side_width, self.__side_height = self.__width - self.__maze_width, self.__height

        self.__screen = pg.display.set_mode((self.__width, self.__height))
        self.__running = True
        self.__screen.fill(self.WHITE)
        self.__current_cell = self.maze.getGrid()[0][0]
        self.__token_visited_cells_coords = []

        while self.__running:
            self.displayMaze()
            self.displaySide()
            self.cell_hover()
            pg.display.flip()
            if self.maze.getMazeType() == "square":
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.__running = False
                    elif event.type == pg.KEYDOWN:
                        
                        if event.key == pg.K_LEFT:
                            self.__solve_step_return_value = self.maze.solve_step((self.__current_cell.getID()[0]-1, self.__current_cell.getID()[1]), self.__current_cell)
                        elif event.key == pg.K_RIGHT:
                            self.__solve_step_return_value = self.maze.solve_step((self.__current_cell.getID()[0]+1, self.__current_cell.getID()[1]), self.__current_cell)
                        elif event.key == pg.K_UP:
                            self.__solve_step_return_value = self.maze.solve_step((self.__current_cell.getID()[0], self.__current_cell.getID()[1]-1), self.__current_cell)
                        elif event.key == pg.K_DOWN:
                            self.__solve_step_return_value = self.maze.solve_step((self.__current_cell.getID()[0], self.__current_cell.getID()[1]+1), self.__current_cell)
                        elif event.key == pg.K_SPACE:
                            self.__solve_step_return_value = self.maze.solve_step("space", self.__current_cell)
                        if self.__solve_step_return_value == "end":
                            print("Congratulations! You solved the maze!")
                            self.__running = False
                        elif self.__solve_step_return_value == "invalid_move":
                            print("Invalid move!")
                        elif self.__solve_step_return_value == "wrong_move":
                            print("Wrong move!")
                        else:
                            self.__current_cell = self.__solve_step_return_value
                    elif event.type == pg.MOUSEBUTTONDOWN:
                        x, y = pg.mouse.get_pos()
                        if x < self.__maze_width:
                            self.__solve_step_return_value = self.maze.solve_step((x//self.__cell_width, y//self.__cell_height), self.__current_cell)
                            if self.__solve_step_return_value == "end":
                                self.__current_cell = self.maze.getGrid()[self.maze.getMazeSize()-1][self.maze.getMazeSize()-1]
                                self.displayMaze()
                                pg.display.flip()
                                print("Congratulations! You solved the maze!")
                                self.__running = False
                            elif self.__solve_step_return_value == "invalid_move":
                                print("Invalid move!")
                            elif self.__solve_step_return_value == "wrong_move":
                                print("Wrong move!")
                            else:
                                self.__current_cell = self.__solve_step_return_value
                self.__screen.fill(self.WHITE)
            elif self.maze.getMazeType() == "hexagonal":
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.__running = False
                    
                    elif event.type == pg.MOUSEBUTTONDOWN:
                        x, y = pg.mouse.get_pos()
                        if x < self.__maze_width:
                            self.__clicked_cell = self.cell_hover(clicked=True)
                            if self.__clicked_cell != None:
                                self.__solve_step_return_value = self.maze.solve_step(self.cell_hover(clicked=True).getID() , self.__current_cell)
                                if self.__solve_step_return_value == "end":
                                    self.__current_cell = self.maze.getGrid()[self.maze.getMazeSize()-1][len(self.maze.getGrid()[self.maze.getMazeSize()-1])-1]
                                    self.displayMaze()
                                    pg.display.flip()
                                    print("Congratulations! You solved the maze!")
                                    self.__running = False
                                elif self.__solve_step_return_value == "invalid_move":
                                    print("Invalid move!")
                                elif self.__solve_step_return_value == "wrong_move":
                                    print("Wrong move!")
                                else:
                                    self.__current_cell = self.__solve_step_return_value
                            else:
                                print("Invalid move!")
                self.__screen.fill(self.WHITE)
            elif self.maze.getMazeType() == "triangular":
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.__running = False
                    
                    elif event.type == pg.MOUSEBUTTONDOWN:
                        x, y = pg.mouse.get_pos()
                        if x < self.__maze_width:
                            self.__clicked_cell = self.cell_hover(clicked=True)
                            if self.__clicked_cell != None:
                                self.__solve_step_return_value = self.maze.solve_step(self.cell_hover(clicked=True).getID() , self.__current_cell)
                                if self.__solve_step_return_value == "end":
                                    self.__current_cell = self.maze.getGrid()[self.maze.getMazeSize()-1][len(self.maze.getGrid()[self.maze.getMazeSize()-1])-1]
                                    self.displayMaze()
                                    pg.display.flip()
                                    print("Congratulations! You solved the maze!")
                                    self.__running = False
                                elif self.__solve_step_return_value == "invalid_move":
                                    print("Invalid move!")
                                elif self.__solve_step_return_value == "wrong_move":
                                    print("Wrong move!")
                                else:
                                    self.__current_cell = self.__solve_step_return_value
                            else:
                                print("Invalid move!")
                self.__screen.fill(self.WHITE)

        pg.quit()


    def run(self):
        pass


class TerminalUI(UI):

    def __init__(self):
        pass
    
    def Hello_world(self):
        print("Hello world!")
    
    def run(self):
        self.__gen_algorithms = ["sidewinder", "binary_tree"]
        self.__solve_algorithms = ["depth_first", "breadth_first", "manual"]

        genAlgorithm = input("Please choose an algorithm to generate the maze, 1 for sidewinder, 2 for binary tree: ")
        if genAlgorithm != "1" and genAlgorithm != "2":
            genAlgorithm = input("Please input a valid option, 1 for sidewinder, 2 for binary tree: ")
        
        solveAlgorithm = input("Please choose an algorithm to solve the maze, 1 for DFS, 2 for BFS, 3 for solving manually: ")
        if solveAlgorithm not in ["1", "2", "3"]:
            solveAlgorithm = input("Please input a valid option, 1 for DFS, 2 for BFS, 3 for manual solving: ")
        
        mazeType = input("Please input the type of the maze, 1 for square, 2 for hexagonal, 3 for triangular: ")
        if mazeType not in ["1", "2", "3"]:
            mazeType = input("Please input a valid option, 1 for square, 2 for hexagonal, 3 for triangular: ")

        mazeSize = input("Please input the size of the maze: ")
        if not mazeSize.isdigit() or int(mazeSize) < 5 or int(mazeSize) > 100:
            mazeSize = input("Please input a valid size, between 5 and 100: ")

        self.maze = Mazes.Maze(mazeType=int(mazeType), size=int(mazeSize), gen_algorithm=self.__gen_algorithms[int(genAlgorithm)-1], solve_algorithm=self.__solve_algorithms[int(solveAlgorithm)-1])

        self.maze.generate()
        
        self.pygameLoop()

class GUI(UI):
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.screenWidth = self.app.desktop().screenGeometry().width()
        self.screenHeight = self.app.desktop().screenGeometry().height()
        self.GUI = Ui_MainMenu(self.screenWidth, self.screenHeight)
        self.GUI.setupUi(self.screenWidth, self.screenHeight)

    def run(self):
        self.GUI.show()
        sys.exit(self.app.exec_())
        

class Ui_MainMenu(QMainWindow):
    def __init__(self, desktopWidth, desktopHeight):
        super(Ui_MainMenu, self).__init__()
        self.desktopWidth = desktopWidth
        self.desktopHeight = desktopHeight
        self.setupUi(self.desktopWidth, self.desktopHeight)

    def setupUi(self, desktopWidth, desktopHeight):
        
        self.resize(desktopWidth*0.6, desktopHeight*0.6)
        
        self.setObjectName("MainMenu")
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # Create a vertical layout
        layout = QtWidgets.QVBoxLayout(self.centralwidget)

        # TitleLabel
        self.TitleLabel = QtWidgets.QLabel("CompSci Maze Master", self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.TitleLabel.setFont(font)
        self.TitleLabel.setAlignment(QtCore.Qt.AlignCenter)  # Center alignment
        layout.addWidget(self.TitleLabel)  # Add to layout

        # StartButton
        self.StartButton = QtWidgets.QPushButton("Generate New Maze", self.centralwidget)
        self.StartButton.setObjectName("StartButton")

        # Set font size for the button text
        buttonFont = QtGui.QFont()
        buttonFont.setPointSize(12)  # Adjust the font size as needed
        self.StartButton.setFont(buttonFont)

        # Set button size
        self.StartButton.setMinimumSize(250, 100)  # Adjust width and height as needed

        layout.addWidget(self.StartButton, 0, QtCore.Qt.AlignCenter)  # Add to layout

        # Set layout to central widget
        self.centralwidget.setLayout(layout)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, desktopWidth*0.8, 21))
        self.menubar.setObjectName("menubar")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuExt = QtWidgets.QMenu(self.menubar)
        self.menuExt.setObjectName("menuExt")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menubar.addAction(self.menuExt.menuAction())

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainMenu", "MainWindow"))
        self.TitleLabel.setText(_translate("MainMenu", "CompSci Maze Master"))
        self.StartButton.setText(_translate("MainMenu", "Generate New Maze"))
        self.menuHelp.setTitle(_translate("MainMenu", "Help"))
        self.menuExt.setTitle(_translate("MainMenu", "Exit"))
        self.StartButton.clicked.connect(self.StartButton_clicked)

    def StartButton_clicked(self):
        self.hide()
        self.ForwardWindow = Ui_GenerateMazeMenu(self.desktopWidth, self.desktopHeight)
        self.ForwardWindow.show()

class Ui_GenerateMazeMenu(QtWidgets.QMainWindow):
    def __init__(self, desktopWidth, desktopHeight):
        super(Ui_GenerateMazeMenu, self).__init__()
        self.desktopWidth = desktopWidth
        self.desktopHeight = desktopHeight
        self.setupUi(self.desktopWidth, self.desktopHeight)

    def setupUi(self, desktopWidth, desktopHeight):
        self.resize(desktopWidth*0.6, desktopHeight*0.6)
        self.setObjectName("GenerateMazeMenu")
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        
        self.BackButton = QtWidgets.QPushButton("Back", self)
        self.BackButton.setGeometry(20, 60, 100, 40)  # Adjust size and position as needed
        self.BackButton.setObjectName("BackButon")
        # Create a vertical layout
        layout = QtWidgets.QVBoxLayout(self.centralwidget)

        # TitleGenerateMaze
        self.TitleGenerateMaze = QtWidgets.QLabel("Generate New Maze", self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.TitleGenerateMaze.setFont(font)
        self.TitleGenerateMaze.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.TitleGenerateMaze)

        # MazeSettingsContainer
        self.MazeSettingsContainer = QtWidgets.QGroupBox("Maze Settings", self.centralwidget)
        self.MazeSettingsContainer.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.MazeSettingsContainer)

        # GroupBox layout
        groupBoxLayout = QtWidgets.QVBoxLayout(self.MazeSettingsContainer)

        # GenAlgorithmContainer with horizontal layout
        self.GenAlgorithmContainer = QtWidgets.QGroupBox("Generation Algorithm", self.MazeSettingsContainer)
        genAlgorithmLayout = QtWidgets.QHBoxLayout()  # Horizontal layout
        genAlgorithmLayout.addStretch(1)  # Add stretchable space on the left
        self.SidewinderRadioButton = QtWidgets.QRadioButton("Sidewinder", self.GenAlgorithmContainer)
        genAlgorithmLayout.addWidget(self.SidewinderRadioButton)
        self.BinaryTreeRadioButton = QtWidgets.QRadioButton("Binary Tree", self.GenAlgorithmContainer)
        genAlgorithmLayout.addWidget(self.BinaryTreeRadioButton)
        genAlgorithmLayout.addStretch(1)  # Add stretchable space on the right
        self.GenAlgorithmContainer.setLayout(genAlgorithmLayout)
        groupBoxLayout.addWidget(self.GenAlgorithmContainer)

        # SolveAlgorithmContainer with horizontal layout
        self.SolveAlgorithmContainer = QtWidgets.QGroupBox("Solving Algorithm", self.MazeSettingsContainer)
        solveAlgorithmLayout = QtWidgets.QHBoxLayout()
        solveAlgorithmLayout.addStretch(1)
        self.DFSRadioButton = QtWidgets.QRadioButton("Depth First Search", self.SolveAlgorithmContainer)
        solveAlgorithmLayout.addWidget(self.DFSRadioButton)
        self.BFSRadioButton = QtWidgets.QRadioButton("Breadth First Search", self.SolveAlgorithmContainer)
        solveAlgorithmLayout.addWidget(self.BFSRadioButton)
        self.ManualRadioButton = QtWidgets.QRadioButton("Manual Solve", self.SolveAlgorithmContainer)
        solveAlgorithmLayout.addWidget(self.ManualRadioButton)
        solveAlgorithmLayout.addStretch(1)
        self.SolveAlgorithmContainer.setLayout(solveAlgorithmLayout)
        groupBoxLayout.addWidget(self.SolveAlgorithmContainer)

        # MazeTypeContainer with horizontal layout
        self.MazeTypeContainer = QtWidgets.QGroupBox("Maze Type", self.MazeSettingsContainer)
        mazeTypeLayout = QtWidgets.QHBoxLayout()
        mazeTypeLayout.addStretch(1)
        self.SquareRadioButton = QtWidgets.QRadioButton("Square", self.MazeTypeContainer)
        mazeTypeLayout.addWidget(self.SquareRadioButton)
        self.HexagonalRadioButton = QtWidgets.QRadioButton("Hexagonal", self.MazeTypeContainer)
        mazeTypeLayout.addWidget(self.HexagonalRadioButton)
        self.TriangularRadioButton = QtWidgets.QRadioButton("Triangular", self.MazeTypeContainer)
        mazeTypeLayout.addWidget(self.TriangularRadioButton)
        mazeTypeLayout.addStretch(1)
        self.MazeTypeContainer.setLayout(mazeTypeLayout)
        groupBoxLayout.addWidget(self.MazeTypeContainer)
        # MazeSizeSlider and MazeSizeText
        self.MazeSizeSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.MazeSettingsContainer)
        self.MazeSizeSlider.setMinimum(5)
        self.MazeSizeSlider.setMaximum(100)
        groupBoxLayout.addWidget(self.MazeSizeSlider)
        self.MazeSizeText = QtWidgets.QLabel("Maze Size: 5", self.MazeSettingsContainer)
        groupBoxLayout.addWidget(self.MazeSizeText)

        # GenerateMazeButton
        self.GenerateMazeButton = QtWidgets.QPushButton("Generate", self.centralwidget)
        self.GenerateMazeButton.setObjectName("GenerateMazeButton")
        layout.addWidget(self.GenerateMazeButton, 0, QtCore.Qt.AlignCenter)

        # Menu and status bar setup
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuExit = QtWidgets.QMenu(self.menubar)
        self.menuExit.setObjectName("menuExit")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menubar.addAction(self.menuExit.menuAction())

        # Set layout to central widget
        self.centralwidget.setLayout(layout)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("GenerateMazeMenu", "MainWindow"))
        self.TitleGenerateMaze.setText(_translate("GenerateMazeMenu", "Generate New Maze"))
        self.GenerateMazeButton.setText(_translate("GenerateMazeMenu", "Generate"))
        self.MazeSettingsContainer.setTitle(_translate("GenerateMazeMenu", "Maze Settings"))
        self.GenAlgorithmContainer.setTitle(_translate("GenerateMazeMenu", "Generation Algorithm"))
        self.SidewinderRadioButton.setText(_translate("GenerateMazeMenu", "Sidewinder"))
        self.BinaryTreeRadioButton.setText(_translate("GenerateMazeMenu", "Binary Tree"))
        self.MazeSizeSlider.setToolTip(_translate("GenerateMazeMenu", "Maze Size"))
        self.MazeSizeText.setText(_translate("GenerateMazeMenu", "Maze Size: 5"))
        self.SolveAlgorithmContainer.setTitle(_translate("GenerateMazeMenu", "Solving Algorithm"))
        self.DFSRadioButton.setText(_translate("GenerateMazeMenu", "Depth First Search"))
        self.BFSRadioButton.setText(_translate("GenerateMazeMenu", "Breadth First Search"))
        self.ManualRadioButton.setText(_translate("GenerateMazeMenu", "Manual Solve"))
        self.MazeTypeContainer.setTitle(_translate("GenerateMazeMenu", "Maze Type"))
        self.SquareRadioButton.setText(_translate("GenerateMazeMenu", "Square"))
        self.HexagonalRadioButton.setText(_translate("GenerateMazeMenu", "Hexagonal"))
        self.TriangularRadioButton.setText(_translate("GenerateMazeMenu", "Triangular"))
        self.menuHelp.setTitle(_translate("GenerateMazeMenu", "Help"))
        self.menuExit.setTitle(_translate("GenerateMazeMenu", "Exit"))

        self.MazeSizeSlider.valueChanged.connect(self.MazeSizeSlider_valueChanged)
        self.GenerateMazeButton.clicked.connect(self.GenerateMazeButton_clicked)
        self.BackButton.clicked.connect(self.BackButton_clicked)

    def MazeSizeSlider_valueChanged(self):
        self.MazeSizeText.setText("Maze Size: " + str(self.MazeSizeSlider.value()))

    def BackButton_clicked(self):
        self.hide()
        self.BackWindow = Ui_MainMenu(self.desktopWidth, self.desktopHeight)
        self.BackWindow.show()

    def GenerateMazeButton_clicked(self):
        if self.SidewinderRadioButton.isChecked():
            self.genAlgorithm = "sidewinder"
        elif self.BinaryTreeRadioButton.isChecked():
            self.genAlgorithm = "binary_tree"
        else:
            self.genAlgorithm = None

        if self.DFSRadioButton.isChecked():
            self.solveAlgorithm = "depth_first"
        elif self.BFSRadioButton.isChecked():
            self.solveAlgorithm = "breadth_first"
        elif self.ManualRadioButton.isChecked():
            self.solveAlgorithm = "manual"
        else:
            self.solveAlgorithm = None

        if self.SquareRadioButton.isChecked():
            self.mazeType = "square"
        elif self.HexagonalRadioButton.isChecked():
            self.mazeType = "hexagonal"
        elif self.TriangularRadioButton.isChecked():
            self.mazeType = "triangular"
        else:
            self.mazeType = None
        if self.genAlgorithm != None and self.solveAlgorithm != None and self.mazeType != None:
            self.hide()
            self.ForwardWindow = Ui_Maze(self.desktopWidth, self.desktopHeight, self.genAlgorithm, self.solveAlgorithm, self.mazeType, self.MazeSizeSlider.value())
            self.ForwardWindow.show()
        else:
            self.Dialog = QtWidgets.QDialog()
            self.error = Ui_Dialog()
            self.error.setupUi(self.Dialog, self.desktopWidth, self.desktopHeight)
            self.Dialog.show()
        self.mazeConfig = [self.genAlgorithm, self.solveAlgorithm, self.mazeType, self.MazeSizeSlider.value()]

    def getMazeConfig(self):
        if self.mazeConfig != None:
            return self.mazeConfig
        else:
            return None

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog, desktopWidth, desktopHeight):
        Dialog.setObjectName("Dialog")
        Dialog.resize(desktopWidth * 0.2, desktopHeight * 0.2)

        # Main vertical layout
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")

        # Spacer item for vertical alignment
        self.verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer)

        # Label
        self.label = QtWidgets.QLabel("Please select all options!", Dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        # Spacer item for vertical alignment
        self.verticalSpacer2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer2)

        # Button Box
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setLayoutDirection(QtCore.Qt.LeftToRight)  # Right-align the buttons
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Please select all options!"))



class Ui_MazeSolveWindow(QMainWindow):
    def __init__(self, desktopWidth, desktopHeight, genAlgorithm, solveAlgorithm, mazeType, mazeSize):
        super(Ui_MazeSolveWindow, self).__init__()
        self.desktopWidth = desktopWidth
        self.desktopHeight = desktopHeight
        self.genAlgorithm = genAlgorithm
        self.solveAlgorithm = solveAlgorithm
        self.mazeType = mazeType
        self.mazeSize = mazeSize
        self.UI = UI()
        self.setupUi()

    def setupUi(self):
        MazeSolveWindow.setObjectName("MazeSolveWindow")
        MazeSolveWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MazeSolveWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.PyGameMazeWidget = QtWidgets.QWidget(self.centralwidget)
        self.PyGameMazeWidget.setGeometry(QtCore.QRect(0, 0, 561, 571))
        self.PyGameMazeWidget.setObjectName("PyGameMazeWidget")
        self.InstructionsWidget = QtWidgets.QWidget(self.centralwidget)
        self.InstructionsWidget.setGeometry(QtCore.QRect(559, -1, 231, 571))
        self.InstructionsWidget.setObjectName("InstructionsWidget")
        self.label = QtWidgets.QLabel(self.InstructionsWidget)
        self.label.setGeometry(QtCore.QRect(50, 20, 151, 61))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setUnderline(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.InstructionsWidget)
        self.label_2.setGeometry(QtCore.QRect(20, 100, 131, 51))
        self.label_2.setObjectName("label_2")
        MazeSolveWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MazeSolveWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuExit = QtWidgets.QMenu(self.menubar)
        self.menuExit.setObjectName("menuExit")
        MazeSolveWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MazeSolveWindow)
        self.statusbar.setObjectName("statusbar")
        MazeSolveWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menubar.addAction(self.menuExit.menuAction())

        self.retranslateUi(MazeSolveWindow)
        QtCore.QMetaObject.connectSlotsByName(MazeSolveWindow)

    def retranslateUi(self, MazeSolveWindow):
        _translate = QtCore.QCoreApplication.translate
        MazeSolveWindow.setWindowTitle(_translate("MazeSolveWindow", "MainWindow"))
        self.label.setText(_translate("MazeSolveWindow", "Instructions"))
        self.label_2.setText(_translate("MazeSolveWindow", "1. Example Instruction"))
        self.menuHelp.setTitle(_translate("MazeSolveWindow", "Help"))
        self.menuExit.setTitle(_translate("MazeSolveWindow", "Exit"))
        self.startPygame()

    def startPygame(self):
        self.maze = Mazes.Maze(mazeType=self.mazeType, size=self.mazeSize, gen_algorithm=self.genAlgorithm, solve_algorithm=self.solveAlgorithm)
        self.maze.generate()
        self.UI.pygameLoop(GUI=True, maze=self.maze)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MazeSolveWindow = QtWidgets.QMainWindow()
    ui = Ui_MazeSolveWindow()
    ui.setupUi(MazeSolveWindow)
    MazeSolveWindow.show()
    sys.exit(app.exec_())
