import typing
from PyQt5.QtCore import Qt
import pygame as pg
import Mazes
import time
from abc import ABC, abstractmethod
import math
import random
import time
import datetime
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGroupBox, QGridLayout, QPushButton, QLabel, QVBoxLayout

from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import QTimer

import sys

class UI():         
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0 , 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    HOVER_COLOUR = (200, 200, 200)
    HIGHLIGHT_COLOUR = (187, 216, 236)
    HINT_COLOUR = (255, 255, 0)
    CHARACTERCOLOUR = (0, 32, 235)

    SQUAREMAZETHICKNESS = 6
    HEXAGONMAZETHICKNESS = 3
    TRIANGULARMAZETHICKNESS = 5

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
            for p in self.__points:
                if self.__mouse_pos_x > self.__maze_width and self.__mouse_pos_y > self.__maze_height:
                    break
                if self.is_inside_polygon(self.__mouse_pos_x, self.__mouse_pos_y, p):
                    self.__cell_x = self.__points.index(p)
                    counter = 0
                    flag = False
                    for y in range(self.maze.getMazeHeight()):
                        for x in range(len(self.maze.getGrid()[y])):
                            if counter == self.__cell_x:
                                self.__cell = self.maze.getGrid()[y][x]
                                flag = True
                                break
                            counter += 1
                        if flag:
                            break         
                    pg.draw.rect(self.__screen, self.HOVER_COLOUR, (self.__cell.getID()[0] * self.__cell_width, self.__cell.getID()[1] * self.__cell_height, self.__cell_width, self.__cell_height), self.SQUAREMAZETHICKNESS)
                    pg.mouse.set_cursor(*pg.cursors.broken_x)
                    if clicked:
                        return self.__cell
                    break

        elif self.maze.getMazeType() == "hexagonal":
            for p in self.__points:
                if self.__mouse_pos_x > self.__maze_width and self.__mouse_pos_y > self.__maze_height:
                    break
                if self.is_inside_polygon(self.__mouse_pos_x, self.__mouse_pos_y, p):
                    
                    self.__cell_x = self.__points.index(p)
                    counter = 0
                    flag = False
                    
                    for y in range(self.maze.getMazeHeight()):
                        
                        for x in range(len(self.maze.getGrid()[y])):
              
                            if counter == self.__cell_x:
                                self.__cell = self.maze.getGrid()[y][x]
                                

                                flag = True
                                break
                            counter += 1
                        if flag:
                            break                            
                    pg.draw.polygon(self.__screen, self.HOVER_COLOUR, p, self.HEXAGONMAZETHICKNESS)
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
                    for y in range(self.maze.getMazeHeight()):
                        
                        for x in range(len(self.maze.getGrid()[y])):
              
                            if counter == self.__cell_x:
                                self.__cell = self.maze.getGrid()[y][x]
                                
                                flag = True
                                break
                            counter += 1
                        if flag:
                            break                            
                    pg.draw.polygon(self.__screen, self.HOVER_COLOUR, p, self.TRIANGULARMAZETHICKNESS)
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
                pg.draw.rect(self.__screen, self.HIGHLIGHT_COLOUR, (cell[0], cell[1], self.__cell_width+2, self.__cell_height+2))
                

            elif self.maze.getMazeType() == "hexagonal":
                self.drawHexagon(cell[0], cell[1]+3, self.__cell_side_length, self.HIGHLIGHT_COLOUR, character=True, fill=True)
            elif self.maze.getMazeType() == "triangular":
                
                self.drawTriangle(cell[0], cell[1], cell[2] , cell[3], self.HIGHLIGHT_COLOUR, character=True, fill=True)

    def drawHexagon(self, x, y, size, color=(0, 0, 0), width=0, character=False, fill=False):
        hexagon_points = []
        for i in range(6):
            angle_deg = 60 * i -30
            angle_rad = math.pi / 180 * angle_deg
            hexagon_points.append((x + size * math.cos(angle_rad), y + size * math.sin(angle_rad)))
        if fill:
            pg.draw.polygon(self.__screen, color, hexagon_points, 0)
        else:
            pg.draw.polygon(self.__screen, color, hexagon_points, self.HEXAGONMAZETHICKNESS)
        if not character:
            self.__points.append(hexagon_points)



    def draw_hexagon_connection(self, cell1, cell2, x, y, size, offsetWidth, offsetHeight):
        # draw a white line between the two cells
        self.__cell1_x, self.__cell1_y = x, y
        self.__cell2_x, self.__cell2_y = cell2.getID()
        self.__cell2_x, self.__cell2_y = (self.__cell2_x * self.__cell_width) + offsetWidth + (self.__cell_width/2) , self.__cell2_y * self.__cell_height  + self.__cell_width/2 + offsetHeight
        

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

        pg.draw.line(self.__screen, self.WHITE, (self.__start_x, self.__start_y), (self.__end_x, self.__end_y), self.HEXAGONMAZETHICKNESS)

    def get_triangle_base_points(self, x, y):
        
        base_point_1 = [(x * self.__cell_width)  , (y * (self.__cell_height))  ]
        base_point_2 = [base_point_1[0]+self.__cell_side_length, (y * (self.__cell_height))  ]
        
        flipped = False
        if x % 2 == 1:
            flipped = True
        if y%2 == 1:
            flipped = not flipped
        if flipped:
            base_point_1[1] += self.__cell_height
            base_point_2[1] += self.__cell_height
      

        return base_point_1, base_point_2

    def drawTriangle(self, base_point_1, base_point_2, size, flipped, color=(0, 0, 0), fill=False, character=False):
        triangle_points = [base_point_1, base_point_2]
        height = math.sqrt((size**2) - ((size/2)**2))
        x = (base_point_1[0] + base_point_2[0])/2
        if flipped:
            y = base_point_1[1] - height
        else:
            y = base_point_1[1] + height
        triangle_points.append((x, y))
        if fill:
            pg.draw.polygon(self.__screen, color, triangle_points, 0)
        else:
            pg.draw.polygon(self.__screen, color, triangle_points, self.TRIANGULARMAZETHICKNESS)
        if not character and not(triangle_points in self.__points):
            
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
            pg.draw.line(self.__screen, self.WHITE, line_start, line_end, self.TRIANGULARMAZETHICKNESS)

    def getCellFlipped(self, cell):
        x, y = cell.getID()
        flipped = False
        if x % 2 == 1:
            flipped = True
        if y%2 == 1:
            flipped = not flipped
        return flipped

    def highlightCell(self, cell, colour=None):
        if self.maze.getMazeType() == "square":
            pg.draw.rect(self.__screen, colour, (cell.getID()[0] * self.__cell_width, cell.getID()[1] * self.__cell_height, self.__cell_width, self.__cell_height), 0)
        elif self.maze.getMazeType() == "hexagonal":
            self.__cell_x, self.__cell_y = cell.getID()
            self.__cell_x, self.__cell_y = (self.__cell_x * self.__cell_width) + self.__cell_width/2 + self.__offsetWidth, self.__cell_y * self.__cell_height  + self.__cell_height/2 + self.__offsetHeight 
            if cell.getID()[1] % 2 == 1:
                self.__cell_x += 0.5 * self.__cell_width
            self.drawHexagon(self.__cell_x, self.__cell_y+3, self.__cell_side_length, colour, character=True, fill=True)
        elif self.maze.getMazeType() == "triangular":
            self.__cell_x, self.__cell_y = cell.getID()
            self.__cell_x, self.__cell_y = (self.__cell_x * self.__cell_width) + self.__cell_width/2 , self.__cell_y * self.__cell_height  + self.__cell_height/2 
            self.__cell_base_point_1, self.__cell_base_point_2 = self.get_triangle_base_points(cell.getID()[0], cell.getID()[1])
            self.__cell_flipped = self.getCellFlipped(cell)
            self.drawTriangle(self.__cell_base_point_1, self.__cell_base_point_2, self.__cell_side_length, self.__cell_flipped, colour, fill=True, character=True)   
    

    def getDistanceColour(self, distance):
        # Define the RGB tuples for green, orange, and red
        green = (0, 255, 0)
        orange = (255, 165, 0)
        red = (255, 0, 0)

        # Normalize the distance to the range [0, 1]
        distance = max(0, min(distance, 1))

        # Calculate the color based on the distance
        if distance < 0.5:
            # Interpolate between green and orange
            interp = distance * 2
            r = int(green[0] + (orange[0] - green[0]) * interp)
            g = int(green[1] + (orange[1] - green[1]) * interp)
            b = int(green[2] + (orange[2] - green[2]) * interp)
        else:
            # Interpolate between orange and red
            interp = (distance - 0.5) * 2
            r = int(orange[0] + (red[0] - orange[0]) * interp)
            g = int(orange[1] + (red[1] - orange[1]) * interp)
            b = int(orange[2] + (red[2] - orange[2]) * interp)

        return (r, g, b)


    def showHint(self):
        self.__hint_cell = self.maze.getHint(self.__current_cell)
        print(self.__hint_cell)
        if not self.__show_hint:
            self.__hints_used += 1
        self.__show_hint = True
        if self.__hint_cell != None:
            self.highlightCell(self.__hint_cell, colour=self.HINT_COLOUR)
        else:
            print("No hint available!")

    def getHintsUsed(self):
        return self.__hints_used
        
    def showDistanceMap(self):
        if self.__distanceMap == None:
            self.__distanceMap = self.maze.getDistanceMap(self.__current_cell)
        
        self.__show_distance_map = True
        self.__dividing_factor = max(self.__distanceMap.values())
        self.__normalised_distance_map = dict()
        for cell, distance in self.__distanceMap.items():
            self.__normalised_distance_map[cell] = distance / self.__dividing_factor

        for cell, distance in self.__normalised_distance_map.items():
            self.highlightCell(self.maze.getGrid()[cell[1]][cell[0]], colour=self.getDistanceColour(distance))

    def hideDistanceMap(self):
        self.__show_distance_map = False
        self.__distanceMap = None

    def showSolution(self):
        if self.__solution == None:
            self.__solution = self.maze.getSolution()
        self.__show_solution = True
        for cell in self.__solution:
            self.highlightCell(cell, colour=self.YELLOW)
        self.__solutionShown = True

    def hideSolution(self):
        self.__show_solution = False
        self.__solution = None

    def getDistanceMapStatus(self):
        return self.__show_distance_map
    
    def getIncorrectMoves(self):
        return self.__incorrect_moves
    
    def getTimeTaken(self):
        return time.time() - self.__time_taken
    
    def generatePerformanceMetrics(self):
        self.__solutionLength = len(self.maze.getSolution())
        self.__optimalityScore = (self.__solutionLength - self.__incorrect_moves) / self.__solutionLength
        self.__movesPerSecond = sum(self.__cellTimes) / len(self.__cellTimes)
    
    def updateMovesPerSecond(self):
        self.__cellTimes.append(time.time() - self.__CellTime)
        self.__CellTime = time.time()

    def getPseudocodeText(self, solve_algorithm):
        return self.PSUEDOCODE[self.TITLE_DICT[solve_algorithm]]

    def getProgramStateText(self):
        self.__currentNeighbours, self.__currentStackQueue = self.__maze.getProgramState(self.__current_cell)
        self.__currentNeighboursText = "Current neighbours: " + str(self.__currentNeighbours)
        if self.__maze.getSolveAlgorithmName() == "depth_first":
            self.__currentStackQueueText = "Current stack: " + str(self.__currentStackQueue)
        else:
            self.__currentStackQueueText = "Current queue: " + str(self.__currentStackQueue)

        self.__currentCellText = "Current cell: " + str(self.__current_cell.getID())
        return self.__currentNeighboursText, self.__currentStackQueueText, self.__currentCellText
    
    def displayMaze(self):
        self.__screen.fill(self.WHITE)
        if self.__show_distance_map:
            self.showDistanceMap()
        if self.__show_solution:
            self.showSolution()
        if self.maze.getMazeType() == "square":
            self.__points = []
            self.__cell_width = self.__maze_width / self.maze.getMazeWidth()
            self.__cell_height = self.__maze_height / self.maze.getMazeHeight()
            self.highlightVisitedCells()
            if self.__show_hint:
                self.highlightCell(self.__hint_cell, colour=self.HINT_COLOUR)
            pg.draw.rect(self.__screen, self.CHARACTERCOLOUR, (self.__current_cell.getID()[0] * self.__cell_width + 3, self.__current_cell.getID()[1] * self.__cell_height + 3, self.__cell_width, self.__cell_height))
            self.__token_visited_cells_coords.append((self.__current_cell.getID()[0] * self.__cell_width, self.__current_cell.getID()[1] * self.__cell_height))
            
            for y in range(self.maze.getMazeHeight()):
                for x in range(len(self.maze.getGrid()[y])):
                    cell = self.maze.getGrid()[y][x]
                    self.__curr_points = [(x * self.__cell_width, y * self.__cell_height), ((x+1) * self.__cell_width, y * self.__cell_height), ((x+1) * self.__cell_width, (y+1) * self.__cell_height), (x * self.__cell_width, (y+1) * self.__cell_height)]
                    self.__points.append(self.__curr_points)
                    if y == 0 or self.maze.getGrid()[y-1][x] not in cell.getConnections():
                        pg.draw.line(self.__screen, self.BLACK, (x *  self.__cell_width, y *  self.__cell_height), 
                                                    ((x+1) *  self.__cell_width, y *  self.__cell_height), self.SQUAREMAZETHICKNESS)
                    if x == 0 or not(str(self.maze.getGrid()[y][x-1]) in [str(i) for i in cell.getConnections()]):
                        pg.draw.line(self.__screen, self.BLACK, (x *  self.__cell_width, y *  self.__cell_height), 
                                                    (x *  self.__cell_width, (y+1) *  self.__cell_height), self.SQUAREMAZETHICKNESS)

        elif self.maze.getMazeType() == "hexagonal":
            self.__points = []
            self.__offsetWidth = self.__maze_width*0.025
            self.__offsetHeight = self.__maze_height*0.025
            self.__cell_width = ((self.__maze_width*0.9) / self.maze.getMazeWidth())
            self.__cell_side_length =  2*((self.__cell_width / 2) / math.tan(math.pi / 3))
            self.__cell_height = (self.__cell_side_length * 2) - (self.__cell_side_length / 2)
            self.__current_cell_x = self.__current_cell.getID()[0] * self.__cell_width + self.__cell_width/2 + self.__offsetWidth
            self.__current_cell_y = self.__current_cell.getID()[1] * self.__cell_height  + self.__cell_height/2 + self.__offsetHeight 

            if self.__current_cell.getID()[1] % 2 == 1:
                self.__current_cell_x += 0.5 * self.__cell_width

            self.__token_visited_cells_coords.append((self.__current_cell_x, self.__current_cell_y))
            if self.__show_hint:
                self.highlightCell(self.__hint_cell, colour=self.HINT_COLOUR)
            self.highlightVisitedCells()
             
            self.drawHexagon(self.__current_cell_x, self.__current_cell_y+3, self.__cell_side_length, self.CHARACTERCOLOUR, character=True, fill=True)
           
            
            for y in range(self.maze.getMazeHeight()):
                for x in range(len(self.maze.getGrid()[y])):
                    
                    cell = self.maze.getGrid()[y][x]
                    self.__curr_x =  (x * self.__cell_width) + (self.__cell_width/2)  + self.__offsetWidth
                    self.__curr_y = (y * (self.__cell_height)) + (self.__cell_width/2)  + self.__offsetHeight
                    if y % 2 == 1:
                        self.__curr_x += 0.5 * self.__cell_width
                        
                    self.__cell_connections = cell.getConnections()

                    self.drawHexagon(self.__curr_x, self.__curr_y, self.__cell_side_length)

                    for c in self.__cell_connections:
                        self.draw_hexagon_connection(self.maze.getGrid()[y][x], c, self.__curr_x, self.__curr_y, self.__cell_side_length, self.__offsetWidth, self.__offsetHeight)

        elif self.maze.getMazeType() == "triangular":
            self.__points = []
            self.__cell_height = ((self.__maze_height*0.95) / (self.maze.getMazeHeight()))
            self.__cell_side_length = self.__cell_height / math.sin(math.pi/3)
            self.__cell_width = self.__cell_side_length / 2
            self.__current_cell_base_point_1, self.__current_cell_base_point_2 = self.get_triangle_base_points(self.__current_cell.getID()[0], self.__current_cell.getID()[1])
            
            self.highlightVisitedCells()

            self.__current_cell_flipped = self.getCellFlipped(self.__current_cell)
            if self.__show_hint:
                self.highlightCell(self.__hint_cell, colour=self.HINT_COLOUR)
        
            self.drawTriangle(self.__current_cell_base_point_1, self.__current_cell_base_point_2, self.__cell_side_length, self.__current_cell_flipped, self.CHARACTERCOLOUR, fill=True, character=True)
            self.__token_visited_cells_coords.append((self.__current_cell_base_point_1, self.__current_cell_base_point_2, self.__cell_side_length ,self.__current_cell_flipped))
            
            for y in range(self.maze.getMazeHeight()):
                for x in range(len(self.maze.getGrid()[y])):
                   
                    cell = self.maze.getGrid()[y][x]
                    self.__base_1, self.__base_2 = self.get_triangle_base_points(x, y)
                    self.__flipped = self.getCellFlipped(cell)
                    self.drawTriangle(self.__base_1, self.__base_2, self.__cell_side_length, self.__flipped)
                    self.__cell_connections = cell.getConnections()

                    for c in self.__cell_connections:
                         self.draw_triangle_connection(self.maze.getGrid()[y][x], c, self.__cell_side_length)

    def initPygame(self, maze=None):
        pg.init()
        self.maze = maze

        self.__infoObject = pg.display.Info()

        self.__width, self.__height = self.__infoObject.current_w*0.6, self.__infoObject.current_h*0.8
        self.__show_distance_map = False
        self.__maze_width, self.__maze_height = self.__width, self.__height
        self.__addedPoints = False
        self.__incorrect_moves = 0
        self.__show_hint = False
        self.__hints_used = 0
        self.__distanceMap = None
        self.__solution = None
        self.__show_solution = False
        self.__solutionShown = False

        self.__time_taken = time.time()
        self.__CellTime = time.time()
        self.__cellTimes = []
        self.__screen = pg.display.set_mode((self.__width, self.__height))
        self.__screen.fill(self.WHITE)
        self.__current_cell = self.maze.getGrid()[0][0]
        self.__token_visited_cells_coords = []
        self.__running = True

    def updatePygame(self):
        if self.__running:
            self.displayMaze()
            
            self.cell_hover()
            pg.display.flip()
            if self.maze.getMazeType() == "square":
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.__running = False

                    elif event.type == pg.MOUSEBUTTONDOWN:
                        x, y = pg.mouse.get_pos()
                        if x < self.__maze_width:
                            self.__clicked_cell = self.cell_hover(clicked=True)
                            print(self.__clicked_cell)
                            if self.__clicked_cell != None:
                                self.__solve_step_return_value = self.maze.solve_step(self.cell_hover(clicked=True).getID(), self.__current_cell)

                                if self.__solve_step_return_value == "end":
                                    self.__current_cell = self.maze.getGrid()[self.maze.getMazeHeight()-1][self.maze.getMazeWidth()-1]
                                    self.displayMaze()
                                    
                                    print("Congratulations! You solved the maze!")
                                    self.__running = False
                                    self.displayMaze()
                                    return True
                                elif self.__solve_step_return_value == "invalid_move":
                                    print("Invalid move!")
                                elif self.__solve_step_return_value == "wrong_move":
                                    print("Wrong move!")
                                    self.__incorrect_moves += 1
                                else:
                                    self.__current_cell = self.__solve_step_return_value
                                    self.__show_hint = False
                                    self.__show_distance_map = False
                                    self.__distanceMap = None
                                self.updateMovesPerSecond()
                        else:
                            print("Invalid move!")
                self.__screen.fill(self.WHITE)
            elif self.maze.getMazeType() == "hexagonal":
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.__running = False
                    
                    elif event.type == pg.MOUSEBUTTONDOWN:
                        x, y = pg.mouse.get_pos()
                        if x < self.__maze_width:
                            self.__clicked_cell = self.cell_hover(clicked=True)
                            print(self.__clicked_cell)
                            if self.__clicked_cell != None:
                                self.__solve_step_return_value = self.maze.solve_step(self.cell_hover(clicked=True).getID() , self.__current_cell)
                                if self.__solve_step_return_value == "end":
                                    self.__current_cell = self.maze.getGrid()[self.maze.getMazeHeight()-1][len(self.maze.getGrid()[self.maze.getMazeHeight()-1])-1]
                                    
                                    print("Congratulations! You solved the maze!")
                                    self.__running = False
                                    self.displayMaze()
                                    return True
                                elif self.__solve_step_return_value == "invalid_move":
                                    print("Invalid move!")
                                elif self.__solve_step_return_value == "wrong_move":
                                    print("Wrong move!")
                                    self.__incorrect_moves += 1

                                else:
                                    self.__current_cell = self.__solve_step_return_value
                                    self.__show_hint = False
                                    self.__show_distance_map = False
                                    self.__distanceMap = None
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
                            print(self.__clicked_cell)
                            if self.__clicked_cell != None:
                                self.__solve_step_return_value = self.maze.solve_step(self.__clicked_cell.getID() , self.__current_cell)
                                if self.__solve_step_return_value == "end":
                                    self.__current_cell = self.maze.getGrid()[self.maze.getMazeHeight()-1][len(self.maze.getGrid()[self.maze.getMazeHeight()-1])-1]
                                    
                                    print("Congratulations! You solved the maze!")
                                    self.__running = False
                                    self.displayMaze()

                                    return True
                                elif self.__solve_step_return_value == "invalid_move":
                                    print("Invalid move!")
                                elif self.__solve_step_return_value == "wrong_move":
                                    print("Wrong move!")
                                    self.__incorrect_moves += 1
                                else:
                                    self.__current_cell = self.__solve_step_return_value
                                    self.__show_hint = False
                                    self.__show_distance_map = False
                                    self.__distanceMap = None
                            else:
                                print("Invalid move!")
                self.__screen.fill(self.WHITE)
            
    def quitPygame(self):
        self.generatePerformanceMetrics()
        self.__summary_stats = {
            
            "time_taken": time.time() - self.__time_taken,
            "hints_used": self.__hints_used,
            "incorrect_moves": self.__incorrect_moves,
            "gen_algorithm": self.maze.getGenAlgorithmName(),
            "solve_algorithm": self.maze.getSolveAlgorithmName(),
            "maze_type": self.maze.getMazeType(),
            "maze_width": self.maze.getMazeWidth(),
            "maze_height": self.maze.getMazeHeight(),
            "solution_length": self.__solutionLength,
            "optimality_score": self.__optimalityScore,
            "moves_per_second": self.__movesPerSecond,
            "solution_shown": self.__solutionShown
        }
        return self.__summary_stats
        
    def downloadMaze(self):
        try:
            now = datetime.datetime.now()
            formatted_now = now.strftime("%Y%m%d_%H%M%S")
            dir_name = "pictures"
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            pg.image.save(self.__screen, os.path.join(dir_name, f"maze_screenshot_{formatted_now}.png"))
            return True
        except:
            return False
        
    def closeProgram(self):
        pg.quit()

    def run(self):
        pass

class Ui_MazeSolveWindow(QMainWindow):
    def __init__(self, desktopWidth, desktopHeight, genAlgorithm, solveAlgorithm, mazeType, mazeWidth, mazeHeight):
        super(Ui_MazeSolveWindow, self).__init__()
        self.desktopWidth = desktopWidth
        self.desktopHeight = desktopHeight
        self.genAlgorithm = genAlgorithm
        self.solveAlgorithm = solveAlgorithm
        self.mazeType = mazeType
        self.UIinstance = UI()
        self.mazeWidth = mazeWidth
        self.mazeHeight = mazeHeight

        self.setupUi()
        self.startPygameLoop()

        self.show()

    def setupUi(self):
        self.setObjectName("MazeSolveWindow")
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        initial_width = self.desktopWidth * 0.7  # 70% of the desktop width
        initial_height = self.desktopHeight * 0.7  
        self.resize(initial_width, initial_height)
        # Main Layout
        mainLayout = QtWidgets.QGridLayout(self.centralwidget)

        # Create GroupBoxes
        self.States = QGroupBox("Program State", self.centralwidget)
        self.actionsBox = QGroupBox("Actions", self.centralwidget)
        self.summaryBox = QGroupBox("Summary", self.centralwidget)
        self.pseudocodeBox = QGroupBox("Psuedocode", self.centralwidget)

        # Add GroupBoxes to layout
        mainLayout.addWidget(self.States, 1, 0, 1, 1)
        mainLayout.addWidget(self.actionsBox, 0, 1, 1, 1)
        mainLayout.addWidget(self.summaryBox, 1, 1, 1, 1)
        mainLayout.addWidget(self.pseudocodeBox, 0, 0, 1, 1)

        # Buttons
        self.showHintButton = QPushButton("Show Hint", self.actionsBox)
        self.showDistanceMapButton = QPushButton("Show Distance Map", self.actionsBox)
        self.showSolutionButton = QPushButton("Show solution", self.actionsBox)
        self.quitButton = QPushButton("Quit", self.actionsBox)

        self.showHintButton.clicked.connect(lambda: self.showHint())
        self.showDistanceMapButton.clicked.connect(lambda: self.showDistanceMap())
        self.showSolutionButton.clicked.connect(lambda: self.showSolution())
        self.quitButton.clicked.connect(lambda: self.quitSolving())

        # Add Buttons to layout
        actionLayout = QtWidgets.QVBoxLayout(self.actionsBox)
        actionLayout.addWidget(self.showHintButton)
        actionLayout.addWidget(self.showDistanceMapButton)
        actionLayout.addWidget(self.showSolutionButton)
        actionLayout.addWidget(self.quitButton)

        # Labels
        self.timeTakenLabel = QLabel("Time: 0s", self.summaryBox)
        self.incorrectMovesLabel = QLabel("Incorrect Moves: 0", self.summaryBox)
        self.hintsUsedLabel = QLabel("Hints used: 0", self.summaryBox)
        self.pseudocodeLabel = QLabel(self.getPseudocode(self.solveAlgorithm), self.pseudocodeBox)
        self.programStateLabel = QLabel("State", self.States)

        # Add Labels to layout
        summaryLayout = QtWidgets.QVBoxLayout(self.summaryBox)
        summaryLayout.addWidget(self.timeTakenLabel)
        summaryLayout.addWidget(self.incorrectMovesLabel)
        summaryLayout.addWidget(self.hintsUsedLabel)

        pseudoLayout = QtWidgets.QVBoxLayout(self.pseudocodeBox)
        pseudoLayout.addWidget(self.pseudocodeLabel)

        self.incorrect_moves_timer = QTimer(self)
        self.incorrect_moves_timer.timeout.connect(lambda: self.updateIncorrectMoves())
        self.incorrect_moves_timer.start(500) 

        self.hide_distance_map_timer = QTimer(self)
        self.hide_distance_map_timer.timeout.connect(lambda: self.getDistanceMapStatus())
        self.hide_distance_map_timer.start(500)

        self.get_time_taken_timer = QTimer(self)
        self.get_time_taken_timer.timeout.connect(lambda: self.getTimeTaken())
        self.get_time_taken_timer.start(1000)

        self.update_program_state_timer = QTimer(self)
        self.update_program_state_timer.timeout.connect(lambda: self.getProgramState())
        self.update_program_state_timer.start(1000)

        self.resizeEvent = self.onResize

    def onResize(self, event):
        # Update font size based on window size
        base_font_size = max(self.width() / 80, 8)  # Adjust base font size
        font = QtGui.QFont()
        font.setPointSize(base_font_size)
        font.setUnderline(True)

        self.States.setFont(font)
        self.actionsBox.setFont(font)
        self.summaryBox.setFont(font)
        self.pseudocodeBox.setFont(font)

        font.setPointSize(base_font_size * 0.6)  # Adjust for smaller font
        font.setUnderline(False)
        self.showHintButton.setFont(font)
        self.showDistanceMapButton.setFont(font)
        self.showSolutionButton.setFont(font)
        self.quitButton.setFont(font)
        self.timeTakenLabel.setFont(font)
        self.incorrectMovesLabel.setFont(font)
        self.hintsUsedLabel.setFont(font)
        self.pseudocodeLabel.setFont(font)

        super(Ui_MazeSolveWindow, self).resizeEvent(event)

    def getPseudocode(self, algorithm):
        return self.UIinstance.getPseudocodeText(algorithm)
    
    def getProgramState(self):
        self.__currentNeighboursText, self.__currentStackQueueText, self.__currentCellText = self.UIinstance.getProgramStateText()
        self.programStateLabel.setText(self.__currentCellText + "\n" + self.__currentNeighboursText + "\n" + self.__currentStackQueueText)

    def startPygameLoop(self):
        self.maze = Mazes.Maze(mazeType=self.mazeType, gen_algorithm=self.genAlgorithm, solve_algorithm=self.solveAlgorithm, mazeWidth=self.mazeWidth, mazeHeight=self.mazeHeight)
        self.maze.generate()
        self.UIinstance.initPygame(self.maze)

        self.pygame_timer = QTimer(self)
        self.pygame_timer.timeout.connect(lambda: self.updatePygame())
        self.pygame_timer.start(33)  # 30 fps

    def updatePygame(self):
        if self.UIinstance.updatePygame():
            self.pygame_timer.stop()
            self.hide_distance_map_timer.stop()
            self.incorrect_moves_timer.stop()
            self.get_time_taken_timer.stop()
            self.__summaryStats = self.UIinstance.quitPygame()
            self.hide()
            self.NextWindow = Ui_DialogMazeSolved(self.desktopWidth, self.desktopHeight, self.__summaryStats, self.UIinstance)
            self.NextWindow.show()

            
    def showHint(self):
        self.UIinstance.showHint()
        self.hintsUsedLabel.setText("Hints used: " + str(self.UIinstance.getHintsUsed()))

    def getDistanceMapStatus(self):
        if not self.UIinstance.getDistanceMapStatus():
            self.showDistanceMapButton.setText("Show Distance Map")

    def showDistanceMap(self):
        if self.showDistanceMapButton.text() == "Show Distance Map":
            self.showDistanceMapButton.setText("Hide Distance Map")
            self.UIinstance.showDistanceMap()
        else:
            self.showDistanceMapButton.setText("Show Distance Map")
            self.UIinstance.hideDistanceMap()

    def updateIncorrectMoves(self):
        self.incorrectMovesLabel.setText("Incorrect Moves: " + str(self.UIinstance.getIncorrectMoves()))

    def showSolution(self):
        if self.showSolutionButton.text() == "Show solution":
            self.showSolutionButton.setText("Hide solution")
            self.UIinstance.showSolution()
        else:
            self.showSolutionButton.setText("Show solution")
            self.UIinstance.hideSolution()

    def getTimeTaken(self):
        self.timeTakenLabel.setText("Time: " + str(int(self.UIinstance.getTimeTaken())) + "s")

    def quitSolving(self):
        self.pygame_timer.stop()
        self.hide_distance_map_timer.stop()
        self.incorrect_moves_timer.stop()
        self.get_time_taken_timer.stop()
        self.UIinstance.quitPygame()
        self.hide()
        self.BackWindow = Ui_MainMenu(self.desktopWidth, self.desktopHeight)
        self.BackWindow.show()

class Ui_DialogMazeSolved(QMainWindow):
    def __init__(self, desktopWidth, desktopHeight, summaryStats, UIinstance):
        super(Ui_DialogMazeSolved, self).__init__()
        self.desktopWidth = desktopWidth
        self.desktopHeight = desktopHeight
        self.__summaryStats = summaryStats
        self.__UIinstance = UIinstance

        self.setupUi()
        self.show()

    def setupUi(self):
        self.setObjectName("Dialog")
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        initial_width = self.desktopWidth * 0.7
        initial_height = self.desktopHeight * 0.7
        self.resize(initial_width, initial_height)

        mainLayout = QGridLayout(self.centralwidget)

        self.summaryGroupBox = QGroupBox("Summary Stats", self.centralwidget)
        self.mazeSolvedGroupBox = QGroupBox("Maze Solved", self.centralwidget)
        self.actionButtonsGroupBox = QGroupBox("Action Buttons", self.centralwidget)

        mainLayout.addWidget(self.summaryGroupBox, 0, 0)
        mainLayout.addWidget(self.mazeSolvedGroupBox, 0, 1)
        mainLayout.addWidget(self.actionButtonsGroupBox, 1, 0, 1, 2)

        # Summary GroupBox
        summaryLayout = QVBoxLayout(self.summaryGroupBox)
        self.__time_taken = self.__summaryStats['time_taken']
        if self.__time_taken >= 60:
            self.__timeTakenText = f"Time Taken: {int(self.__time_taken/60)}m {int(self.__time_taken%60)}s"
        else:
            self.__timeTakenText = f"Time Taken: {int(self.__time_taken)}s"

        self.timeTakenLabel = QLabel(f"{self.__timeTakenText}", self.summaryGroupBox)
        self.hintsUsedLabel = QLabel(f"Hints Used: {self.__summaryStats['hints_used']}", self.summaryGroupBox)
        self.incorrectMovesLabel = QLabel(f"Incorrect Moves: {self.__summaryStats['incorrect_moves']}", self.summaryGroupBox)
        self.optimalityScoreLabel = QLabel(f"Optimality Score: {(self.__summaryStats['optimality_score']*100):.2f}%", self.summaryGroupBox)
        self.movesPerSecondLabel = QLabel(f"Moves Per Second: {self.__summaryStats['moves_per_second']:.2f}", self.summaryGroupBox)
        self.solutionLengthLabel = QLabel(f"Solution Length: {self.__summaryStats['solution_length']}", self.summaryGroupBox)

        summaryLayout.addWidget(self.timeTakenLabel)
        summaryLayout.addWidget(self.hintsUsedLabel)
        summaryLayout.addWidget(self.incorrectMovesLabel)
        summaryLayout.addWidget(self.optimalityScoreLabel)
        summaryLayout.addWidget(self.movesPerSecondLabel)
        summaryLayout.addWidget(self.solutionLengthLabel)
        # Maze Solved GroupBox

        mazeSolvedLayout = QVBoxLayout(self.mazeSolvedGroupBox)
        self.generationAlgorithmLabel = QLabel(f"Generation Algorithm: {self.__summaryStats['gen_algorithm']}", self.mazeSolvedGroupBox)
        self.solvingAlgorithmLabel = QLabel(f"Solving Algorithm: {self.__summaryStats['solve_algorithm']}", self.mazeSolvedGroupBox)
        self.mazeTypeLabel = QLabel(f"Maze Type: {self.__summaryStats['maze_type']}", self.mazeSolvedGroupBox)
        self.mazeWidthLabel = QLabel(f"Maze Width: {self.__summaryStats['maze_width']}", self.mazeSolvedGroupBox)
        self.mazeHeightLabel = QLabel(f"Maze Height: {self.__summaryStats['maze_height']}", self.mazeSolvedGroupBox)

        mazeSolvedLayout.addWidget(self.generationAlgorithmLabel)
        mazeSolvedLayout.addWidget(self.solvingAlgorithmLabel)
        mazeSolvedLayout.addWidget(self.mazeTypeLabel)
        mazeSolvedLayout.addWidget(self.mazeWidthLabel)
        mazeSolvedLayout.addWidget(self.mazeHeightLabel)

        # Action Buttons GroupBox
        actionButtonsLayout = QVBoxLayout(self.actionButtonsGroupBox)
        self.returnToMenuButton = QPushButton("Return to Menu", self.actionButtonsGroupBox)
        self.downloadMazeButton = QPushButton("Download Maze", self.actionButtonsGroupBox)
        actionButtonsLayout.addWidget(self.returnToMenuButton)
        actionButtonsLayout.addWidget(self.downloadMazeButton)
        self.returnToMenuButton.clicked.connect(lambda: self.returnToMenu())
        self.downloadMazeButton.clicked.connect(lambda: self.downloadMaze())

        self.resizeEvent = self.onResize

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        # Set the texts for all the labels and buttons as per your requirement


    def onResize(self, event):
        base_font_size = max(self.width() / 80, 8)
        font = QtGui.QFont()
        font.setPointSize(base_font_size)

        
        # Set font for all group boxes
        # Set font for all labels and buttons with adjusted size
        self.summaryGroupBox.setFont(font)
        self.mazeSolvedGroupBox.setFont(font)
        self.actionButtonsGroupBox.setFont(font)

        font.setPointSize(base_font_size * 0.6)  # Adjust for smaller font
        font.setUnderline(False)

        self.timeTakenLabel.setFont(font)
        self.hintsUsedLabel.setFont(font)
        self.incorrectMovesLabel.setFont(font)
        self.optimalityScoreLabel.setFont(font)
        self.movesPerSecondLabel.setFont(font)
        self.solutionLengthLabel.setFont(font)
        self.generationAlgorithmLabel.setFont(font)
        self.solvingAlgorithmLabel.setFont(font)
        self.mazeTypeLabel.setFont(font)
        self.mazeWidthLabel.setFont(font)
        self.mazeHeightLabel.setFont(font)
        self.returnToMenuButton.setFont(font)
        self.downloadMazeButton.setFont(font)

        super(Ui_DialogMazeSolved, self).resizeEvent(event)

    def returnToMenu(self):
        self.__UIinstance.closeProgram()
        self.hide()
        self.BackWindow = Ui_MainMenu(self.desktopWidth, self.desktopHeight)
        self.BackWindow.show()

    def downloadMaze(self):
        self.__UIinstance.downloadMaze()

        #ERROR HANDLE THE MAZE DOWNLOAD HERE.

class TerminalUI():

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

        self.GUI = Ui_MazeSolveWindow(self.screenWidth, self.screenHeight, self.__gen_algorithms[int(genAlgorithm)-1], self.__solve_algorithms[int(solveAlgorithm)-1], int(mazeType), int(mazeSize))
        self.GUI.show()

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
        # MazeSizeSliderX and MazeSizeText
        self.MazeSizeSliderX = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.MazeSettingsContainer)
        self.MazeSizeSliderX.setMinimum(5)
        self.MazeSizeSliderX.setMaximum(100)
        groupBoxLayout.addWidget(self.MazeSizeSliderX)
        self.MazeSizeTextX = QtWidgets.QLabel("Maze Width: 5", self.MazeSettingsContainer)
        groupBoxLayout.addWidget(self.MazeSizeTextX)

        self.MazeSizeSliderY = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.MazeSettingsContainer)
        self.MazeSizeSliderY.setMinimum(5)
        self.MazeSizeSliderY.setMaximum(100)
        groupBoxLayout.addWidget(self.MazeSizeSliderY)
        self.MazeSizeTextY = QtWidgets.QLabel("Maze Height: 5", self.MazeSettingsContainer)
        groupBoxLayout.addWidget(self.MazeSizeTextY)
        

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
        self.MazeSizeSliderX.setToolTip(_translate("GenerateMazeMenu", "Maze Width"))
        self.MazeSizeTextX.setText(_translate("GenerateMazeMenu", "Maze Width: 5"))
        self.MazeSizeSliderY.setToolTip(_translate("GenerateMazeMenu", "Maze Height"))
        self.MazeSizeTextY.setText(_translate("GenerateMazeMenu", "Maze Height: 5"))
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

        self.MazeSizeSliderX.valueChanged.connect(self.MazeSizeSliderX_valueChanged)
        self.MazeSizeSliderY.valueChanged.connect(self.MazeSizeSliderY_valueChanged)
        self.GenerateMazeButton.clicked.connect(self.GenerateMazeButton_clicked)
        self.BackButton.clicked.connect(self.BackButton_clicked)

    def MazeSizeSliderX_valueChanged(self):
        self.MazeSizeTextX.setText("Maze Width: " + str(self.MazeSizeSliderX.value()))


    def MazeSizeSliderY_valueChanged(self):
        self.MazeSizeTextY.setText("Maze Height: " + str(self.MazeSizeSliderY.value()))
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
            self.solveAlgorithm =  "depth_first"
        elif self.BFSRadioButton.isChecked():
            self.solveAlgorithm = "breadth_first"
        elif self.ManualRadioButton.isChecked():
            self.solveAlgorithm = "manual"
        else:
            self.solveAlgorithm = None

        if self.SquareRadioButton.isChecked():
            self.mazeType = 1
        elif self.HexagonalRadioButton.isChecked():
            self.mazeType = 2
        elif self.TriangularRadioButton.isChecked():
            self.mazeType = 3
        else:
            self.mazeType = None
        if self.genAlgorithm != None and self.solveAlgorithm != None and self.mazeType != None:
            self.hide()
            self.ForwardWindow = Ui_MazeSolveWindow(self.desktopWidth, self.desktopHeight, self.genAlgorithm, self.solveAlgorithm, self.mazeType, self.MazeSizeSliderX.value(), self.MazeSizeSliderY.value())
            self.ForwardWindow.show()
        else:
            self.Dialog = QtWidgets.QDialog()
            self.error = Ui_Dialog()
            self.error.setupUi(self.Dialog, self.desktopWidth, self.desktopHeight)
            self.Dialog.show()
        self.mazeConfig = [self.genAlgorithm, self.solveAlgorithm, self.mazeType, self.MazeSizeSliderX.value(), self.MazeSizeSliderY.value()]

    def getMazeConfig(self):
        if self.mazeConfig != None:
            return self.mazeConfig
        else:
            return None


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


