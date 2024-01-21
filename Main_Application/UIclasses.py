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
import sys
import re
import json
import requests
import ast
from screeninfo import get_monitors
from PyQt5 import QtWidgets, QtCore, QtGui, QtWebSockets
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QWidget, QDialog, QGroupBox, QGridLayout, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import QTimer, QThread, QUrl
from PyQt5.QtWebSockets import QWebSocket
from functools import partial

class UI():         
    __WHITE = (255, 255, 255)
    __BLACK = (0, 0, 0)
    __RED = (255, 0 , 0)
    __GREEN = (0, 255, 0)
    __BLUE = (0, 0, 255)
    __YELLOW = (255, 255, 0)
    __HOVER_COLOUR = (200, 200, 200)
    __HIGHLIGHT_COLOUR = (187, 216, 236)
    __HINT_COLOUR = (255, 255, 0)
    __CHARACTERCOLOUR = (0, 32, 235)
    __OPPONENTCOLOUR = (255, 0, 0)

    __TITLE_DICT = {"sidewinder": "Sidewinder", "binary_tree": "Binary Tree", "depth_first": "Depth First Search", "breadth_first": "Breadth First Search", "manual": "Manual solve"}

    __INSTRUCTIONS = {
        "Breadth First Search": "Breadth First Search is a search algorithm that traverses the maze by exploring all of the neighbour cells of the current cell before moving on to the next cell.",
        "Depth First Search": "Depth First Search is a search algorithm that traverses the maze by exploring the first neighbour cell of the current cell before moving on to the next cell.",
        "Manual solve": "Manual solve allows the user to solve the maze themselves. Use the arrow keys to move the cell around the maze. The cell can only move to a cell that is connected to it. Have fun!",
    }
    __PSUEDOCODE = {
        "Breadth First Search": "1. Add the starting cell to the queue\n2. While the queue is not empty:\n\t3. Remove the first cell from the queue\n\t4. If the cell is the end cell, return the path\n\t5. For each neighbour of the cell:\n\t\t6. If the neighbour has not been visited:\n\t\t\t7. Add the neighbour to the queue\n\t\t\t8. Set the neighbour's parent to be the current cell\n9. Return that no path exists",
        "Depth First Search": "1. Add the starting cell to the stack\n2. While the stack is not empty:\n\t3. Remove the first cell from the stack\n\t4. If the cell is the end cell, return the path\n\t5. For each neighbour of the cell:\n\t\t6. If the neighbour has not been visited:\n\t\t\t7. Add the neighbour to the stack\n\t\t\t8. Set the neighbour's parent to be the current cell\n9. Return that no path exists",
        "Manual solve": ""
    }

    __DESKTOP_WIDTH = get_monitors()[0].width
    __DESKTOP_HEIGHT = get_monitors()[0].height

    def __init__(self):
        self.__maze = None

    def is_inside_polygon(self, x, y, poly):
        """
        Checks if a point (x, y) is inside a polygon defined by a list of vertices.

        Args:
            x (float): The x-coordinate of the point.
            y (float): The y-coordinate of the point.
            poly (List[Tuple[float, float]]): The list of vertices defining the polygon.

        Returns:
            bool: True if the point is inside the polygon, False otherwise.
        """
        n = len(poly)  # Get the number of vertices in the polygon
        inside = False  # Initialize the flag to False
        p1x, p1y = poly[0]  # Get the first vertex of the polygon
        for i in range(n + 1):  # Loop through each vertex
            p2x, p2y = poly[i % n]  # Get the next vertex of the polygon
            if y > min(p1y, p2y):  # Check if the point is within the vertical bounds of the edge
                if y <= max(p1y, p2y):  # Check if the point is within the vertical bounds of the edge
                    if x <= max(p1x, p2x):  # Check if the point is to the left of the edge
                        if p1y != p2y:  # Check if the edge is not horizontal
                            # Compute the x-coordinate of the intersection of the edge with the horizontal line through the point
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:  # Check if the point is to the left of the intersection
                            inside = not inside  # If so, flip the flag
            p1x, p1y = p2x, p2y  # Move to the next edge
        return inside  # Return the flag
    
    def cell_hover(self, clicked=False):
        self.__mouse_pos_x, self.__mouse_pos_y = pg.mouse.get_pos()
        if self.__maze.getMazeType() == "square":
            for p in self.__points:
                if self.__mouse_pos_x > self.__maze_width and self.__mouse_pos_y > self.__maze_height:
                    break
                if self.is_inside_polygon(self.__mouse_pos_x, self.__mouse_pos_y, p):
                    self.__cell_x = self.__points.index(p)
                    counter = 0
                    flag = False
                    for y in range(self.__maze.getMazeHeight()):
                        for x in range(len(self.__maze.getGrid()[y])):
                            if counter == self.__cell_x:
                                self.__cell = self.__maze.getGrid()[y][x]
                                flag = True
                                break
                            counter += 1
                        if flag:
                            break         
                    pg.draw.rect(self.__screen, self.__HOVER_COLOUR, (self.__cell.getID()[0] * self.__cell_width, self.__cell.getID()[1] * self.__cell_height, self.__cell_width, self.__cell_height), self.__squareMazeThickness)
                    pg.mouse.set_cursor(*pg.cursors.broken_x)
                    if clicked:
                        return self.__cell
                    break

        elif self.__maze.getMazeType() == "hexagonal":
            for p in self.__points:
                if self.__mouse_pos_x > self.__maze_width and self.__mouse_pos_y > self.__maze_height:
                    break
                if self.is_inside_polygon(self.__mouse_pos_x, self.__mouse_pos_y, p):
                    self.__cell_x = self.__points.index(p)
                    counter = 0
                    flag = False
                    for y in range(self.__maze.getMazeHeight()):
                        for x in range(len(self.__maze.getGrid()[y])):
                            if counter == self.__cell_x:
                                self.__cell = self.__maze.getGrid()[y][x] 
                                flag = True
                                break
                            counter += 1
                        if flag:
                            break                            
                    pg.draw.polygon(self.__screen, self.__HOVER_COLOUR, p, self.__hexagonMazeThickness)
                    pg.mouse.set_cursor(*pg.cursors.broken_x)
                    if clicked:
                        return self.__cell
                    break
        elif self.__maze.getMazeType() == "triangular":
            for p in self.__points:
                if self.__mouse_pos_x > self.__maze_width and self.__mouse_pos_y > self.__maze_height:
                    break
                if self.is_inside_polygon(self.__mouse_pos_x, self.__mouse_pos_y, p):
                    
                    self.__cell_x = self.__points.index(p)
                    counter = 0
                    flag = False
                    for y in range(self.__maze.getMazeHeight()):
                        
                        for x in range(len(self.__maze.getGrid()[y])):
              
                            if counter == self.__cell_x:
                                self.__cell = self.__maze.getGrid()[y][x]
                                
                                flag = True
                                break
                            counter += 1
                        if flag:
                            break                            
                    pg.draw.polygon(self.__screen, self.__HOVER_COLOUR, p, self.__triangularMazeThickness)
                    pg.mouse.set_cursor(*pg.cursors.broken_x)
                    if clicked:
                        return self.__cell
                    break
                
    def highlightVisitedCells(self):
        for cell in self.__token_visited_cells_coords:
            if self.__maze.getMazeType() == "square":
                pg.draw.rect(self.__screen, self.__HIGHLIGHT_COLOUR, (cell.getID()[0] * self.__cell_width, cell.getID()[1] * self.__cell_height, self.__cell_width, self.__cell_height), 0)
                
            elif self.__maze.getMazeType() == "hexagonal":
                cell_x, cell_y = cell.getID()
                cell_x, cell_y = (cell_x * self.__cell_width) + self.__cell_width/2 + self.__offsetWidth, cell_y * self.__cell_height  + self.__cell_height/2 + self.__offsetHeight
                if cell.getID()[1] % 2 == 1:
                    cell_x += 0.5 * self.__cell_width
                self.drawHexagon(cell_x, cell_y, self.__cell_side_length, self.__HIGHLIGHT_COLOUR, character=True, fill=True)
                
            elif self.__maze.getMazeType() == "triangular":
                cell_x, cell_y = cell.getID()
                cell_x, cell_y = (cell_x * self.__cell_width) + self.__cell_width/2 , cell_y * self.__cell_height  + self.__cell_height/2
                cell_base_point_1, cell_base_point_2 = self.get_triangle_base_points(cell.getID()[0], cell.getID()[1])
                cell_flipped = self.getCellFlipped(cell)
                self.drawTriangle(cell_base_point_1, cell_base_point_2, self.__cell_side_length, cell_flipped, self.__HIGHLIGHT_COLOUR, fill=True, character=True)

    def drawHexagon(self, x, y, size, color=(0, 0, 0), width=0, character=False, fill=False):
        __hexagon_points = []
        for i in range(6):
            __angle_deg = 60 * i -30
            __angle_rad = math.pi / 180 * __angle_deg
            __hexagon_points.append((x + size * math.cos(__angle_rad), y + size * math.sin(__angle_rad)))
        if fill:
            pg.draw.polygon(self.__screen, color, __hexagon_points, 0)
        else:
            pg.draw.polygon(self.__screen, color, __hexagon_points, self.__hexagonMazeThickness)
        if not character:
            self.__points.append(__hexagon_points)

    def draw_hexagon_connection(self, cell1, cell2, x, y, size, offsetWidth, offsetHeight):
        # draw a white line between the two cells
        self.__cell1_x, self.__cell1_y = x, y
        self.__cell2_x, self.__cell2_y = cell2.getID()
        self.__cell2_x, self.__cell2_y = (self.__cell2_x * self.__cell_width) + offsetWidth + (self.__cell_width/2) , self.__cell2_y * self.__cell_height  + self.__cell_height/2 + offsetHeight



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

        pg.draw.line(self.__screen, self.__WHITE, (self.__start_x, self.__start_y), (self.__end_x, self.__end_y), self.__hexagonMazeThickness)

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
            pg.draw.polygon(self.__screen, color, triangle_points, self.__triangularMazeThickness)
        if not character and not(triangle_points in self.__points):
            
            self.__points.append(triangle_points)        


    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def draw_triangle_connection(self, cell1, cell2, size):
        if cell1.checkConnection(cell2):

            self.__cell1_base_point_1, self.__cell1_base_point_2 = self.get_triangle_base_points(cell1.getID()[0], cell1.getID()[1])
            self.__cell2_base_point_1, self.__cell2_base_point_2 = self.get_triangle_base_points(cell2.getID()[0], cell2.getID()[1])

            if list(map(int, self.__cell1_base_point_1)) == list(map(int, self.__cell2_base_point_1)):
                line_start = self.__cell1_base_point_1
                line_end = self.__cell1_base_point_2

            elif self.distance(self.__cell1_base_point_1[0], self.__cell1_base_point_1[1], self.__cell2_base_point_2[0], self.__cell2_base_point_2[1] ) < self.distance(self.__cell1_base_point_2[0], self.__cell1_base_point_2[1], self.__cell2_base_point_1[0], self.__cell2_base_point_1[1] ):
                line_start = self.__cell1_base_point_1
                line_end = self.__cell2_base_point_2
            else:
                line_start = self.__cell1_base_point_2
                line_end = self.__cell2_base_point_1
            pg.draw.line(self.__screen, self.__WHITE, line_start, line_end, self.__triangularMazeThickness)

    def getCellFlipped(self, cell):
        x, y = cell.getID()
        flipped = False
        if x % 2 == 1:
            flipped = True
        if y%2 == 1:
            flipped = not flipped
        return flipped

    def highlightCell(self, cell, colour=None):
        if self.__maze.getMazeType() == "square":
            pg.draw.rect(self.__screen, colour, (cell.getID()[0] * self.__cell_width, cell.getID()[1] * self.__cell_height, self.__cell_width, self.__cell_height), 0)
        elif self.__maze.getMazeType() == "hexagonal":
            self.__cell_x, self.__cell_y = cell.getID()
            self.__cell_x, self.__cell_y = (self.__cell_x * self.__cell_width) + self.__cell_width/2 + self.__offsetWidth, self.__cell_y * self.__cell_height  + self.__cell_height/2 + self.__offsetHeight 
            if cell.getID()[1] % 2 == 1:
                self.__cell_x += 0.5 * self.__cell_width
            self.drawHexagon(self.__cell_x, self.__cell_y+3, self.__cell_side_length, colour, character=True, fill=True)
        elif self.__maze.getMazeType() == "triangular":
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
        self.__hint_cell = self.__maze.getHint(self.__current_cell)
        if not self.__show_hint:
            self.__hints_used += 1
        self.__show_hint = True
        if self.__hint_cell != None:
            self.highlightCell(self.__hint_cell, colour=self.__HINT_COLOUR)
        else:
            self.__dialog = Ui_Dialog("There are no hints available for this maze. Try solving it yourself!", self.__DESKTOP_WIDTH, self.__DESKTOP_HEIGHT)
            self.__dialog.show()

    def getHintsUsed(self):
        return self.__hints_used
        
    def showDistanceMap(self):
        if self.__distanceMap == None:
            self.__distanceMap = self.__maze.getDistanceMap(self.__current_cell)
        
        self.__show_distance_map = True
        self.__dividing_factor = max(self.__distanceMap.values())
        self.__normalised_distance_map = dict()
        for cell, distance in self.__distanceMap.items():
            self.__normalised_distance_map[cell] = distance / self.__dividing_factor

        for cell, distance in self.__normalised_distance_map.items():
            self.highlightCell(self.__maze.getGrid()[cell[1]][cell[0]], colour=self.getDistanceColour(distance))

    def hideDistanceMap(self):
        self.__show_distance_map = False
        self.__distanceMap = None

    def showSolution(self):
        if self.__solution == None:
            self.__solution = self.__maze.getSolution()
        self.__show_solution = True
        for cell in self.__solution:
            self.highlightCell(cell, colour=self.__YELLOW)
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
        self.__solutionLength = len(self.__maze.getSolution())
        self.__optimalityScore =  self.__solutionLength / (self.__solutionLength + self.__incorrect_moves)
        self.__movesPerSecond = len(self.__cellTimes) / sum(self.__cellTimes) 
    
    def updateMovesPerSecond(self):
        self.__cellTimes.append(time.time() - self.__CellTime)
        self.__CellTime = time.time()

    def getPseudocodeText(self, solve_algorithm):
        return self.__PSUEDOCODE[self.__TITLE_DICT[solve_algorithm]]

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
        self.__screen.fill(self.__WHITE)
        if self.__show_distance_map:
            self.showDistanceMap()
        if self.__show_solution:
            self.showSolution()
        if self.__maze.getMazeType() == "square":
            self.__points = []
            self.__cell_width = self.__maze_width / self.__maze.getMazeWidth()
            self.__cell_height = self.__maze_height / self.__maze.getMazeHeight()
            self.highlightVisitedCells()
            
            if self.__display_opponent_move:
                if self.__opponent_current_cell != None:
                    self.highlightCell(self.__opponent_current_cell, colour=self.__OPPONENTCOLOUR)

            if self.__show_hint:
                self.highlightCell(self.__hint_cell, colour=self.__HINT_COLOUR)
            pg.draw.rect(self.__screen, self.__CHARACTERCOLOUR, (self.__current_cell.getID()[0] * self.__cell_width + 3, self.__current_cell.getID()[1] * self.__cell_height + 3, self.__cell_width, self.__cell_height))
            self.__token_visited_cells_coords.append(self.__current_cell)
            
            for y in range(self.__maze.getMazeHeight()):
                for x in range(len(self.__maze.getGrid()[y])):
                    cell = self.__maze.getGrid()[y][x]
                    self.__curr_points = [(x * self.__cell_width, y * self.__cell_height), ((x+1) * self.__cell_width, y * self.__cell_height), ((x+1) * self.__cell_width, (y+1) * self.__cell_height), (x * self.__cell_width, (y+1) * self.__cell_height)]
                    self.__points.append(self.__curr_points)
                    if y == 0 or self.__maze.getGrid()[y-1][x] not in cell.getConnections():
                        pg.draw.line(self.__screen, self.__BLACK, (x *  self.__cell_width, y *  self.__cell_height), 
                                                    ((x+1) *  self.__cell_width, y *  self.__cell_height), self.__squareMazeThickness)
                    if x == 0 or not(str(self.__maze.getGrid()[y][x-1]) in [str(i) for i in cell.getConnections()]):
                        pg.draw.line(self.__screen, self.__BLACK, (x *  self.__cell_width, y *  self.__cell_height), 
                                                    (x *  self.__cell_width, (y+1) *  self.__cell_height), self.__squareMazeThickness)

        elif self.__maze.getMazeType() == "hexagonal":
            self.__points = []
            self.__offsetWidth = self.__maze_width*0.025
            self.__offsetHeight = self.__maze_height*0.025
            self.__cell_width = ((self.__maze_width*0.8) / self.__maze.getMazeWidth())
            self.__cell_side_length =  2*((self.__cell_width / 2) / math.tan(math.pi / 3))
            self.__cell_height = (self.__cell_side_length * 2) - (self.__cell_side_length / 2)
            self.__current_cell_x = self.__current_cell.getID()[0] * self.__cell_width + self.__cell_width/2 + self.__offsetWidth
            self.__current_cell_y = self.__current_cell.getID()[1] * self.__cell_height  + self.__cell_height/2 + self.__offsetHeight 

            if self.__current_cell.getID()[1] % 2 == 1:
                self.__current_cell_x += 0.5 * self.__cell_width

            self.__token_visited_cells_coords.append(self.__current_cell)
            self.highlightVisitedCells()

            if self.__display_opponent_move:
                if self.__opponent_current_cell != None:
                    self.highlightCell(self.__opponent_current_cell, colour=self.__OPPONENTCOLOUR)

            if self.__show_hint:
                self.highlightCell(self.__hint_cell, colour=self.__HINT_COLOUR)
             
            self.drawHexagon(self.__current_cell_x, self.__current_cell_y, self.__cell_side_length, self.__CHARACTERCOLOUR, character=True, fill=True)
           
            for y in range(self.__maze.getMazeHeight()):
                for x in range(len(self.__maze.getGrid()[y])):
                    
                    cell = self.__maze.getGrid()[y][x]
                    self.__curr_x =  (x * self.__cell_width) + (self.__cell_width/2)  + self.__offsetWidth
                    self.__curr_y = (y * (self.__cell_height)) + (self.__cell_height/2)  + self.__offsetHeight
                    if y % 2 == 1:
                        self.__curr_x += 0.5 * self.__cell_width
                        
                    self.__cell_connections = cell.getConnections()

                    self.drawHexagon(self.__curr_x, self.__curr_y, self.__cell_side_length)

                    for c in self.__cell_connections:
                        self.draw_hexagon_connection(self.__maze.getGrid()[y][x], c, self.__curr_x, self.__curr_y, self.__cell_side_length, self.__offsetWidth, self.__offsetHeight)

        elif self.__maze.getMazeType() == "triangular":
            self.__points = []
            self.__cell_height = ((self.__maze_height*0.95) / (self.__maze.getMazeHeight()))
            self.__cell_side_length = self.__cell_height / math.sin(math.pi/3)
            self.__cell_width = self.__cell_side_length / 2
            self.__current_cell_base_point_1, self.__current_cell_base_point_2 = self.get_triangle_base_points(self.__current_cell.getID()[0], self.__current_cell.getID()[1])
            
            self.highlightVisitedCells()
            if self.__display_opponent_move:
                if self.__opponent_current_cell != None:
                    self.highlightCell(self.__opponent_current_cell, colour=self.__OPPONENTCOLOUR)
            self.__current_cell_flipped = self.getCellFlipped(self.__current_cell)
            if self.__show_hint:
                self.highlightCell(self.__hint_cell, colour=self.__HINT_COLOUR)
        
            self.drawTriangle(self.__current_cell_base_point_1, self.__current_cell_base_point_2, self.__cell_side_length, self.__current_cell_flipped, self.__CHARACTERCOLOUR, fill=True, character=True)
            self.__token_visited_cells_coords.append(self.__current_cell)
            
            for y in range(self.__maze.getMazeHeight()):
                for x in range(len(self.__maze.getGrid()[y])):
                   
                    cell = self.__maze.getGrid()[y][x]
                    self.__base_1, self.__base_2 = self.get_triangle_base_points(x, y)
                    self.__flipped = self.getCellFlipped(cell)
                    self.drawTriangle(self.__base_1, self.__base_2, self.__cell_side_length, self.__flipped)
                    self.__cell_connections = cell.getConnections()

                    for c in self.__cell_connections:
                         self.draw_triangle_connection(self.__maze.getGrid()[y][x], c, self.__cell_side_length)

    def scale_thickness(self):
        self.__potentialSquareMazeThickness = list(range(1, 7))
        self.__potentialHexagonMazeThickness = list(range(1, 4))
        self.__potentialTriangularMazeThickness = list(range(1, 6))

        self.__squareMazeThickness = self.__potentialSquareMazeThickness[::-1][min(int(self.DESKTOP_WIDTH/ self.__width)-1, len(self.__potentialSquareMazeThickness)-1)]
        self.__hexagonMazeThickness = self.__potentialHexagonMazeThickness[::-1][min(int(self.DESKTOP_WIDTH/ self.__width)-1, len(self.__potentialHexagonMazeThickness)-1)]
        self.__triangularMazeThickness = self.__potentialTriangularMazeThickness[::-1][min(int(self.DESKTOP_WIDTH/ self.__width)-1, len(self.__potentialTriangularMazeThickness)-1)]

    def initPygame(self, maze=None, gui=False):
        pg.init()
        if gui:
            self.__UiType = "GUI"
        self.__maze = maze
        self.__infoObject = pg.display.Info()
        self.__width, self.__height = self.__DESKTOP_WIDTH*0.7, self.__DESKTOP_HEIGHT*0.7

        self.__show_distance_map = False
        self.__maze_width, self.__maze_height = self.__width, self.__height
        self.__display_opponent_move = True

        self.__opponent_current_cell = None
        self.__addedPoints = False
        self.__incorrect_moves = 0
        self.__show_hint = False
        self.__hints_used = 0
        self.__distanceMap = None
        self.__solution = None
        self.__show_solution = False
        self.__solutionShown = False    
        self.__points = []
        

        self.__squareMazeThickness = 6
        self.__hexagonMazeThickness = 3
        self.__triangularMazeThickness = 5

        self.__time_taken = time.time()
        self.__CellTime = time.time()
        self.__cellTimes = []
        self.__screen = pg.display.set_mode((self.__width, self.__height), pg.RESIZABLE)
        pg.display.set_caption("CompSci Maze Master")

        self.__screen.fill(self.__WHITE)
        self.__current_cell = self.__maze.getGrid()[0][0]
        self.__token_visited_cells_coords = []
        self.__running = True

    def updatePygame(self):
        if self.__running:
            
            self.displayMaze()
            self.cell_hover()
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.__running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    x, y = pg.mouse.get_pos()
                    if x < self.__maze_width:
                        self.__clicked_cell = self.cell_hover(clicked=True)
                        if self.__clicked_cell != None:
                            self.__solve_step_return_value = self.__maze.solve_step(self.cell_hover(clicked=True).getID(), self.__current_cell)
                            if self.__solve_step_return_value == "end":
                                self.__current_cell = self.__maze.getGrid()[self.__maze.getMazeHeight()-1][self.__maze.getMazeWidth()-1]
                                self.displayMaze()
                                self.__running = False
                                return True
                            elif self.__solve_step_return_value == "invalid_move":
                                if self.__UiType == "GUI":
                                    self.__dialog = Ui_Dialog("Invalid move!", self.__DESKTOP_WIDTH, self.__DESKTOP_HEIGHT)
                                    self.__dialog.show()
                                else:
                                    print("Invalid move!")
                            elif self.__solve_step_return_value == "wrong_move":
                                if self.__UiType == "GUI":
                                    self.__dialog = Ui_Dialog("Wrong move!", self.__DESKTOP_WIDTH, self.__DESKTOP_HEIGHT)
                                    self.__dialog.show()
                                else:
                                    print("Wrong move!")
                                self.__incorrect_moves += 1
                            else:
                                self.__current_cell = self.__solve_step_return_value
                                self.__show_hint = False
                                self.__show_distance_map = False
                                self.__distanceMap = None
                            self.updateMovesPerSecond()
                    else:
                        if self.__UiType == "GUI":
                            self.__dialog = Ui_Dialog("Please click inside the maze!", self.__DESKTOP_WIDTH, self.__DESKTOP_HEIGHT)
                            self.__dialog.show()
                        else:
                            print("Please click inside the maze!")
                       
                elif event.type == pg.VIDEORESIZE:
                    
                    self.__oldWidth, self.__oldHeight = self.__width, self.__height

                    width, height = event.w, event.h
                    self.__screen = pg.display.set_mode((width, height), pg.RESIZABLE)
                    
                    self.__infoObject = pg.display.Info()

                    self.__width, self.__height = self.__infoObject.current_w, self.__infoObject.current_h
                    self.__show_distance_map = False
                    self.__maze_width, self.__maze_height = self.__width, self.__height
                    
                    self.__scale_thickness()

                        
            self.__screen.fill(self.__WHITE)

    def quitPygame(self):
        self.generatePerformanceMetrics()
        self.__summary_stats = {
            
            "time_taken": time.time() - self.__time_taken,
            "hints_used": self.__hints_used,
            "incorrect_moves": self.__incorrect_moves,
            "gen_algorithm": self.__TITLE_DICT[self.__maze.getGenAlgorithmName()],
            "solve_algorithm": self.__TITLE_DICT[self.__maze.getSolveAlgorithmName()],
            "maze_type": self.__maze.getMazeType().capitalize(),
            "maze_width": self.__maze.getMazeWidth(),
            "maze_height": self.__maze.getMazeHeight(),
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

    def getCurrentCell(self):
        return self.__current_cell    

    def updateOpponentMove(self, cellID):
        self.__opponent_current_cell = self.__maze.getGrid()[cellID[1]][cellID[0]]

    def closeProgram(self):
        pg.quit()

    def run(self):
        pass

class Ui_MazeSolveWindow(QMainWindow):
    def __init__(self, desktopWidth, desktopHeight, genAlgorithm, solveAlgorithm, mazeType, mazeWidth, mazeHeight, mazeGrid=None, LANInstance=None, online=False):
        super(Ui_MazeSolveWindow, self).__init__()
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.__genAlgorithm = genAlgorithm
        self.__solveAlgorithm = solveAlgorithm
        self.__mazeType = mazeType
        self.__UIinstance = UI()
        self.__mazeWidth = mazeWidth
        self.__mazeHeight = mazeHeight
        self.__LANInstance = LANInstance
        self.__mazeGrid = mazeGrid
        self.__online = online
        self.__opponentWon = False
        self.setWindowTitle("CompSci Maze Master")
        self.setupUi()
        with open("Main_Application/style.css", "r") as f:
            self.setStyleSheet(f.read())
        self.startPygameLoop()
        self.show()

    def setupUi(self):
        self.setObjectName("MazeSolveWindow")
        self.__centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.__centralwidget)
        initial_width = self.__desktopWidth * 0.7  # 70% of the desktop width
        initial_height = self.__desktopHeight * 0.7  
        self.resize(initial_width, initial_height)

        self.__menubar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.__menubar)

        self.__menuHelp = QtWidgets.QMenu("Help", self)
        self.__menuExit = QtWidgets.QMenu("Exit", self)

        # Adding actions to the menus
        self.__actionAbout = QtWidgets.QAction("Help Documentation", self)
        self.__actionExit = QtWidgets.QAction("Exit", self)

        self.__menuHelp.addAction(self.__actionAbout)
        self.__menuExit.addAction(self.__actionExit)

        self.__menubar.addMenu(self.__menuHelp)
        self.__menubar.addMenu(self.__menuExit)

        # Connect actions to slots
        self.__actionAbout.triggered.connect(self.about_action_triggered)
        self.__actionExit.triggered.connect(self.exit_action_triggered)

        # Main Layout
        mainLayout = QtWidgets.QGridLayout(self.__centralwidget)

        # Create GroupBoxes
        self.__States = QGroupBox("Program State", self.__centralwidget)
        self.__actionsBox = QGroupBox("Actions", self.__centralwidget)
        self.__summaryBox = QGroupBox("Summary", self.__centralwidget)
        self.__pseudocodeBox = QGroupBox("Psuedocode", self.__centralwidget)

    # Conditionally hide pseudocode and program state group boxes based on maze type
        if self.__solveAlgorithm == "manual":
            self.__States.setVisible(False)
            self.__pseudocodeBox.setVisible(False)
            # Make the other two boxes take up the entire window
            mainLayout.addWidget(self.__actionsBox, 0, 0, 1, 2)  # Span 2 columns
            mainLayout.addWidget(self.__summaryBox, 1, 0, 1, 2)  # Span 2 columns
        else:
            # The regular layout if not 'manual'
            mainLayout.addWidget(self.__States, 1, 0, 1, 1)
            mainLayout.addWidget(self.__actionsBox, 0, 1, 1, 1)
            mainLayout.addWidget(self.__summaryBox, 1, 1, 1, 1)
            mainLayout.addWidget(self.__pseudocodeBox, 0, 0, 1, 1)
        
        # Buttons

        self.__showDistanceMapButton = QPushButton("Show Distance Map", self.__actionsBox)
        self.__showSolutionButton = QPushButton("Show solution", self.__actionsBox)
        self.__quitButton = QPushButton("Quit", self.__actionsBox)

        self.__showDistanceMapButton.clicked.connect(lambda: self.showDistanceMap())
        self.__showSolutionButton.clicked.connect(lambda: self.showSolution())
        self.__quitButton.clicked.connect(lambda: self.quitSolving())

        # Add Buttons to layout
        actionLayout = QtWidgets.QVBoxLayout(self.__actionsBox)
        actionLayout.addWidget(self.__showDistanceMapButton)
        actionLayout.addWidget(self.__showSolutionButton)
        actionLayout.addWidget(self.__quitButton)

        # Labels
        self.__timeTakenLabel = QLabel("Time: 0s", self.__summaryBox)

        # Add Labels to layout
        summaryLayout = QtWidgets.QVBoxLayout(self.__summaryBox)
        summaryLayout.addWidget(self.__timeTakenLabel)
        
        self.__hide_distance_map_timer = QTimer(self)
        self.__hide_distance_map_timer.timeout.connect(lambda: self.getDistanceMapStatus())
        self.__hide_distance_map_timer.start(500)

        self.__get_time_taken_timer = QTimer(self)
        self.__get_time_taken_timer.timeout.connect(lambda: self.getTimeTaken())
        self.__get_time_taken_timer.start(1000)

        if self.__solveAlgorithm != "manual":
            self.__incorrectMovesLabel = QLabel("Incorrect Moves: 0", self.__summaryBox)
            self.__hintsUsedLabel = QLabel("Hints used: 0", self.__summaryBox)

            summaryLayout.addWidget(self.__incorrectMovesLabel)
            summaryLayout.addWidget(self.__hintsUsedLabel)

            self.__pseudocodeLabel = QLabel(self.getPseudocode(self.__solveAlgorithm), self.__pseudocodeBox)
            self.__programStateLabel = QLabel("State", self.__States)

            self.__showHintButton = QPushButton("Show Hint", self.__actionsBox)
            self.__showHintButton.clicked.connect(lambda: self.showHint())

            self.__update_program_state_timer = QTimer(self)
            self.__update_program_state_timer.timeout.connect(lambda: self.getProgramState())
            self.__update_program_state_timer.start(1000)

            self.__incorrect_moves_timer = QTimer(self)
            self.__incorrect_moves_timer.timeout.connect(lambda: self.updateIncorrectMoves())
            self.__incorrect_moves_timer.start(500) 
            
            # Add labels to state layout
            stateLayout = QtWidgets.QVBoxLayout(self.__States)
            stateLayout.addWidget(self.__programStateLabel)
        
            pseudoLayout = QtWidgets.QVBoxLayout(self.__pseudocodeBox)
            pseudoLayout.addWidget(self.__pseudocodeLabel)

            actionLayout.addWidget(self.__showHintButton)

        self.resizeEvent = self.onResize

    def onResize(self, event):
        # Update font size based on window size
        base_font_size = max(min(self.width() / 80, self.height() / 80), 14)  # Use the smaller dimension to scale font      
        font = QtGui.QFont()

        font.setPointSize(base_font_size)
        font.setUnderline(True)
        
        self.__actionsBox.setFont(font)
        self.__summaryBox.setFont(font)
        if self.__solveAlgorithm != "manual":
            self.__States.setFont(font)
            self.__pseudocodeBox.setFont(font)

        font.setPointSize(base_font_size * 0.8)  # Adjust for smaller font
        font.setUnderline(False)
        
        self.__showDistanceMapButton.setFont(font)
        self.__showSolutionButton.setFont(font)
        self.__quitButton.setFont(font)
        self.__timeTakenLabel.setFont(font)
       
        if self.__solveAlgorithm != "manual":

            self.__showHintButton.setFont(font)
            self.__incorrectMovesLabel.setFont(font)
            self.__hintsUsedLabel.setFont(font)
            self.__pseudocodeLabel.setFont(font)
            self.__programStateLabel.setFont(font)

        super(Ui_MazeSolveWindow, self).resizeEvent(event)

    def mazeToJSON(self, maze):
        self.__mazeType = maze.getMazeType()
        if self.__mazeType == "square":
            self.__mazeType = 1
        elif self.__mazeType == "hexagonal":
            self.__mazeType = 2
        elif self.__mazeType == "triangular":
            self.__mazeType = 3

        mazeDict = {
            "maze_type": self.__mazeType,
            "maze_width": maze.getMazeWidth(),
            "maze_height": maze.getMazeHeight(),
            "gen_algorithm": maze.getGenAlgorithmName(),
            "solve_algorithm": maze.getSolveAlgorithmName(),
            "grid": dict()
        }

        for y in range(maze.getMazeHeight()):
            mazeDict["grid"][y] = []
            for x in range(len(maze.getGrid()[y])):
                cell = maze.getGrid()[y][x]
                cellDict = {
                    "id": cell.getID(),
                    "connections": [str(c) for c in cell.getConnections()]
                }
                mazeDict["grid"][y].append(cellDict)

        return mazeDict
    
    def about_action_triggered(self):
        pass

    def exit_action_triggered(self):
        sys.exit()

    def getPseudocode(self, algorithm):
        return self.__UIinstance.getPseudocodeText(algorithm)

    def getProgramState(self):
        self.__currentNeighboursText, self.__currentStackQueueText, self.__currentCellText = self.__UIinstance.getProgramStateText()
        self.__programStateLabel.setText(self.__currentCellText + "\n" + self.__currentNeighboursText + "\n" + self.__currentStackQueueText)

    def startPygameLoop(self):
        if self.__mazeGrid != None:
            self.__maze = Mazes.Maze(mazeType=self.__mazeType, gen_algorithm=self.__genAlgorithm, solve_algorithm=self.__solveAlgorithm, mazeWidth=self.__mazeWidth, mazeHeight=self.__mazeHeight, mazeGrid=self.__mazeGrid)
        else:
            self.__maze = Mazes.Maze(mazeType=self.__mazeType, gen_algorithm=self.__genAlgorithm, solve_algorithm=self.__solveAlgorithm, mazeWidth=self.__mazeWidth, mazeHeight=self.__mazeHeight)
        self.__maze.generate()

        if self.__online and self.__mazeGrid == None:
            self.__LANInstance.sendMaze(self.mazeToJSON(self.__maze))

        self.__UIinstance.initPygame(self.__maze, gui=True)

        self.__pygame_timer = QTimer(self)
        self.__pygame_timer.timeout.connect(lambda: self.updatePygame())
        self.__pygame_timer.start(33)  # 30 fps

        if self.__online:
            self.__update_opponent_timer = QTimer(self)
            self.__update_opponent_timer.timeout.connect(lambda: self.updateOpponent())
            self.__update_opponent_timer.start(100)
            
            self.__get_opponent_move_timer = QTimer(self)
            self.__get_opponent_move_timer.timeout.connect(lambda: self.getOpponentMove())
            self.__get_opponent_move_timer.start(100)

            self.__check_opponent_win_timer = QTimer(self)
            self.__check_opponent_win_timer.timeout.connect(lambda: self.checkOpponentWin())
            self.__check_opponent_win_timer.start(1000)
            
            self.__check_opponent_disconnected_timer = QTimer(self)
            self.__check_opponent_disconnected_timer.timeout.connect(lambda: self.checkOpponentDisconnected())
            self.__check_opponent_disconnected_timer.start(1000)

    def updateOpponent(self):
        self.__currentCellID = self.__UIinstance.getCurrentCell().getID()
        self.__LANInstance.sendCurrentCell(self.__currentCellID)

    def getOpponentMove(self):
        self.__opponentMove = self.__LANInstance.getOpponentMove()
        if self.__opponentMove != None:
            self.__UIinstance.updateOpponentMove(self.__opponentMove)

    def checkOpponentWin(self):
        if self.__LANInstance.checkOpponentWin():
            self.__opponentWon = True
            self.__opponentWonDialog = Ui_OpponentWonDialog("Your opponent has won!", self.__desktopWidth, self.__desktopHeight)
            self.__opponentWonDialog.show()
            while self.__opponentWonDialog.getContinuePlayingState() == None:
                QtWidgets.QApplication.processEvents( QtCore.QEventLoop.AllEvents, 1000)
            if self.__opponentWonDialog.getContinuePlayingState():
                self.__opponentWonDialog.close()
            else:
                self.__opponentWonDialog.close()
                self.quitSolving()    
            
    def checkOpponentDisconnected(self):
        if self.__LANInstance.checkOpponentDisconnected():
            self.__LANInstance.sendWin()
            self.__opponentWon = True

    def updatePygame(self):
        if self.__UIinstance.updatePygame():
            self.__pygame_timer.stop()
            self.__hide_distance_map_timer.stop()
            self.__get_time_taken_timer.stop()
            self.__summaryStats = self.__UIinstance.quitPygame()

            if self.__solveAlgorithm != "manual":
                self.__update_program_state_timer.stop()
                self.__incorrect_moves_timer.stop()

            if self.__online:
                self.__update_opponent_timer.stop()
                self.__get_opponent_move_timer.stop()
                self.__check_opponent_win_timer.stop()
                if not(self.__opponentWon):
                    self.__LANInstance.sendWin()
                
            self.hide()
            self.__NextWindow = Ui_DialogMazeSolved(self.__desktopWidth, self.__desktopHeight, self.__summaryStats, self.__UIinstance, self.__LANInstance, self.__online)
            self.__NextWindow.show()

            
    def showHint(self):
        self.__UIinstance.showHint()
        self.__hintsUsedLabel.setText("Hints used: " + str(self.__UIinstance.getHintsUsed()))

    def getDistanceMapStatus(self):
        if not self.__UIinstance.getDistanceMapStatus():
            self.__showDistanceMapButton.setText("Show Distance Map")

    def showDistanceMap(self):
        if self.__showDistanceMapButton.text() == "Show Distance Map":
            self.__showDistanceMapButton.setText("Hide Distance Map")
            self.__UIinstance.showDistanceMap()
        else:
            self.__showDistanceMapButton.setText("Show Distance Map")
            self.__UIinstance.hideDistanceMap()

    def updateIncorrectMoves(self):
        self.__incorrectMovesLabel.setText("Incorrect Moves: " + str(self.__UIinstance.getIncorrectMoves()))

    def showSolution(self):
        if self.__showSolutionButton.text() == "Show solution":
            self.__showSolutionButton.setText("Hide solution")
            self.__UIinstance.showSolution()
        else:
            self.__showSolutionButton.setText("Show solution")
            self.__UIinstance.hideSolution()

    def getTimeTaken(self):
        self.__timeTakenLabel.setText("Time: " + str(int(self.__UIinstance.getTimeTaken())) + "s")

    def quitSolving(self):
        if self.__solveAlgorithm != "manual":
            self.__incorrect_moves_timer.stop()
            self.__update_program_state_timer.stop()
        
        if self.__online:
            self.__update_opponent_timer.stop()
            self.__get_opponent_move_timer.stop()
            self.__check_opponent_win_timer.stop()
            self.__check_opponent_disconnected_timer.stop()
            
            self.__LANInstance.logout()

        self.__pygame_timer.stop()
        self.__hide_distance_map_timer.stop()
        self.__get_time_taken_timer.stop()
        self.__UIinstance.closeProgram()
        self.hide()
        self.__BackWindow = Ui_MainMenu(self.__desktopWidth, self.__desktopHeight)
        self.__BackWindow.show()

class Ui_DialogMazeSolved(QMainWindow):
    def __init__(self, desktopWidth, desktopHeight, summaryStats, UIinstance, LANInstance=None, online=False):
        super(Ui_DialogMazeSolved, self).__init__()
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.__summaryStats = summaryStats
        self.__UIinstance = UIinstance
        self.__LANInstance = LANInstance
        self.__online = online
        self.setWindowTitle("Summary: Maze Solved")
        self.setupUi()
        with open("Main_Application/style.css", "r") as f:
            self.setStyleSheet(f.read())
        self.show()

    def setupUi(self):
        self.setObjectName("Dialog")
        self.__centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.__centralwidget)

        initial_width = self.__desktopWidth * 0.7
        initial_height = self.__desktopHeight * 0.7
        self.resize(initial_width, initial_height)

        mainLayout = QGridLayout(self.__centralwidget)

        self.__summaryGroupBox = QGroupBox("Summary Stats", self.__centralwidget)
        self.__mazeSolvedGroupBox = QGroupBox("Maze Solved", self.__centralwidget)
        self.__actionButtonsGroupBox = QGroupBox("Action Buttons", self.__centralwidget)

        mainLayout.addWidget(self.__summaryGroupBox, 0, 0)
        mainLayout.addWidget(self.__mazeSolvedGroupBox, 0, 1)
        mainLayout.addWidget(self.__actionButtonsGroupBox, 1, 0, 1, 2)

        # Summary GroupBox
        summaryLayout = QVBoxLayout(self.__summaryGroupBox)
        self.__time_taken = self.__summaryStats['time_taken']
        if self.__time_taken >= 60:
            self.__timeTakenText = f"Time Taken: {int(self.__time_taken/60)}m {int(self.__time_taken%60)}s"
        else:
            self.__timeTakenText = f"Time Taken: {int(self.__time_taken)}s"

        self.__timeTakenLabel = QLabel(f"{self.__timeTakenText}", self.__summaryGroupBox)
        self.__optimalityScoreLabel = QLabel(f"Optimality Score: {(self.__summaryStats['optimality_score']*100):.2f}%", self.__summaryGroupBox)
        self.__movesPerSecondLabel = QLabel(f"Moves Per Second: {self.__summaryStats['moves_per_second']:.2f}", self.__summaryGroupBox)
        self.__solutionLengthLabel = QLabel(f"Optimal Solution Length: {self.__summaryStats['solution_length']}", self.__summaryGroupBox)
        self.__solutionShownLabel = QLabel(f"Solution Shown: {self.__summaryStats['solution_shown']}", self.__summaryGroupBox)

        summaryLayout.addWidget(self.__timeTakenLabel)
        summaryLayout.addWidget(self.__optimalityScoreLabel)
        summaryLayout.addWidget(self.__movesPerSecondLabel)
        summaryLayout.addWidget(self.__solutionLengthLabel)
        summaryLayout.addWidget(self.__solutionShownLabel)
        # Maze Solved GroupBox

        if self.__summaryStats['solve_algorithm'] != "Manual solve":
            self.__hintsUsedLabel = QLabel(f"Hints Used: {self.__summaryStats['hints_used']}", self.__summaryGroupBox)
            self.__incorrectMovesLabel = QLabel(f"Incorrect Moves: {self.__summaryStats['incorrect_moves']}", self.__summaryGroupBox)
            summaryLayout.addWidget(self.__hintsUsedLabel)
            summaryLayout.addWidget(self.__incorrectMovesLabel)

        mazeSolvedLayout = QVBoxLayout(self.__mazeSolvedGroupBox)
        self.__generationAlgorithmLabel = QLabel(f"Generation Algorithm: {self.__summaryStats['gen_algorithm']}", self.__mazeSolvedGroupBox)
        self.__solvingAlgorithmLabel = QLabel(f"Solving Algorithm: {self.__summaryStats['solve_algorithm']}", self.__mazeSolvedGroupBox)
        self.__mazeTypeLabel = QLabel(f"Maze Type: {self.__summaryStats['maze_type']}", self.__mazeSolvedGroupBox)
        self.__mazeWidthLabel = QLabel(f"Maze Width: {self.__summaryStats['maze_width']}", self.__mazeSolvedGroupBox)
        self.__mazeHeightLabel = QLabel(f"Maze Height: {self.__summaryStats['maze_height']}", self.__mazeSolvedGroupBox)

        mazeSolvedLayout.addWidget(self.__generationAlgorithmLabel)
        mazeSolvedLayout.addWidget(self.__solvingAlgorithmLabel)
        mazeSolvedLayout.addWidget(self.__mazeTypeLabel)
        mazeSolvedLayout.addWidget(self.__mazeWidthLabel)
        mazeSolvedLayout.addWidget(self.__mazeHeightLabel)

        # Action Buttons GroupBox
        actionButtonsLayout = QVBoxLayout(self.__actionButtonsGroupBox)
        self.__returnToMenuButton = QPushButton("Return to Menu", self.__actionButtonsGroupBox)
        self.__downloadMazeButton = QPushButton("Download Maze", self.__actionButtonsGroupBox)
        actionButtonsLayout.addWidget(self.__returnToMenuButton)
        actionButtonsLayout.addWidget(self.__downloadMazeButton)
        self.__returnToMenuButton.clicked.connect(lambda: self.returnToMenu())
        self.__downloadMazeButton.clicked.connect(lambda: self.downloadMaze())
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
        self.__summaryGroupBox.setFont(font)
        self.__mazeSolvedGroupBox.setFont(font)
        self.__actionButtonsGroupBox.setFont(font)

        font.setPointSize(base_font_size * 0.6)  # Adjust for smaller font
        font.setUnderline(False)

        self.__timeTakenLabel.setFont(font)
        self.__optimalityScoreLabel.setFont(font)
        self.__movesPerSecondLabel.setFont(font)
        self.__solutionLengthLabel.setFont(font)
        self.__solutionShownLabel.setFont(font)

        self.__generationAlgorithmLabel.setFont(font)
        self.__solvingAlgorithmLabel.setFont(font)
        self.__mazeTypeLabel.setFont(font)
        self.__mazeWidthLabel.setFont(font)
        self.__mazeHeightLabel.setFont(font)
        self.__returnToMenuButton.setFont(font)
        self.__downloadMazeButton.setFont(font)

        if self.__summaryStats['solve_algorithm'] != "Manual solve":
            self.__hintsUsedLabel.setFont(font)
            self.__incorrectMovesLabel.setFont(font)

        super(Ui_DialogMazeSolved, self).resizeEvent(event)

    def returnToMenu(self):
        self.__UIinstance.closeProgram()
        if self.__online:
            self.__LANInstance.logout()
        self.hide()
        self.__BackWindow = Ui_MainMenu(self.__desktopWidth, self.__desktopHeight)
        self.__BackWindow.show()

    def downloadMaze(self):
        if not self.__UIinstance.downloadMaze():
            self.errorDialog = Ui_Dialog("Error downloading maze! Try again.")
            self.errorself.show()

class TerminalUI(UI):

    def __init__(self):
        self.__gen_algorithms = ["sidewinder", "binary_tree"]
        self.__solve_algorithms = ["depth_first", "breadth_first", "manual"]

    def run(self):
        genAlgorithm = input("Please choose an algorithm to generate the maze, 1 for sidewinder, 2 for binary tree: ")
        while genAlgorithm != "1" and genAlgorithm != "2":
            genAlgorithm = input("Please input a valid option, 1 for sidewinder, 2 for binary tree: ")
        
        solveAlgorithm = input("Please choose an algorithm to solve the maze, 1 for DFS, 2 for BFS, 3 for solving manually: ")
        while solveAlgorithm not in ["1", "2", "3"]:
            solveAlgorithm = input("Please input a valid option, 1 for DFS, 2 for BFS, 3 for manual solving: ")
        
        mazeType = input("Please input the type of the maze, 1 for square, 2 for hexagonal, 3 for triangular: ")
        while mazeType not in ["1", "2", "3"]:
            mazeType = input("Please input a valid option, 1 for square, 2 for hexagonal, 3 for triangular: ")

        mazeWidth = input("Please input the width of the maze: ")
        while not mazeWidth.isdigit() or int(mazeWidth) < 5 or int(mazeWidth) > 100:
            mazeWidth = input("Please input a valid size, between 5 and 100: ")
        
        mazeHeight = input("Please input the height of the maze: ")
        while not mazeHeight.isdigit() or int(mazeHeight) < 5 or int(mazeHeight) > 100:
            mazeHeight = input("Please input a valid size, between 5 and 100: ")
        
        self.__maze = Mazes.Maze(mazeType=int(mazeType), gen_algorithm=self.__gen_algorithms[int(genAlgorithm)-1], solve_algorithm=self.__solve_algorithms[int(solveAlgorithm)-1], mazeWidth=int(mazeWidth), mazeHeight=int(mazeHeight))

        self.__maze.generate()
        self.initPygame(self.__maze)
        self.UiType = "terminal"
        while True:
            if self.updatePygame():
                print("Congratulations! You solved the maze!")
                break




class GUI(UI):
    def __init__(self):
        self.__app = QApplication(sys.argv)

        self.__screenWidth = self.__app.desktop().screenGeometry().width()
        self.__screenHeight = self.__app.desktop().screenGeometry().height()
        self.UiType = "GUI"
        self.__GUI = Ui_MainMenu(self.__screenWidth, self.__screenHeight)

    def run(self):
        self.__GUI.show()
        self.__app.exec_()

class Ui_MainMenu(QMainWindow):
    def __init__(self, desktopWidth, desktopHeight):
        super(Ui_MainMenu, self).__init__()
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.setWindowTitle("Main Menu: CompSci Maze Master")
        self.setupUi(self.__desktopWidth, self.__desktopHeight)
        with open("Main_Application/style.css", "r") as f:
            self.setStyleSheet(f.read())

    def setupUi(self, desktopWidth, desktopHeight):
        self.resize(desktopWidth*0.6, desktopHeight*0.6)
        self.setObjectName("MainMenu")
        self.__centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.__centralwidget)

        # Create a vertical layout
        layout = QtWidgets.QVBoxLayout(self.__centralwidget)

        # TitleLabel
        self.__TitleLabel = QtWidgets.QLabel("CompSci Maze Master", self.__centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setUnderline(True)
        self.__TitleLabel.setFont(font)
        self.__TitleLabel.setAlignment(QtCore.Qt.AlignCenter)  # Center alignment
        

        layout.addWidget(self.__TitleLabel)  # Add to layout

        # StartButton
        self.__StartButton = QtWidgets.QPushButton("Generate New Maze", self.__centralwidget)
        self.__StartButton.setObjectName("StartButton")

        # Set font size for the button text
        buttonFont = QtGui.QFont()
        buttonFont.setPointSize(12)  # Adjust the font size as needed
        self.__StartButton.setFont(buttonFont)

        # Set button size
        self.__StartButton.setMinimumSize(250, 100)  # Adjust width and height as needed

        layout.addWidget(self.__StartButton, 0, QtCore.Qt.AlignCenter)  # Add to layout

        # Play over LAN button
        self.__PlayOverLANButton = QtWidgets.QPushButton("Play over LAN", self.__centralwidget)
        self.__PlayOverLANButton.setObjectName("PlayOverLANButton")
        self.__PlayOverLANButton.setFont(buttonFont)
        self.__PlayOverLANButton.setMinimumSize(250, 100)
        layout.addWidget(self.__PlayOverLANButton, 0, QtCore.Qt.AlignCenter)

        # Set layout to central widget
        self.__centralwidget.setLayout(layout)

        self.__menubar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.__menubar)

        self.__menuHelp = QtWidgets.QMenu("Help", self)
        self.__menuExit = QtWidgets.QMenu("Exit", self)

        # Adding actions to the menus
        self.__actionAbout = QtWidgets.QAction("Help Documentation", self)
        self.__actionExit = QtWidgets.QAction("Exit", self)
        self.__actionAbout.triggered.connect(self.about_action_triggered)

        self.__menuHelp.addAction(self.__actionAbout)
        self.__menuExit.addAction(self.__actionExit)

        self.__menubar.addMenu(self.__menuHelp)
        self.__menubar.addMenu(self.__menuExit)

        # Connect actions to slots
        self.__actionAbout.triggered.connect(self.about_action_triggered)
        self.__actionExit.triggered.connect(self.exit_action_triggered)

        

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.__TitleLabel.setText(_translate("MainMenu", "CompSci Maze Master"))
        self.__StartButton.setText(_translate("MainMenu", "Generate New Maze"))
        self.__menuHelp.setTitle(_translate("MainMenu", "Help"))
        self.__menuExit.setTitle(_translate("MainMenu", "Exit"))
        self.__StartButton.clicked.connect(self.StartButton_clicked)
        self.__PlayOverLANButton.clicked.connect(self.PlayOverLANButton_clicked)

    def StartButton_clicked(self):
        self.hide()
        self.__ForwardWindow = Ui_GenerateMazeMenu(self.__desktopWidth, self.__desktopHeight)
        self.__ForwardWindow.show()

    def PlayOverLANButton_clicked(self):
        self.hide()
        self.__ForwardWindow = Ui_Login(self.__desktopWidth, self.__desktopHeight)
        self.__ForwardWindow.show()

    def about_action_triggered(self):
        self.__helpMenu = Ui_HelpMenu(self.__desktopWidth, self.__desktopHeight)
        self.__helpMenu.show()

    def exit_action_triggered(self):
        sys.exit()

class Ui_GenerateMazeMenu(QtWidgets.QMainWindow):
    def __init__(self, desktopWidth, desktopHeight, LANInstance=None, online=False):
        super(Ui_GenerateMazeMenu, self).__init__()
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.__LANInstance = LANInstance
        self.__online = online
        self.setWindowTitle("Generate New Maze: CompSci Maze Master")
        self.setupUi(self.__desktopWidth, self.__desktopHeight)
        with open("Main_Application/style.css", "r") as f:
                    self.setStyleSheet(f.read())
                
    def setupUi(self, desktopWidth, desktopHeight):
        self.resize(self.__desktopWidth * 0.6, self.__desktopHeight * 0.6)
        self.setObjectName("GenerateMazeMenu")
        self.__centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.__centralwidget)
        self.__BackButton = QtWidgets.QPushButton("Back", self)
        self.__BackButton.setGeometry(20, 60, 100, 40)  # Adjust size and position as needed
        self.__BackButton.setObjectName("BackButon")
        # Create a vertical layout
        layout = QtWidgets.QVBoxLayout(self.__centralwidget)

        # TitleGenerateMaze
        self.__TitleGenerateMaze = QtWidgets.QLabel("Generate New Maze", self.__centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.__TitleGenerateMaze.setFont(font)
        self.__TitleGenerateMaze.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.__TitleGenerateMaze)

        # GenAlgorithmContainer with horizontal layout
        self.__GenAlgorithmContainer = QtWidgets.QGroupBox("Generation Algorithm", self.__centralwidget)
        genAlgorithmLayout = QtWidgets.QHBoxLayout()
        genAlgorithmLayout.addStretch(1)
        self.__SidewinderRadioButton = QtWidgets.QRadioButton("Sidewinder", self.__GenAlgorithmContainer)
        genAlgorithmLayout.addWidget(self.__SidewinderRadioButton)
        self.__BinaryTreeRadioButton = QtWidgets.QRadioButton("Binary Tree", self.__GenAlgorithmContainer)
        genAlgorithmLayout.addWidget(self.__BinaryTreeRadioButton)
        genAlgorithmLayout.addStretch(1)
        self.__GenAlgorithmContainer.setLayout(genAlgorithmLayout)
        layout.addWidget(self.__GenAlgorithmContainer)

        # SolveAlgorithmContainer with horizontal layout
        self.__SolveAlgorithmContainer = QtWidgets.QGroupBox("Solving Algorithm", self.__centralwidget)
        solveAlgorithmLayout = QtWidgets.QHBoxLayout()
        solveAlgorithmLayout.addStretch(1)
        self.__DFSRadioButton = QtWidgets.QRadioButton("Depth First Search", self.__SolveAlgorithmContainer)
        solveAlgorithmLayout.addWidget(self.__DFSRadioButton)
        self.__BFSRadioButton = QtWidgets.QRadioButton("Breadth First Search", self.__SolveAlgorithmContainer)
        solveAlgorithmLayout.addWidget(self.__BFSRadioButton)
        self.__ManualRadioButton = QtWidgets.QRadioButton("Manual Solve", self.__SolveAlgorithmContainer)
        solveAlgorithmLayout.addWidget(self.__ManualRadioButton)
        solveAlgorithmLayout.addStretch(1)
        self.__SolveAlgorithmContainer.setLayout(solveAlgorithmLayout)
        layout.addWidget(self.__SolveAlgorithmContainer)

        # MazeTypeContainer with horizontal layout
        self.__mazeTypeContainer = QtWidgets.QGroupBox("Maze Type", self.__centralwidget)
        mazeTypeLayout = QtWidgets.QHBoxLayout()
        mazeTypeLayout.addStretch(1)
        self.__SquareRadioButton = QtWidgets.QRadioButton("Square", self.__mazeTypeContainer)
        mazeTypeLayout.addWidget(self.__SquareRadioButton)
        self.__HexagonalRadioButton = QtWidgets.QRadioButton("Hexagonal", self.__mazeTypeContainer)
        mazeTypeLayout.addWidget(self.__HexagonalRadioButton)
        self.__TriangularRadioButton = QtWidgets.QRadioButton("Triangular", self.__mazeTypeContainer)
        mazeTypeLayout.addWidget(self.__TriangularRadioButton)
        mazeTypeLayout.addStretch(1)
        self.__mazeTypeContainer.setLayout(mazeTypeLayout)
        layout.addWidget(self.__mazeTypeContainer)

        self.__widthLayout = QtWidgets.QVBoxLayout()  # Vertical layout for the width slider and label
        self.__mazeSizeSliderX = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.__centralwidget)
        self.__mazeSizeSliderX.setMinimum(5)
        self.__mazeSizeSliderX.setMaximum(100)
        self.__mazeSizeTextX = QtWidgets.QLabel("Maze Width: 5", self.__centralwidget)
        self.__widthLayout.addWidget(self.__mazeSizeTextX)

        self.__widthLayout.addWidget(self.__mazeSizeSliderX)
        layout.addLayout(self.__widthLayout)  # Add width layout to the main layout

        # Maze Height Slider and Label
        self.__heightLayout = QtWidgets.QVBoxLayout()  # Vertical layout for the height slider and label
        self.__mazeSizeSliderY = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.__centralwidget)
        self.__mazeSizeSliderY.setMinimum(5)
        self.__mazeSizeSliderY.setMaximum(100)
        self.__mazeSizeTextY = QtWidgets.QLabel("Maze Height: 5", self.__centralwidget)
        self.__heightLayout.addWidget(self.__mazeSizeTextY)

        self.__heightLayout.addWidget(self.__mazeSizeSliderY)
        layout.addLayout(self.__heightLayout)  # Add height layout to the main layout

        # GenerateMazeButton
        self.__GenerateMazeButton = QtWidgets.QPushButton("Generate", self.__centralwidget)
        self.__GenerateMazeButton.setObjectName("GenerateMazeButton")
        layout.addWidget(self.__GenerateMazeButton, 0, QtCore.Qt.AlignCenter)

        self.__centralwidget.setLayout(layout)
        self.__menubar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.__menubar)

        self.__menuHelp = QtWidgets.QMenu("Help", self)
        self.__menuExit = QtWidgets.QMenu("Exit", self)

        # Adding actions to the menus
        self.__actionAbout = QtWidgets.QAction("Help Documentation", self)
        self.__actionExit = QtWidgets.QAction("Exit", self)

        self.__menuHelp.addAction(self.__actionAbout)
        self.__menuExit.addAction(self.__actionExit)

        self.__menubar.addMenu(self.__menuHelp)
        self.__menubar.addMenu(self.__menuExit)

        # Connect actions to slots
        self.__actionAbout.triggered.connect(self.about_action_triggered)
        self.__actionExit.triggered.connect(self.exit_action_triggered)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        if self.__online:
            self.__BackButton.setVisible(False)
            self.__dialog = Ui_Dialog(f"Creating maze for play against {self.__LANInstance.getOpponentName()}", self.__desktopWidth, self.__desktopHeight)
        else:
            self.__BackButton.clicked.connect(self.BackButton_clicked)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.__TitleGenerateMaze.setText(_translate("GenerateMazeMenu", "Generate New Maze"))
        self.__GenerateMazeButton.setText(_translate("GenerateMazeMenu", "Generate"))
        self.__GenAlgorithmContainer.setTitle(_translate("GenerateMazeMenu", "Generation Algorithm"))
        self.__SidewinderRadioButton.setText(_translate("GenerateMazeMenu", "Sidewinder"))
        self.__BinaryTreeRadioButton.setText(_translate("GenerateMazeMenu", "Binary Tree"))
        self.__mazeSizeSliderX.setToolTip(_translate("GenerateMazeMenu", "Maze Width"))
        self.__mazeSizeTextX.setText(_translate("GenerateMazeMenu", "Maze Width: 5"))
        self.__mazeSizeSliderY.setToolTip(_translate("GenerateMazeMenu", "Maze Height"))
        self.__mazeSizeTextY.setText(_translate("GenerateMazeMenu", "Maze Height: 5"))
        self.__SolveAlgorithmContainer.setTitle(_translate("GenerateMazeMenu", "Solving Algorithm"))
        self.__DFSRadioButton.setText(_translate("GenerateMazeMenu", "Depth First Search"))
        self.__BFSRadioButton.setText(_translate("GenerateMazeMenu", "Breadth First Search"))
        self.__ManualRadioButton.setText(_translate("GenerateMazeMenu", "Manual Solve"))
        self.__mazeTypeContainer.setTitle(_translate("GenerateMazeMenu", "Maze Type"))
        self.__SquareRadioButton.setText(_translate("GenerateMazeMenu", "Square"))
        self.__HexagonalRadioButton.setText(_translate("GenerateMazeMenu", "Hexagonal"))
        self.__TriangularRadioButton.setText(_translate("GenerateMazeMenu", "Triangular"))
        self.__menuHelp.setTitle(_translate("GenerateMazeMenu", "Help"))
        self.__menuExit.setTitle(_translate("GenerateMazeMenu", "Exit"))
        self.__mazeSizeSliderX.valueChanged.connect(self.MazeSizeSliderX_valueChanged)
        self.__mazeSizeSliderY.valueChanged.connect(self.MazeSizeSliderY_valueChanged)
        self.__GenerateMazeButton.clicked.connect(self.GenerateMazeButton_clicked)

    def MazeSizeSliderX_valueChanged(self):
        self.__mazeSizeTextX.setText("Maze Width: " + str(self.__mazeSizeSliderX.value()))

    def MazeSizeSliderY_valueChanged(self):
        self.__mazeSizeTextY.setText("Maze Height: " + str(self.__mazeSizeSliderY.value()))

    def BackButton_clicked(self):
        self.hide()
        self.__BackWindow = Ui_MainMenu(self.__desktopWidth, self.__desktopHeight)
        self.__BackWindow.show()

    def about_action_triggered(self):
        self.__helpMenu = Ui_HelpMenu(self.__desktopWidth, self.__desktopHeight)
        self.__helpMenu.show()

    def exit_action_triggered(self):
        sys.exit()

    def GenerateMazeButton_clicked(self):
        if self.__SidewinderRadioButton.isChecked():
            self.__genAlgorithm = "sidewinder"
        elif self.__BinaryTreeRadioButton.isChecked():
            self.__genAlgorithm = "binary_tree"
        else:
            self.__genAlgorithm = None

        if self.__DFSRadioButton.isChecked():
            self.__solveAlgorithm =  "depth_first"
        elif self.__BFSRadioButton.isChecked():
            self.__solveAlgorithm = "breadth_first"
        elif self.__ManualRadioButton.isChecked():
            self.__solveAlgorithm = "manual"
        else:
            self.__solveAlgorithm = None

        if self.__SquareRadioButton.isChecked():
            self.__mazeType = 1
        elif self.__HexagonalRadioButton.isChecked():
            self.__mazeType = 2
        elif self.__TriangularRadioButton.isChecked():
            self.__mazeType = 3
        else:
            self.__mazeType = None
        if self.__genAlgorithm != None and self.__solveAlgorithm != None and self.__mazeType != None:
            
            self.hide()
            self.__ForwardWindow = Ui_MazeSolveWindow(self.__desktopWidth, self.__desktopHeight, self.__genAlgorithm, self.__solveAlgorithm, self.__mazeType, self.__mazeSizeSliderX.value(), self.__mazeSizeSliderY.value(), LANInstance=self.__LANInstance, online=self.__online)
            self.__ForwardWindow.show()
        else:
            self.__Dialog = QtWidgets.QDialog()
            self.__error = Ui_Dialog("Please select all options!", self.__desktopWidth, self.__desktopHeight)
            self.__error.show()

    def getMazeConfig(self):
        if self.__mazeConfig != None:
            return self.__mazeConfig
        else:
            return None

class Ui_Dialog(QDialog):
    def __init__(self, text, desktopWidth, desktopHeight):
        super(Ui_Dialog, self).__init__()
        self.__text = text
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.setWindowTitle("Popup")
        self.setupUi()
        with open("Main_Application/style.css", "r") as f:
            self.setStyleSheet(f.read())
    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(self.__desktopWidth * 0.2, self.__desktopHeight * 0.2)

        # Main vertical layout
        self.__verticalLayout = QtWidgets.QVBoxLayout(self)
        self.__verticalLayout.setObjectName("verticalLayout")

        # Spacer item for vertical alignment
        self.__verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.__verticalLayout.addItem(self.__verticalSpacer)

        # Label
        self.__label = QtWidgets.QLabel(self.__text, self)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.__label.setFont(font)
        self.__label.setAlignment(QtCore.Qt.AlignCenter)
        self.__label.setObjectName("label")
        self.__verticalLayout.addWidget(self.__label)

        # Spacer item for vertical alignment
        self.__verticalSpacer2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.__verticalLayout.addItem(self.__verticalSpacer2)

        # Button Box
        self.__buttonBox = QtWidgets.QDialogButtonBox(self)
        self.__buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.__buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.__buttonBox.setObjectName("buttonBox")
        self.__buttonBox.setLayoutDirection(QtCore.Qt.LeftToRight)  # Right-align the buttons
        self.__verticalLayout.addWidget(self.__buttonBox)
        self.__buttonBox.accepted.connect(self.accept)
        self.__buttonBox.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.retranslateUi()
        

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Dialog"))
        self.__label.setText(_translate("Dialog", self.__text))

class Ui_RequestToPlayDialog(QDialog):
    def __init__(self, text, desktopWidth, desktopHeight):
        super(Ui_RequestToPlayDialog, self).__init__()
        self.__text = text
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.__acceptGameState = None
        self.setWindowTitle("Popup")
        self.setupUi()
        with open("Main_Application/style.css", "r") as f:
            self.setStyleSheet(f.read())

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(self.__desktopWidth * 0.2, self.__desktopHeight * 0.2)

        # Main vertical layout
        self.__verticalLayout = QtWidgets.QVBoxLayout(self)
        self.__verticalLayout.setObjectName("verticalLayout")

        # Spacer item for vertical alignment
        self.__verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.__verticalLayout.addItem(self.__verticalSpacer)

        # Label
        self.__label = QtWidgets.QLabel(self.__text, self)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.__label.setFont(font)
        self.__label.setAlignment(QtCore.Qt.AlignCenter)
        self.__label.setObjectName("label")
        self.__verticalLayout.addWidget(self.__label)

        # Spacer item for vertical alignment
        self.__verticalSpacer2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.__verticalLayout.addItem(self.__verticalSpacer2)

        # Button Box
        self.__buttonBox = QtWidgets.QDialogButtonBox(self)
        self.__buttonBox.setOrientation(QtCore.Qt.Horizontal)
        # Create and add 'Accept' button
        self.__acceptButton = self.__buttonBox.addButton("Accept", QtWidgets.QDialogButtonBox.AcceptRole)
        self.__acceptButton.clicked.connect(self.acceptGame)  # Connect to the accept slot

        # Create and add 'Reject' button
        self.__rejectButton = self.__buttonBox.addButton("Reject", QtWidgets.QDialogButtonBox.RejectRole)
        self.__rejectButton.clicked.connect(self.rejectGame)  # Connect to the reject slot
        self.__buttonBox.setObjectName("buttonBox")
        self.__buttonBox.setLayoutDirection(QtCore.Qt.LeftToRight)  # Right-align the buttons
        self.__verticalLayout.addWidget(self.__buttonBox)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.retranslateUi()
        

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Dialog"))
        self.__label.setText(_translate("Dialog", self.__text))

    def acceptGame(self):
        self.__acceptGameState = True

    def rejectGame(self):
        self.__acceptGameState = False

    def getAcceptGame(self):
        return self.__acceptGameState
    
class Ui_OpponentWonDialog(QDialog):
    def __init__(self, text, desktopWidth, desktopHeight):
        super(Ui_OpponentWonDialog, self).__init__()
        self.__text = text
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.__continuePlayingState = None
        self.setWindowTitle("Popup")
        self.setupUi()
        with open("Main_Application/style.css", "r") as f:
            self.setStyleSheet(f.read())

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(self.__desktopWidth * 0.2, self.__desktopHeight * 0.2)

        # Main vertical layout
        self.__verticalLayout = QtWidgets.QVBoxLayout(self)
        self.__verticalLayout.setObjectName("verticalLayout")

        # Spacer item for vertical alignment
        self.__verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.__verticalLayout.addItem(self.__verticalSpacer)

        # Label
        self.__label = QtWidgets.QLabel(self.__text, self)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.__label.setFont(font)
        self.__label.setAlignment(QtCore.Qt.AlignCenter)
        self.__label.setObjectName("label")
        self.__verticalLayout.addWidget(self.__label)

        # Spacer item for vertical alignment
        self.__verticalSpacer2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.__verticalLayout.addItem(self.__verticalSpacer2)

        # Button Box
        self.__buttonBox = QtWidgets.QDialogButtonBox(self)
        self.__buttonBox.setOrientation(QtCore.Qt.Horizontal)
        # Create and add 'Accept' button
        self.__acceptButton = self.__buttonBox.addButton("Continue playing", QtWidgets.QDialogButtonBox.AcceptRole)
        self.__acceptButton.clicked.connect(self.continuePlaying)  # Connect to the accept slot

        # Create and add 'Reject' button
        self.__rejectButton = self.__buttonBox.addButton("Back to menu", QtWidgets.QDialogButtonBox.RejectRole)
        self.__rejectButton.clicked.connect(self.backToMenu)  # Connect to the reject slot
        self.__buttonBox.setObjectName("buttonBox")
        self.__buttonBox.setLayoutDirection(QtCore.Qt.LeftToRight)  # Right-align the buttons
        self.__verticalLayout.addWidget(self.__buttonBox)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.retranslateUi()
        

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Dialog"))
        self.__label.setText(_translate("Dialog", self.__text))

    def continuePlaying(self):
        self.__continuePlayingState = True

    def backToMenu(self):
        self.__mainMenu = Ui_MainMenu(self.__desktopWidth, self.__desktopHeight)
        self.__mainMenu.show()
        self.close()
        self.__continuePlayingState = False
    
    def getContinuePlayingState(self):
        return self.__continuePlayingState
    
class Ui_LANAndWebSockets(QtWidgets.QMainWindow):
    def __init__(self, desktopWidth, desktopHeight, username):
        super(Ui_LANAndWebSockets, self).__init__()
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.__username = username
        self.__playerButtonDict = {}
        self.__currentOpponentCellID = None
        self.__currentOpponent = None
        self.__opponentWon = False
        self.__opponentDisconnected = False
        self.__mazeReceived = False

        self.setWindowTitle("Play over LAN: CompSci Maze Master")
        self.setupUi(self.__desktopWidth, self.__desktopHeight)
        with open("Main_Application/style.css", "r") as f:
            self.setStyleSheet(f.read())

    def setupUi(self, desktopWidth, desktopHeight):
        self.resize(self.__desktopWidth * 0.6, self.__desktopHeight * 0.6)
        self.setObjectName("PlayOverLANMenu")
        self.__centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.__centralwidget)
        # Main layout
        mainLayout = QtWidgets.QVBoxLayout(self.__centralwidget)
        mainLayout.setAlignment(QtCore.Qt.AlignCenter)
        # Back Button
        self.__BackButton = QtWidgets.QPushButton("Back", self.__centralwidget)
        self.__BackButton.setGeometry(20, 20, 100, 40)  # Position in the top left corner
        self.__BackButton.setObjectName("BackButton")
        self.__BackButton.clicked.connect(self.BackButton_clicked)

        # Title Label
        self.__TitlePlayOverLAN = QtWidgets.QLabel("Available players", self.__centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setUnderline(True)
        self.__TitlePlayOverLAN.setFont(font)
        self.__TitlePlayOverLAN.setAlignment(QtCore.Qt.AlignCenter)
        mainLayout.addWidget(self.__TitlePlayOverLAN)

        # Players GroupBox
        self.__playersGroupBox = QtWidgets.QGroupBox("Players:", self.__centralwidget)
        playersLayout = QtWidgets.QVBoxLayout()
        self.__playersGroupBox.setLayout(playersLayout)

        # Set a fixed width for the playersGroupBox
        self.__playersGroupBox.setFixedWidth(self.width() * 0.8)

        mainLayout.addWidget(self.__playersGroupBox)
        
        self.__websocket = QWebSocket()
        self.__websocket.connected.connect(self.websocket_connected)
        self.__websocket.disconnected.connect(self.websocket_disconnected)
        self.__websocket.textMessageReceived.connect(self.websocket_message)
        self.__websocket.error.connect(self.websocket_error)
        self.connectToWebSocket()

    def connectToWebSocket(self):
        self.__websocket.open(QUrl("ws://192.168.68.102:8080"))

    def websocket_error(self, error):
        self.__errorDialog = Ui_Dialog("Error connecting to server! Try restarting the server.", self.__desktopWidth, self.__desktopHeight)
        self.__errorDialog.show()
        self.connectToWebSocket()

    def sendWebSocketMessage(self, message):
        self.__websocket.sendTextMessage(json.dumps(message))

    def websocket_connected(self):
        print("Connected to websocket")
        self.__logout = False
        self.__websocket.sendTextMessage(json.dumps({"type": "login", "user": self.__username}))
    
    def websocket_disconnected(self):
        if not(self.__logout):
            self.__errorDialog = Ui_Dialog("Disconnected from server! Try restarting the server.", self.__desktopWidth, self.__desktopHeight)
            self.__errorDialog.show()

    def websocket_message(self, message):
        try:
            message_data = json.loads(message)
            if message_data["type"] == "login":
                if message_data["success"]:
                    self.getAvailablePlayers(message_data["connectedUsers"])

            elif message_data["type"] == "logout":
                if message_data["success"]:
                    self.hide()
                    self.__BackWindow = Ui_MainMenu(self.__desktopWidth, self.__desktopHeight)
                    self.__BackWindow.show()
                else:
                    self.__errorDialog = Ui_Dialog("Error logging out!")
                    self.__errorDialog.show()
            elif message_data["type"] == "newUser":
                self.getAvailablePlayers(message_data["connectedUsers"])
            elif message_data["type"] == "playRequest":
                self.requestToPlayDialog = Ui_RequestToPlayDialog(f"{message_data['user']} wants to play with you!", self.__desktopWidth, self.__desktopHeight)
                self.requestToPlayDialog.show()

                self.check_accept_game_timer = QtCore.QTimer()
                self.check_accept_game_timer.timeout.connect(lambda: self.checkAcceptGame(message_data))
                self.check_accept_game_timer.start(1000)

            elif message_data["type"] == "confirmationAcceptRequest":
                    self.__currentOpponent = message_data["user"] 
                    self.hide()
                    self.__ForwardWindow = Ui_GenerateMazeMenu(self.__desktopWidth, self.__desktopHeight, self, online=True)
                    self.__ForwardWindow.show()

            elif message_data["type"] == "confirmationRejectRequest":
                try:
                    self.__errorDialog = Ui_Dialog("Game rejected!")
                    self.__errorDialog.show()
                except Exception as e:
                    print(e)
                    self.__errorDialog = Ui_Dialog("Error rejecting game! Try again.", self.__desktopWidth, self.__desktopHeight)
                    self.__errorDialog.show()
            elif message_data["type"] == "maze":
                self.hide()
                if not(self.__mazeReceived):
                    self.loadingDialog.hide()
                    self.__mazeReceived = True
                    print("Received maze")
                    message_data = message_data["maze"]
                    self.JSONgrid = dict(message_data['grid'])
                    self.__mazeType = message_data['maze_type']
                    if self.__mazeType == 1:
                        self.cellMaxConnections = 4
                    elif self.__mazeType == 2:
                        self.cellMaxConnections = 6
                    elif self.__mazeType == 3:
                        self.cellMaxConnections = 3
                    self.grid = dict()
                    
                    print(self.JSONgrid)
                    # Create the grid
                    for y in range(message_data['maze_height']):
                        self.grid[y] = []
                        for x in range(len(self.JSONgrid[str(y)])):
                            self.grid[y].append(Mazes.Cell(self.cellMaxConnections, (x, y)))

                    # Set the connections
                    for y in range(len(self.grid)):
                        for x in range(len(self.grid[y])):
                            for connection in self.JSONgrid[str(y)][x]['connections']:
                                connection = ast.literal_eval(connection)
                                self.grid[y][x].addConnection(self.grid[connection[1]][connection[0]])

                    self.__ForwardWindow = Ui_MazeSolveWindow(self.__desktopWidth, self.__desktopHeight, message_data["gen_algorithm"], message_data["solve_algorithm"], message_data["maze_type"], message_data["maze_width"], message_data["maze_height"], self.grid, self, online=True)
            elif message_data["type"] == "move":
                self.__currentOpponentCellID = message_data["move"]
            elif message_data["type"] == "win":
                
                self.__opponentWon = True
                
            elif message_data["type"] == "keepalive":
                self.sendWebSocketMessage({"type": "keepalive", "user": self.__username, "alive": True})
            elif message_data["type"] == "opponentDisconnected":
                self.__opponentDisconnected = True
                self.opponentDisconnectedDialog = Ui_Dialog("Opponent disconnected!", self.__desktopWidth, self.__desktopHeight)
                self.opponentDisconnectedDialog.show()

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    
    def sendCurrentCell(self, currentCellID):
        self.sendWebSocketMessage({"type": "sendMove", "user": self.__username, "opponent": self.__currentOpponent, "currentCell": currentCellID})

    def getOpponentMove(self):
        return self.__currentOpponentCellID

    def checkOpponentWin(self):
        return self.__opponentWon

    def checkOpponentDisconnected(self):
        return self.__opponentDisconnected
    
    def checkAcceptGame(self, message_data):
        if self.requestToPlayDialog.getAcceptGame() != None:
            if self.requestToPlayDialog.getAcceptGame():
                self.sendWebSocketMessage({"type": "acceptGame", "user": self.__username, "opponent": message_data["user"]})
                self.__currentOpponent = message_data["user"]
            else:
                self.sendWebSocketMessage({"type": "rejectGame", "user": self.__username, "opponent": message_data["user"]})
            self.requestToPlayDialog.close()
            self.check_accept_game_timer.stop()
            self.loadingDialog = Ui_Dialog("Waiting for opponent to create maze...", self.__desktopWidth, self.__desktopHeight)
            self.loadingDialog.show()

    def getAvailablePlayers(self, players):
        print(players)
        # Step 1: Clear existing buttons
        for button in self.__playerButtonDict.values():
            button.setParent(None)  # This will remove the button from the layout
            button.deleteLater()    # This will delete the button object

        self.__playerButtonDict.clear()  # Clear the dictionary

        # Step 2: Add new buttons
        for player in players:
            if player is None:
                continue

            self.__playerButtonFont = QtGui.QFont()
            self.__playerButtonFont.setPointSize(12)
            playerButton = QtWidgets.QPushButton(player, self.__centralwidget)
            playerButton.setObjectName(f"button_{player}")
            playerButton.clicked.connect(partial(self.playerButtonClicked, player))
            playerButton.setFont(self.__playerButtonFont)
            self.__playerButtonDict[player] = playerButton
            self.__playersGroupBox.layout().addWidget(playerButton)

    def logout(self):
        self.sendWebSocketMessage({"type": "logout", "user": self.__username})
        self.__logout = True
        self.__websocket.close()

    def BackButton_clicked(self):
        self.logout()
        self.hide()
        self.__BackWindow = Ui_MainMenu(self.__desktopWidth, self.__desktopHeight)
        self.__BackWindow.show()
        
    def playerButtonClicked(self, player):
        self.__currentOpponent = player
        self.sendWebSocketMessage({"type": "requestToPlay", "user": self.__username, "opponent": player})

    def getOpponentName(self):
        return self.__currentOpponent

    def getCurrentOpponentCellID(self):
        return self.__currentOpponentCellID

    def sendMaze(self, maze):
        self.sendWebSocketMessage({"type": "sendMaze", "user": self.__username, "opponent": self.__currentOpponent, "maze": maze})

    def sendWin(self):
        self.sendWebSocketMessage({"type": "win", "user": self.__username, "opponent": self.__currentOpponent})

    def resizeEvent(self, event):
        QtWidgets.QMainWindow.resizeEvent(self,event)
        # Adjust the back button position on resize
        self.__BackButton.move(20, 20)

class Ui_Login(QtWidgets.QDialog):
    def __init__(self, desktopWidth, desktopHeight):
        super(Ui_Login, self).__init__()
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.setupUi()
        with open("Main_Application/style.css", "r") as f:
            self.setStyleSheet(f.read())

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(self.__desktopWidth * 0.2, self.__desktopHeight * 0.2)

        # Main layout
        mainLayout = QtWidgets.QVBoxLayout(self)

        # Username layout
        self.__groupBox_2 = QtWidgets.QGroupBox("Enter Username:")
        groupBox_2_layout = QtWidgets.QHBoxLayout(self.__groupBox_2)
        self.__lineEdit = QtWidgets.QLineEdit()
        groupBox_2_layout.addWidget(self.__lineEdit)
        mainLayout.addWidget(self.__groupBox_2)

        # Button Box
        self.__buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.__buttonBox.accepted.connect(self.login)  # type: ignore
        self.__buttonBox.rejected.connect(self.backToMainMenu)  # type: ignore
        mainLayout.addWidget(self.__buttonBox)

        # Centering the layout
        mainLayout.setAlignment(QtCore.Qt.AlignCenter)

        self.setLayout(mainLayout)

        # Resize event
        self.resizeEvent = self.onResize

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)


    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Login"))
        self.__groupBox_2.setTitle(_translate("Dialog", "Enter Username:"))

    def onResize(self, event):
        # Adjust font size based on window size
        fontSize = max(8, min(self.width(), self.height()) // 50)
        font = QtGui.QFont("Arial", fontSize)
        self.__groupBox_2.setFont(font)
        self.__lineEdit.setFont(font)
    
    def login(self):
        self.__username = self.__lineEdit.text()

        self.__usernameRegex = '^[a-zA-Z0-9]+$'
        if re.match(self.__usernameRegex, self.__username):
            self.hide()
            self.__ForwardWindow = Ui_LANAndWebSockets(self.__desktopWidth, self.__desktopHeight, self.__username)
            self.__ForwardWindow.show()
        else:
            self.__errorDialog = Ui_Dialog("Please enter a valid username!")
            self.__errorDialog.show()

    def backToMainMenu(self):
        self.hide()
        self.__BackWindow = Ui_MainMenu(self.__desktopWidth, self.__desktopHeight)
        self.__BackWindow.show()


class Ui_HelpMenu(QMainWindow):
    def __init__(self, desktopWidth, desktopHeight):
        super(Ui_HelpMenu, self).__init__()
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.setupUi()
        with open("Main_Application/style.css", "r") as f:
            self.setStyleSheet(f.read())

    def setupUi(self):
        self.setObjectName("HelpMenu")
        self.resize(self.__desktopWidth * 0.6, self.__desktopHeight * 0.6)

        self.__centralwidget = QtWidgets.QWidget(self)
        self.__centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.__centralwidget)

        # Create a vertical layout
        self.__layout = QtWidgets.QVBoxLayout(self.__centralwidget)

        # Label
        self.__label = QtWidgets.QLabel("Help for CompSciMazeMaster", self.__centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.__label.setAlignment(QtCore.Qt.AlignCenter)  # Set label alignment to center

        self.__label.setFont(font)
        self.__label.setObjectName("label")
        self.__layout.addWidget(self.__label)

        # Scroll Area
        self.__helpArea = QtWidgets.QScrollArea(self.__centralwidget)
        self.__helpArea.setWidgetResizable(True)
        self.__helpArea.setObjectName("helpArea")

        self.__scrollAreaWidgetContents = QtWidgets.QWidget()
        self.__scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 789, 549))
        self.__scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        # Layout for scrollAreaWidgetContents
        self.__scrollLayout = QtWidgets.QVBoxLayout(self.__scrollAreaWidgetContents)
        self.__helpArea.setWidget(self.__scrollAreaWidgetContents)

        # Text Browser
        self.__textBrowser = QtWidgets.QTextBrowser(self.__scrollAreaWidgetContents)
        self.__textBrowser.setObjectName("textBrowser")
        self.__scrollLayout.addWidget(self.__textBrowser)

        # Adding helpArea to the main layout
        self.__layout.addWidget(self.__helpArea)

        self.__menubar = QtWidgets.QMenuBar(self)
        self.__menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.__menubar.setObjectName("menubar")
        self.setMenuBar(self.__menubar)

        self.__statusbar = QtWidgets.QStatusBar(self)
        self.__statusbar.setObjectName("statusbar")
        self.setStatusBar(self.__statusbar)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("HelpMenu", "HelpMenu"))
        self.__textBrowser.setHtml(_translate("HelpMenu",  "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<h2 style=\" margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Introduction</span></h2>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Welcome to the Maze Generator and Solver, an interactive platform designed to enhance your understanding of maze algorithms and graph traversal techniques in computer science. This guide will assist you in navigating and utilising the features of our application effectively.</span></p>\n"
"<h2 style=\" margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Features and How to Use</span></h2>\n"
"<h3 style=\" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Main Menu</span></h3>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:8pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Generate Maze</span>: Create a new maze with customizable settings.</li></ul>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Help: Access instructions, FAQs, and user tips.</li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Quit: Exit the application.</li></ul>\n"
"<h3 style=\" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Generating a Maze</span></h3>\n"
"<ol style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:16pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Select Maze Type</span><span style=\" font-size:8pt;\">: Choose from square, hexagonal, or triangular grid shapes.</span></li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Select Algorithm</span>: Pick an algorithm for maze generation like Sidewinder, Binary Tree, etc.</li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Customize Size</span>: Set the dimensions of the maze.</li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Generate</span>: Click on ‘Generate’ to create the maze based on your specifications.</li></ol>\n"
"<h3 style=\" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Solving a Maze</span></h3>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:16pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Select Solving Method</span><span style=\" font-size:8pt;\">: Choose between  algorithms (DFS, BFS, etc.) or manual solving.</span></li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Interact and Solve</span>: Use your mouse to navigate the maze to trace out the solving algorithm as it attempts to find a route from the top left cell to the bottom right.</li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">View Solution</span>: After solving, view your solving stats such as the optimal solution path and a heat map indicating the number of visits per cell.</li></ul>\n"
"<h2 style=\" margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Tips for Effective Learning</span></h2>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:16pt;\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Use the manual mode to deeply understand the maze-solving process</span></li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Utilise the program state you have access to, which tells you the current contents of the stack/queue along with neighbour information.</li></ul>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Experiment with different maze types and sizes to understand their complexities.</li></ul>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:600;\">Conclusion</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">The Maze Generator and Solver is a comprehensive tool designed to make learning computer science algorithms engaging and interactive. We hope this guide assists you in exploring and mastering the intricacies of maze algorithms and graph traversal techniques. Happy learning!</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\"><br /></span></p></body></html>"))  # Your HTML content
        self.__label.setText(_translate("HelpMenu", "Help for CompSciMazeMaster"))

    # Resize Event to adjust font size
    def resizeEvent(self, event):
        newFont = self.__label.font()
        newFont.setPointSize(max(8, int(self.width() / 80)))  # Adjust this ratio as needed
        self.__label.setFont(newFont)
        self.__textBrowser.setFont(newFont)
        super(Ui_HelpMenu, self).resizeEvent(event)

