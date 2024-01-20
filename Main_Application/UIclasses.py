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
from screeninfo import get_monitors
from PyQt5 import QtWidgets, QtCore, QtGui, QtWebSockets
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QWidget, QDialog, QGroupBox, QGridLayout, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import QTimer, QThread, QUrl
from PyQt5.QtWebSockets import QWebSocket
from functools import partial

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

    DESKTOP_WIDTH = get_monitors()[0].width
    DESKTOP_HEIGHT = get_monitors()[0].height

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
                    pg.draw.rect(self.__screen, self.HOVER_COLOUR, (self.__cell.getID()[0] * self.__cell_width, self.__cell.getID()[1] * self.__cell_height, self.__cell_width, self.__cell_height), self.__squareMazeThickness)
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
                    pg.draw.polygon(self.__screen, self.HOVER_COLOUR, p, self.__hexagonMazeThickness)
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
                    pg.draw.polygon(self.__screen, self.HOVER_COLOUR, p, self.__triangularMazeThickness)
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
                pg.draw.rect(self.__screen, self.HIGHLIGHT_COLOUR, (cell.getID()[0] * self.__cell_width, cell.getID()[1] * self.__cell_height, self.__cell_width, self.__cell_height), 0)
                # pg.draw.rect(self.__screen, self.HIGHLIGHT_COLOUR, (cell[0], cell[1], self.__cell_width+2, self.__cell_height+2))
                
            elif self.maze.getMazeType() == "hexagonal":
                self.__cell_x, self.__cell_y = cell.getID()
                self.__cell_x, self.__cell_y = (self.__cell_x * self.__cell_width) + self.__cell_width/2 + self.__offsetWidth, self.__cell_y * self.__cell_height  + self.__cell_height/2 + self.__offsetHeight
                if cell.getID()[1] % 2 == 1:
                    self.__cell_x += 0.5 * self.__cell_width
                self.drawHexagon(self.__cell_x, self.__cell_y, self.__cell_side_length, self.HIGHLIGHT_COLOUR, character=True, fill=True)
                # self.drawHexagon(cell[0], cell[1], self.__cell_side_length, self.HIGHLIGHT_COLOUR, character=True, fill=True)
            elif self.maze.getMazeType() == "triangular":
                self.__cell_x, self.__cell_y = cell.getID()
                self.__cell_x, self.__cell_y = (self.__cell_x * self.__cell_width) + self.__cell_width/2 , self.__cell_y * self.__cell_height  + self.__cell_height/2
                self.__cell_base_point_1, self.__cell_base_point_2 = self.get_triangle_base_points(cell.getID()[0], cell.getID()[1])
                self.__cell_flipped = self.getCellFlipped(cell)
                self.drawTriangle(self.__cell_base_point_1, self.__cell_base_point_2, self.__cell_side_length, self.__cell_flipped, self.HIGHLIGHT_COLOUR, fill=True, character=True)
                # self.drawTriangle(cell[0], cell[1], cell[2] , cell[3], self.HIGHLIGHT_COLOUR, character=True, fill=True)

    def drawHexagon(self, x, y, size, color=(0, 0, 0), width=0, character=False, fill=False):
        hexagon_points = []
        for i in range(6):
            angle_deg = 60 * i -30
            angle_rad = math.pi / 180 * angle_deg
            hexagon_points.append((x + size * math.cos(angle_rad), y + size * math.sin(angle_rad)))
        if fill:
            pg.draw.polygon(self.__screen, color, hexagon_points, 0)
        else:
            pg.draw.polygon(self.__screen, color, hexagon_points, self.__hexagonMazeThickness)
        if not character:
            self.__points.append(hexagon_points)



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

        pg.draw.line(self.__screen, self.WHITE, (self.__start_x, self.__start_y), (self.__end_x, self.__end_y), self.__hexagonMazeThickness)

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
            pg.draw.line(self.__screen, self.WHITE, line_start, line_end, self.__triangularMazeThickness)

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
        if not self.__show_hint:
            self.__hints_used += 1
        self.__show_hint = True
        if self.__hint_cell != None:
            self.highlightCell(self.__hint_cell, colour=self.HINT_COLOUR)
        else:
            self.dialog = Ui_Dialog("There are no hints available for this maze. Try solving it yourself!", self.DESKTOP_WIDTH, self.DESKTOP_HEIGHT)
            self.dialog.show()

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
        self.__optimalityScore =  self.__solutionLength / (self.__solutionLength + self.__incorrect_moves)
        self.__movesPerSecond = len(self.__cellTimes) / sum(self.__cellTimes) 
    
    def updateMovesPerSecond(self):
        self.__cellTimes.append(time.time() - self.__CellTime)
        self.__CellTime = time.time()

    def getPseudocodeText(self, solve_algorithm):
        return self.PSUEDOCODE[self.TITLE_DICT[solve_algorithm]]

    def getProgramStateText(self):
        self.__currentNeighbours, self.__currentStackQueue = self.maze.getProgramState(self.__current_cell)
        self.__currentNeighboursText = "Current neighbours: " + str(self.__currentNeighbours)
        if self.maze.getSolveAlgorithmName() == "depth_first":
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
            self.__token_visited_cells_coords.append(self.__current_cell)
            
            for y in range(self.maze.getMazeHeight()):
                for x in range(len(self.maze.getGrid()[y])):
                    cell = self.maze.getGrid()[y][x]
                    self.__curr_points = [(x * self.__cell_width, y * self.__cell_height), ((x+1) * self.__cell_width, y * self.__cell_height), ((x+1) * self.__cell_width, (y+1) * self.__cell_height), (x * self.__cell_width, (y+1) * self.__cell_height)]
                    self.__points.append(self.__curr_points)
                    if y == 0 or self.maze.getGrid()[y-1][x] not in cell.getConnections():
                        pg.draw.line(self.__screen, self.BLACK, (x *  self.__cell_width, y *  self.__cell_height), 
                                                    ((x+1) *  self.__cell_width, y *  self.__cell_height), self.__squareMazeThickness)
                    if x == 0 or not(str(self.maze.getGrid()[y][x-1]) in [str(i) for i in cell.getConnections()]):
                        pg.draw.line(self.__screen, self.BLACK, (x *  self.__cell_width, y *  self.__cell_height), 
                                                    (x *  self.__cell_width, (y+1) *  self.__cell_height), self.__squareMazeThickness)

        elif self.maze.getMazeType() == "hexagonal":
            self.__points = []
            self.__offsetWidth = self.__maze_width*0.025
            self.__offsetHeight = self.__maze_height*0.025
            self.__cell_width = ((self.__maze_width*0.8) / self.maze.getMazeWidth())
            self.__cell_side_length =  2*((self.__cell_width / 2) / math.tan(math.pi / 3))
            self.__cell_height = (self.__cell_side_length * 2) - (self.__cell_side_length / 2)
            self.__current_cell_x = self.__current_cell.getID()[0] * self.__cell_width + self.__cell_width/2 + self.__offsetWidth
            self.__current_cell_y = self.__current_cell.getID()[1] * self.__cell_height  + self.__cell_height/2 + self.__offsetHeight 

            if self.__current_cell.getID()[1] % 2 == 1:
                self.__current_cell_x += 0.5 * self.__cell_width

            self.__token_visited_cells_coords.append(self.__current_cell)

            if self.__show_hint:
                self.highlightCell(self.__hint_cell, colour=self.HINT_COLOUR)
            self.highlightVisitedCells()
             
            self.drawHexagon(self.__current_cell_x, self.__current_cell_y, self.__cell_side_length, self.CHARACTERCOLOUR, character=True, fill=True)
           
            for y in range(self.maze.getMazeHeight()):
                for x in range(len(self.maze.getGrid()[y])):
                    
                    cell = self.maze.getGrid()[y][x]
                    self.__curr_x =  (x * self.__cell_width) + (self.__cell_width/2)  + self.__offsetWidth
                    self.__curr_y = (y * (self.__cell_height)) + (self.__cell_height/2)  + self.__offsetHeight
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
            self.__token_visited_cells_coords.append(self.__current_cell)
            
            for y in range(self.maze.getMazeHeight()):
                for x in range(len(self.maze.getGrid()[y])):
                   
                    cell = self.maze.getGrid()[y][x]
                    self.__base_1, self.__base_2 = self.get_triangle_base_points(x, y)
                    self.__flipped = self.getCellFlipped(cell)
                    self.drawTriangle(self.__base_1, self.__base_2, self.__cell_side_length, self.__flipped)
                    self.__cell_connections = cell.getConnections()

                    for c in self.__cell_connections:
                         self.draw_triangle_connection(self.maze.getGrid()[y][x], c, self.__cell_side_length)

    def scale_thickness(self):
        self.__potentialSquareMazeThickness = list(range(1, 7))
        self.__potentialHexagonMazeThickness = list(range(1, 4))
        self.__potentialTriangularMazeThickness = list(range(1, 6))

        self.__squareMazeThickness = self.__potentialSquareMazeThickness[::-1][min(int(self.DESKTOP_WIDTH/ self.__width)-1, len(self.__potentialSquareMazeThickness)-1)]
        self.__hexagonMazeThickness = self.__potentialHexagonMazeThickness[::-1][min(int(self.DESKTOP_WIDTH/ self.__width)-1, len(self.__potentialHexagonMazeThickness)-1)]
        self.__triangularMazeThickness = self.__potentialTriangularMazeThickness[::-1][min(int(self.DESKTOP_WIDTH/ self.__width)-1, len(self.__potentialTriangularMazeThickness)-1)]


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

        self.__squareMazeThickness = 6
        self.__hexagonMazeThickness = 3
        self.__triangularMazeThickness = 5

        self.__time_taken = time.time()
        self.__CellTime = time.time()
        self.__cellTimes = []
        self.__screen = pg.display.set_mode((self.__width, self.__height), pg.RESIZABLE)
        pg.display.set_caption("CompSci Maze Master")

        self.__screen.fill(self.WHITE)
        self.__current_cell = self.maze.getGrid()[0][0]
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
                            self.__solve_step_return_value = self.maze.solve_step(self.cell_hover(clicked=True).getID(), self.__current_cell)
                            if self.__solve_step_return_value == "end":
                                self.__current_cell = self.maze.getGrid()[self.maze.getMazeHeight()-1][self.maze.getMazeWidth()-1]
                                self.displayMaze()
                                self.__running = False
                                return True
                            elif self.__solve_step_return_value == "invalid_move":
                                if self.UiType == "GUI":
                                    self.dialog = Ui_Dialog("Invalid move!", self.DESKTOP_WIDTH, self.DESKTOP_HEIGHT)
                                    self.dialog.show()
                                else:
                                    print("Invalid move!")
                            elif self.__solve_step_return_value == "wrong_move":
                                if self.UiType == "GUI":
                                    self.dialog = Ui_Dialog("Wrong move!", self.DESKTOP_WIDTH, self.DESKTOP_HEIGHT)
                                    self.dialog.show()
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
                        if self.UiType == "GUI":
                            self.dialog = Ui_Dialog("Please click inside the maze!", self.DESKTOP_WIDTH, self.DESKTOP_HEIGHT)
                            self.dialog.show()
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
                    
                    self.scale_thickness()

                        
            self.__screen.fill(self.WHITE)

    def quitPygame(self):
        self.generatePerformanceMetrics()
        self.__summary_stats = {
            
            "time_taken": time.time() - self.__time_taken,
            "hints_used": self.__hints_used,
            "incorrect_moves": self.__incorrect_moves,
            "gen_algorithm": self.TITLE_DICT[self.maze.getGenAlgorithmName()],
            "solve_algorithm": self.TITLE_DICT[self.maze.getSolveAlgorithmName()],
            "maze_type": self.maze.getMazeType().capitalize(),
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
    def __init__(self, desktopWidth, desktopHeight, genAlgorithm, solveAlgorithm, mazeType, mazeWidth, mazeHeight, mazeGrid=None, LANInstance=None, online=False):
        super(Ui_MazeSolveWindow, self).__init__()
        self.desktopWidth = desktopWidth
        self.desktopHeight = desktopHeight
        self.genAlgorithm = genAlgorithm
        self.solveAlgorithm = solveAlgorithm
        self.mazeType = mazeType
        self.UIinstance = UI()
        self.mazeWidth = mazeWidth
        self.mazeHeight = mazeHeight
        self.LANInstance = LANInstance
        self.mazeGrid = mazeGrid
        self.online = online
        self.setWindowTitle("CompSci Maze Master")
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

        self.menubar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.menuHelp = QtWidgets.QMenu("Help", self)
        self.menuExit = QtWidgets.QMenu("Exit", self)

        # Adding actions to the menus
        self.actionAbout = QtWidgets.QAction("Help Documentation", self)
        self.actionExit = QtWidgets.QAction("Exit", self)

        self.menuHelp.addAction(self.actionAbout)
        self.menuExit.addAction(self.actionExit)

        self.menubar.addMenu(self.menuHelp)
        self.menubar.addMenu(self.menuExit)

        # Connect actions to slots
        self.actionAbout.triggered.connect(self.about_action_triggered)
        self.actionExit.triggered.connect(self.exit_action_triggered)

    
        # Main Layout
        mainLayout = QtWidgets.QGridLayout(self.centralwidget)

        # Create GroupBoxes
        self.States = QGroupBox("Program State", self.centralwidget)
        self.actionsBox = QGroupBox("Actions", self.centralwidget)
        self.summaryBox = QGroupBox("Summary", self.centralwidget)
        self.pseudocodeBox = QGroupBox("Psuedocode", self.centralwidget)

    # Conditionally hide pseudocode and program state group boxes based on maze type
        if self.solveAlgorithm == "manual":
            self.States.setVisible(False)
            self.pseudocodeBox.setVisible(False)
            # Make the other two boxes take up the entire window
            mainLayout.addWidget(self.actionsBox, 0, 0, 1, 2)  # Span 2 columns
            mainLayout.addWidget(self.summaryBox, 1, 0, 1, 2)  # Span 2 columns
        else:
            # The regular layout if not 'manual'
            mainLayout.addWidget(self.States, 1, 0, 1, 1)
            mainLayout.addWidget(self.actionsBox, 0, 1, 1, 1)
            mainLayout.addWidget(self.summaryBox, 1, 1, 1, 1)
            mainLayout.addWidget(self.pseudocodeBox, 0, 0, 1, 1)
        
        # Buttons

        self.showDistanceMapButton = QPushButton("Show Distance Map", self.actionsBox)
        self.showSolutionButton = QPushButton("Show solution", self.actionsBox)
        self.quitButton = QPushButton("Quit", self.actionsBox)

        self.showDistanceMapButton.clicked.connect(lambda: self.showDistanceMap())
        self.showSolutionButton.clicked.connect(lambda: self.showSolution())
        self.quitButton.clicked.connect(lambda: self.quitSolving())

        # Add Buttons to layout
        actionLayout = QtWidgets.QVBoxLayout(self.actionsBox)
        actionLayout.addWidget(self.showDistanceMapButton)
        actionLayout.addWidget(self.showSolutionButton)
        actionLayout.addWidget(self.quitButton)

        # Labels
       
        self.timeTakenLabel = QLabel("Time: 0s", self.summaryBox)

        # Add Labels to layout
        summaryLayout = QtWidgets.QVBoxLayout(self.summaryBox)
        summaryLayout.addWidget(self.timeTakenLabel)
        



        self.hide_distance_map_timer = QTimer(self)
        self.hide_distance_map_timer.timeout.connect(lambda: self.getDistanceMapStatus())
        self.hide_distance_map_timer.start(500)

        self.get_time_taken_timer = QTimer(self)
        self.get_time_taken_timer.timeout.connect(lambda: self.getTimeTaken())
        self.get_time_taken_timer.start(1000)

        if self.solveAlgorithm != "manual":
            self.incorrectMovesLabel = QLabel("Incorrect Moves: 0", self.summaryBox)
            self.hintsUsedLabel = QLabel("Hints used: 0", self.summaryBox)

            summaryLayout.addWidget(self.incorrectMovesLabel)
            summaryLayout.addWidget(self.hintsUsedLabel)

            self.pseudocodeLabel = QLabel(self.getPseudocode(self.solveAlgorithm), self.pseudocodeBox)
            self.programStateLabel = QLabel("State", self.States)

            self.showHintButton = QPushButton("Show Hint", self.actionsBox)
            self.showHintButton.clicked.connect(lambda: self.showHint())

            self.update_program_state_timer = QTimer(self)
            self.update_program_state_timer.timeout.connect(lambda: self.getProgramState())
            self.update_program_state_timer.start(1000)

            self.incorrect_moves_timer = QTimer(self)
            self.incorrect_moves_timer.timeout.connect(lambda: self.updateIncorrectMoves())
            self.incorrect_moves_timer.start(500) 
                    # Add labels to state layout
            stateLayout = QtWidgets.QVBoxLayout(self.States)
            stateLayout.addWidget(self.programStateLabel)
        
            pseudoLayout = QtWidgets.QVBoxLayout(self.pseudocodeBox)
            pseudoLayout.addWidget(self.pseudocodeLabel)

            actionLayout.addWidget(self.showHintButton)


        self.resizeEvent = self.onResize

    def onResize(self, event):
        # Update font size based on window size
        base_font_size = max(self.width() / 80, 8)  # Adjust base font size
        font = QtGui.QFont()
        font.setPointSize(base_font_size)
        font.setUnderline(True)
        
        self.actionsBox.setFont(font)
        self.summaryBox.setFont(font)

        font.setPointSize(base_font_size * 0.6)  # Adjust for smaller font
        font.setUnderline(False)
        
        self.showDistanceMapButton.setFont(font)
        self.showSolutionButton.setFont(font)
        self.quitButton.setFont(font)
        self.timeTakenLabel.setFont(font)
       
        if self.solveAlgorithm != "manual":

            self.pseudocodeBox.setFont(font)
            self.States.setFont(font)
            self.showHintButton.setFont(font)
            self.incorrectMovesLabel.setFont(font)
            self.hintsUsedLabel.setFont(font)
            self.pseudocodeLabel.setFont(font)


        super(Ui_MazeSolveWindow, self).resizeEvent(event)

    def mazeToJSON(self, maze):
        mazeDict = {
            "maze_type": maze.getMazeType(),
            "maze_width": maze.getMazeWidth(),
            "maze_height": maze.getMazeHeight(),
            "gen_algorithm": maze.getGenAlgorithmName(),
            "solve_algorithm": maze.getSolveAlgorithmName(),
            "grid": []
        }

        for y in range(maze.getMazeHeight()):
            mazeDict["grid"].append([])
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
        return self.UIinstance.getPseudocodeText(algorithm)

    def getProgramState(self):
        self.__currentNeighboursText, self.__currentStackQueueText, self.__currentCellText = self.UIinstance.getProgramStateText()
        self.programStateLabel.setText(self.__currentCellText + "\n" + self.__currentNeighboursText + "\n" + self.__currentStackQueueText)

    def startPygameLoop(self):
        if self.mazeGrid != None:
            self.maze = Mazes.Maze(mazeType=self.mazeType, gen_algorithm=self.genAlgorithm, solve_algorithm=self.solveAlgorithm, mazeWidth=self.mazeWidth, mazeHeight=self.mazeHeight, mazeGrid=self.mazeGrid)
        else:
            self.maze = Mazes.Maze(mazeType=self.mazeType, gen_algorithm=self.genAlgorithm, solve_algorithm=self.solveAlgorithm, mazeWidth=self.mazeWidth, mazeHeight=self.mazeHeight)
        self.maze.generate()

        if self.online and self.mazeGrid == None:
            self.LANInstance.sendMaze(self.mazeToJSON(self.maze))

        self.UIinstance.initPygame(self.maze)

        self.pygame_timer = QTimer(self)
        self.pygame_timer.timeout.connect(lambda: self.updatePygame())
        self.pygame_timer.start(33)  # 30 fps

    def updatePygame(self):
        if self.UIinstance.updatePygame():
            self.pygame_timer.stop()
            self.hide_distance_map_timer.stop()
            self.get_time_taken_timer.stop()
            
            self.__summaryStats = self.UIinstance.quitPygame()

            if self.solveAlgorithm != "manual":
                self.update_program_state_timer.stop()
                self.incorrect_moves_timer.stop()
                
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
        if self.solveAlgorithm != "manual":
            self.incorrect_moves_timer.stop()
            self.update_program_state_timer.stop()

        self.pygame_timer.stop()
        self.hide_distance_map_timer.stop()
        self.get_time_taken_timer.stop()
        self.UIinstance.closeProgram()
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
        self.setWindowTitle("Summary: Maze Solved")
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
        self.optimalityScoreLabel = QLabel(f"Optimality Score: {(self.__summaryStats['optimality_score']*100):.2f}%", self.summaryGroupBox)
        self.movesPerSecondLabel = QLabel(f"Moves Per Second: {self.__summaryStats['moves_per_second']:.2f}", self.summaryGroupBox)
        self.solutionLengthLabel = QLabel(f"Optimal Solution Length: {self.__summaryStats['solution_length']}", self.summaryGroupBox)
        self.solutionShownLabel = QLabel(f"Solution Shown: {self.__summaryStats['solution_shown']}", self.summaryGroupBox)

        summaryLayout.addWidget(self.timeTakenLabel)
        summaryLayout.addWidget(self.optimalityScoreLabel)
        summaryLayout.addWidget(self.movesPerSecondLabel)
        summaryLayout.addWidget(self.solutionLengthLabel)
        summaryLayout.addWidget(self.solutionShownLabel)
        # Maze Solved GroupBox

        if self.__summaryStats['solve_algorithm'] != "Manual solve":
            self.hintsUsedLabel = QLabel(f"Hints Used: {self.__summaryStats['hints_used']}", self.summaryGroupBox)
            self.incorrectMovesLabel = QLabel(f"Incorrect Moves: {self.__summaryStats['incorrect_moves']}", self.summaryGroupBox)
            summaryLayout.addWidget(self.hintsUsedLabel)
            summaryLayout.addWidget(self.incorrectMovesLabel)

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
        self.optimalityScoreLabel.setFont(font)
        self.movesPerSecondLabel.setFont(font)
        self.solutionLengthLabel.setFont(font)
        self.solutionShownLabel.setFont(font)

        self.generationAlgorithmLabel.setFont(font)
        self.solvingAlgorithmLabel.setFont(font)
        self.mazeTypeLabel.setFont(font)
        self.mazeWidthLabel.setFont(font)
        self.mazeHeightLabel.setFont(font)
        self.returnToMenuButton.setFont(font)
        self.downloadMazeButton.setFont(font)

        if self.__summaryStats['solve_algorithm'] != "Manual solve":
            self.hintsUsedLabel.setFont(font)
            self.incorrectMovesLabel.setFont(font)

        super(Ui_DialogMazeSolved, self).resizeEvent(event)

    def returnToMenu(self):
        self.__UIinstance.closeProgram()
        self.hide()
        self.BackWindow = Ui_MainMenu(self.desktopWidth, self.desktopHeight)
        self.BackWindow.show()

    def downloadMaze(self):
        if not self.__UIinstance.downloadMaze():
            self.errorDialog = Ui_Dialog("Error downloading maze! Try again.")
            self.errorself.show()

class TerminalUI(UI):

    def __init__(self):
        pass    

    def run(self):
        self.__gen_algorithms = ["sidewinder", "binary_tree"]
        self.__solve_algorithms = ["depth_first", "breadth_first", "manual"]

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
        
        self.maze = Mazes.Maze(mazeType=int(mazeType), gen_algorithm=self.__gen_algorithms[int(genAlgorithm)-1], solve_algorithm=self.__solve_algorithms[int(solveAlgorithm)-1], mazeWidth=int(mazeWidth), mazeHeight=int(mazeHeight))

        self.maze.generate()
        self.initPygame(self.maze)
        self.UiType = "terminal"
        while True:
            if self.updatePygame():
                print("Congratulations! You solved the maze!")
                break




class GUI(UI):
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.screenWidth = self.app.desktop().screenGeometry().width()
        self.screenHeight = self.app.desktop().screenGeometry().height()
        self.UiType = "GUI"
        self.GUI = Ui_MainMenu(self.screenWidth, self.screenHeight)

    def run(self):
        self.GUI.show()
        self.app.exec_()

class Ui_MainMenu(QMainWindow):
    def __init__(self, desktopWidth, desktopHeight):
        super(Ui_MainMenu, self).__init__()
        self.desktopWidth = desktopWidth
        self.desktopHeight = desktopHeight
        self.setWindowTitle("Main Menu: CompSci Maze Master")
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

        # Play over LAN button
        self.PlayOverLANButton = QtWidgets.QPushButton("Play over LAN", self.centralwidget)
        self.PlayOverLANButton.setObjectName("PlayOverLANButton")
        self.PlayOverLANButton.setFont(buttonFont)
        self.PlayOverLANButton.setMinimumSize(250, 100)
        layout.addWidget(self.PlayOverLANButton, 0, QtCore.Qt.AlignCenter)


        # Set layout to central widget
        self.centralwidget.setLayout(layout)

        self.menubar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.menuHelp = QtWidgets.QMenu("Help", self)
        self.menuExit = QtWidgets.QMenu("Exit", self)

        # Adding actions to the menus
        self.actionAbout = QtWidgets.QAction("Help Documentation", self)
        self.actionExit = QtWidgets.QAction("Exit", self)
        self.actionAbout.triggered.connect(self.about_action_triggered)

        self.menuHelp.addAction(self.actionAbout)
        self.menuExit.addAction(self.actionExit)

        self.menubar.addMenu(self.menuHelp)
        self.menubar.addMenu(self.menuExit)

        # Connect actions to slots
        self.actionAbout.triggered.connect(self.about_action_triggered)
        self.actionExit.triggered.connect(self.exit_action_triggered)

        

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.TitleLabel.setText(_translate("MainMenu", "CompSci Maze Master"))
        self.StartButton.setText(_translate("MainMenu", "Generate New Maze"))
        self.menuHelp.setTitle(_translate("MainMenu", "Help"))
        self.menuExit.setTitle(_translate("MainMenu", "Exit"))
        self.StartButton.clicked.connect(self.StartButton_clicked)
        self.PlayOverLANButton.clicked.connect(self.PlayOverLANButton_clicked)

    def StartButton_clicked(self):
        self.hide()
        self.ForwardWindow = Ui_GenerateMazeMenu(self.desktopWidth, self.desktopHeight)
        self.ForwardWindow.show()

    def PlayOverLANButton_clicked(self):
        self.hide()
        self.ForwardWindow = Ui_Login(self.desktopWidth, self.desktopHeight)
        self.ForwardWindow.show()

    def about_action_triggered(self):
        self.__helpMenu = Ui_HelpMenu(self.desktopWidth, self.desktopHeight)
        self.__helpMenu.show()

    def exit_action_triggered(self):
        sys.exit()

class Ui_GenerateMazeMenu(QtWidgets.QMainWindow):
    def __init__(self, desktopWidth, desktopHeight, LANInstance=None, online=False):
        super(Ui_GenerateMazeMenu, self).__init__()
        self.desktopWidth = desktopWidth
        self.desktopHeight = desktopHeight
        self.LANInstance = LANInstance
        self.online = online
        self.setWindowTitle("Generate New Maze: CompSci Maze Master")
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
        self.setMenuBar(self.menubar)

        self.menuHelp = QtWidgets.QMenu("Help", self)
        self.menuExit = QtWidgets.QMenu("Exit", self)

        # Adding actions to the menus
        self.actionAbout = QtWidgets.QAction("Help Documentation", self)
        self.actionExit = QtWidgets.QAction("Exit", self)

        self.menuHelp.addAction(self.actionAbout)
        self.menuExit.addAction(self.actionExit)

        self.menubar.addMenu(self.menuHelp)
        self.menubar.addMenu(self.menuExit)

        # Connect actions to slots
        self.actionAbout.triggered.connect(self.about_action_triggered)
        self.actionExit.triggered.connect(self.exit_action_triggered)

        
        # Set layout to central widget
        self.centralwidget.setLayout(layout)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        if self.online:
            self.BackButton.setVisible(False)
            self.dialog = Ui_Dialog(f"Creating maze for play against {self.LANInstance.getOpponentName()}", self.desktopWidth, self.desktopHeight)
        else:
            self.BackButton.clicked.connect(self.BackButton_clicked)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
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

    def MazeSizeSliderX_valueChanged(self):
        self.MazeSizeTextX.setText("Maze Width: " + str(self.MazeSizeSliderX.value()))

    def MazeSizeSliderY_valueChanged(self):
        self.MazeSizeTextY.setText("Maze Height: " + str(self.MazeSizeSliderY.value()))

    def BackButton_clicked(self):
        self.hide()
        self.BackWindow = Ui_MainMenu(self.desktopWidth, self.desktopHeight)
        self.BackWindow.show()

    def about_action_triggered(self):
        self.__helpMenu = Ui_HelpMenu(self.desktopWidth, self.desktopHeight)
        self.__helpMenu.show()

    def exit_action_triggered(self):
        sys.exit()

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
            self.ForwardWindow = Ui_MazeSolveWindow(self.desktopWidth, self.desktopHeight, self.genAlgorithm, self.solveAlgorithm, self.mazeType, self.MazeSizeSliderX.value(), self.MazeSizeSliderY.value(), self.LANInstance, self.online)
            self.ForwardWindow.show()
        else:
            self.Dialog = QtWidgets.QDialog()
            self.error = Ui_Dialog("Please select all options!", self.desktopWidth, self.desktopHeight)
            self.error.show()


    def getMazeConfig(self):
        if self.mazeConfig != None:
            return self.mazeConfig
        else:
            return None

class Ui_Dialog(QDialog):
    def __init__(self, text, desktopWidth, desktopHeight):
        super(Ui_Dialog, self).__init__()
        self.text = text
        self.desktopWidth = desktopWidth
        self.desktopHeight = desktopHeight
        self.setWindowTitle("Popup")
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(self.desktopWidth * 0.2, self.desktopHeight * 0.2)

        # Main vertical layout
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        # Spacer item for vertical alignment
        self.verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer)

        # Label
        self.label = QtWidgets.QLabel(self.text, self)
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
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setLayoutDirection(QtCore.Qt.LeftToRight)  # Right-align the buttons
        self.verticalLayout.addWidget(self.buttonBox)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.retranslateUi()
        

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", self.text))

class Ui_RequestToPlayDialog(QDialog):
    def __init__(self, text, desktopWidth, desktopHeight):
        super(Ui_RequestToPlayDialog, self).__init__()
        self.text = text
        self.desktopWidth = desktopWidth
        self.desktopHeight = desktopHeight
        self.acceptGameState = None
        self.setWindowTitle("Popup")
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(self.desktopWidth * 0.2, self.desktopHeight * 0.2)

        # Main vertical layout
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        # Spacer item for vertical alignment
        self.verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer)

        # Label
        self.label = QtWidgets.QLabel(self.text, self)
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
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        # Create and add 'Accept' button
        self.acceptButton = self.buttonBox.addButton("Accept", QtWidgets.QDialogButtonBox.AcceptRole)
        self.acceptButton.clicked.connect(self.acceptGame)  # Connect to the accept slot

        # Create and add 'Reject' button
        self.rejectButton = self.buttonBox.addButton("Reject", QtWidgets.QDialogButtonBox.RejectRole)
        self.rejectButton.clicked.connect(self.rejectGame)  # Connect to the reject slot
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setLayoutDirection(QtCore.Qt.LeftToRight)  # Right-align the buttons
        self.verticalLayout.addWidget(self.buttonBox)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.retranslateUi()
        

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", self.text))

    def acceptGame(self):
        self.acceptGameState = True

    def rejectGame(self):
        self.acceptGameState = False

    def getAcceptGame(self):
        return self.acceptGameState
    

class Ui_LANAndWebSockets(QtWidgets.QMainWindow):
    def __init__(self, desktopWidth, desktopHeight, username, password):
        super(Ui_LANAndWebSockets, self).__init__()
        self.desktopWidth = desktopWidth
        self.desktopHeight = desktopHeight
        self.username = username
        self.password = password
        self.playerButtonDict = {}
        self.setWindowTitle("Play over LAN: CompSci Maze Master")
        self.setupUi(self.desktopWidth, self.desktopHeight)

    def setupUi(self, desktopWidth, desktopHeight):
        self.resize(desktopWidth * 0.6, desktopHeight * 0.6)
        self.setObjectName("PlayOverLANMenu")
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        # Main layout
        mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        mainLayout.setAlignment(QtCore.Qt.AlignCenter)
        # Back Button
        self.BackButton = QtWidgets.QPushButton("Back", self.centralwidget)
        self.BackButton.setGeometry(20, 20, 100, 40)  # Position in the top left corner
        self.BackButton.setObjectName("BackButton")
        self.BackButton.clicked.connect(self.BackButton_clicked)

        # Title Label
        self.TitlePlayOverLAN = QtWidgets.QLabel("Available players", self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setUnderline(True)
        self.TitlePlayOverLAN.setFont(font)
        self.TitlePlayOverLAN.setAlignment(QtCore.Qt.AlignCenter)
        mainLayout.addWidget(self.TitlePlayOverLAN)

        # Players GroupBox
        self.playersGroupBox = QtWidgets.QGroupBox("Players:", self.centralwidget)
        playersLayout = QtWidgets.QVBoxLayout()
        self.playersGroupBox.setLayout(playersLayout)

        # Set a fixed width for the playersGroupBox
        self.playersGroupBox.setFixedWidth(self.width() * 0.8)

        mainLayout.addWidget(self.playersGroupBox)
        
        self.websocket = QWebSocket()
        self.websocket.connected.connect(self.websocket_connected)
        self.websocket.disconnected.connect(self.websocket_disconnected)
        self.websocket.textMessageReceived.connect(self.websocket_message)
        self.websocket.error.connect(self.websocket_error)
        self.connectToWebSocket()

    def connectToWebSocket(self):
        self.websocket.open(QUrl("ws://192.168.68.102:8080"))

    def websocket_error(self, error):
        self.errorDialog = Ui_Dialog("Error connecting to server! Try restarting the server.", self.desktopWidth, self.desktopHeight)
        self.errorDialog.show()
        self.connectToWebSocket()

    def sendWebSocketMessage(self, message):
        self.websocket.sendTextMessage(json.dumps(message))

    def websocket_connected(self):
        print("Connected to websocket")
        self.websocket.sendTextMessage(json.dumps({"type": "login", "user": self.username}))
    
    def websocket_disconnected(self):
        self.errorDialog = Ui_Dialog("Disconnected from server! Try restarting the server.", self.desktopWidth, self.desktopHeight)
        self.errorDialog.show()
        self.connectToWebSocket()

    def websocket_message(self, message):
        try:
            message_data = json.loads(message)
            if message_data["type"] == "login":
                if message_data["success"]:
                    self.getAvailablePlayers(message_data["connectedUsers"])

            elif message_data["type"] == "logout":
                if message_data["success"]:
                    self.hide()
                    self.BackWindow = Ui_MainMenu(self.desktopWidth, self.desktopHeight)
                    self.BackWindow.show()
                else:
                    self.errorDialog = Ui_Dialog("Error logging out!")
                    self.errorDialog.show()
            elif message_data["type"] == "newUser":
                self.getAvailablePlayers(message_data["connectedUsers"])
            elif message_data["type"] == "playRequest":
                self.requestToPlayDialog = Ui_RequestToPlayDialog(f"{message_data['user']} wants to play with you!", self.desktopWidth, self.desktopHeight)
                self.requestToPlayDialog.show()
                while self.requestToPlayDialog.getAcceptGame() == None:
                    QtWidgets.QApplication.processEvents()
                
                if self.requestToPlayDialog.getAcceptGame():
                    self.sendWebSocketMessage({"type": "acceptGame", "user": self.username, "opponent": message_data["user"]})
                else:
                    self.sendWebSocketMessage({"type": "rejectGame", "user": self.username, "opponent": message_data["user"]})
                self.requestToPlayDialog.close()
            elif message_data["type"] == "confirmationAcceptRequest":
                #try:
                    self.hide()
                    self.ForwardWindow = Ui_GenerateMazeMenu(self.desktopWidth, self.desktopHeight, self, online=True)
                    self.ForwardWindow.show()
                # except Exception as e:
                #     print(e)
                #     self.errorDialog = Ui_Dialog("Error confirming game! Try again.", self.desktopWidth, self.desktopHeight)
                #     self.errorDialog.show()
            elif message_data["type"] == "confirmationRejectRequest":
                try:
                    self.errorDialog = Ui_Dialog("Game rejected!")
                    self.errorDialog.show()
                except Exception as e:
                    print(e)
                    self.errorDialog = Ui_Dialog("Error rejecting game! Try again.", self.desktopWidth, self.desktopHeight)
                    self.errorDialog.show()
            elif message_data["type"] == "maze":
                self.hide()
                message_data = message_data["maze"]
                self.ForwardWindow = Ui_MazeSolveWindow(self.desktopWidth, self.desktopHeight, message_data["gen_algorithm"], message_data["solve_algorithm"], message_data["maze_type"], message_data["maze_width"], message_data["maze_height"], message_data['grid'], self, online=True)
                self.ForwardWindow.show()


        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        
    def getAvailablePlayers(self, players):
        print(players)

        # Step 1: Clear existing buttons
        for button in self.playerButtonDict.values():
            button.setParent(None)  # This will remove the button from the layout
            button.deleteLater()    # This will delete the button object

        self.playerButtonDict.clear()  # Clear the dictionary

        # Step 2: Add new buttons
        for player in players:
            if player is None:
                continue

            self.playerButtonFont = QtGui.QFont()
            self.playerButtonFont.setPointSize(12)
            playerButton = QtWidgets.QPushButton(player, self.centralwidget)
            playerButton.setObjectName(f"button_{player}")
            playerButton.clicked.connect(partial(self.playerButtonClicked, player))
            playerButton.setFont(self.playerButtonFont)
            self.playerButtonDict[player] = playerButton
            self.playersGroupBox.layout().addWidget(playerButton)

    def BackButton_clicked(self):
        self.sendWebSocketMessage({"type": "logout", "user": self.username})
        
    def playerButtonClicked(self, player):
        self.opponent = player
        self.sendWebSocketMessage({"type": "requestToPlay", "user": self.username, "opponent": player})

    def getOpponentName(self):
        return self.opponent

    def sendMaze(self, maze):
        self.sendWebSocketMessage({"type": "sendMaze", "user": self.username, "opponent": self.opponent, "maze": maze})

    def resizeEvent(self, event):
        QtWidgets.QMainWindow.resizeEvent(self,event)
        # Adjust the back button position on resize
        self.BackButton.move(20, 20)

class Ui_Login(QtWidgets.QDialog):
    def __init__(self, desktopWidth, desktopHeight):
        super(Ui_Login, self).__init__()
        self.desktopWidth = desktopWidth
        self.desktopHeight = desktopHeight
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(self.desktopWidth * 0.2, self.desktopHeight * 0.2)

        # Main layout
        mainLayout = QtWidgets.QVBoxLayout(self)

        # GroupBox for Login
        self.groupBox = QtWidgets.QGroupBox("Login")
        groupBoxLayout = QtWidgets.QVBoxLayout(self.groupBox)

        # Username layout
        self.groupBox_2 = QtWidgets.QGroupBox("Enter Username:")
        groupBox_2_layout = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.lineEdit = QtWidgets.QLineEdit()
        groupBox_2_layout.addWidget(self.lineEdit)
        groupBoxLayout.addWidget(self.groupBox_2)

        # Password layout
        self.groupBox_3 = QtWidgets.QGroupBox("Enter Password:")
        groupBox_3_layout = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.lineEdit_2 = QtWidgets.QLineEdit()
        groupBox_3_layout.addWidget(self.lineEdit_2)
        groupBoxLayout.addWidget(self.groupBox_3)

        # Button Box
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.login)  # type: ignore
        self.buttonBox.rejected.connect(self.backToMainMenu)  # type: ignore
        groupBoxLayout.addWidget(self.buttonBox)

        # Add group box to the main layout
        mainLayout.addWidget(self.groupBox)

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
        self.groupBox.setTitle(_translate("Dialog", "Login"))
        self.groupBox_2.setTitle(_translate("Dialog", "Enter Username:"))
        self.groupBox_3.setTitle(_translate("Dialog", "Enter Password:"))    

    def onResize(self, event):
        # Adjust font size based on window size
        fontSize = max(8, min(self.width(), self.height()) // 50)
        font = QtGui.QFont("Arial", fontSize)
        self.groupBox.setFont(font)
        self.groupBox_2.setFont(font)
        self.groupBox_3.setFont(font)
        self.lineEdit.setFont(font)
        self.lineEdit_2.setFont(font)
    
    def login(self):
        self.username = self.lineEdit.text()
        self.password = self.lineEdit_2.text()

        self.usernameRegex = '^[a-zA-Z0-9]+$'
        if re.match(self.usernameRegex, self.username):
            self.hide()
            self.ForwardWindow = Ui_LANAndWebSockets(self.desktopWidth, self.desktopHeight, self.username, self.password)
            self.ForwardWindow.show()
        else:
            self.errorDialog = Ui_Dialog("Please enter a valid username!")
            self.errorDialog.show()

    def backToMainMenu(self):
        self.hide()
        self.BackWindow = Ui_MainMenu(self.desktopWidth, self.desktopHeight)
        self.BackWindow.show()


class Ui_HelpMenu(QMainWindow):
    def __init__(self, desktopWidth, desktopHeight):
        super(Ui_HelpMenu, self).__init__()
        self.desktopWidth = desktopWidth
        self.desktopHeight = desktopHeight
        self.setupUi()

    def setupUi(self):
        self.setObjectName("HelpMenu")
        self.resize(self.desktopWidth * 0.6, self.desktopHeight * 0.6)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)

        # Create a vertical layout
        self.layout = QtWidgets.QVBoxLayout(self.centralwidget)

        # Label
        self.label = QtWidgets.QLabel("Help for CompSciMazeMaster", self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label.setAlignment(QtCore.Qt.AlignCenter)  # Set label alignment to center

        self.label.setFont(font)
        self.label.setObjectName("label")
        self.layout.addWidget(self.label)

        # Scroll Area
        self.helpArea = QtWidgets.QScrollArea(self.centralwidget)
        self.helpArea.setWidgetResizable(True)
        self.helpArea.setObjectName("helpArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 789, 549))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        # Layout for scrollAreaWidgetContents
        self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.helpArea.setWidget(self.scrollAreaWidgetContents)

        # Text Browser
        self.textBrowser = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents)
        self.textBrowser.setObjectName("textBrowser")
        self.scrollLayout.addWidget(self.textBrowser)

        # Adding helpArea to the main layout
        self.layout.addWidget(self.helpArea)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("HelpMenu", "HelpMenu"))
        self.textBrowser.setHtml(_translate("HelpMenu",  "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<h2 style=\" margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Introduction</span></h2>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Welcome to the Maze Generator and Solver, an interactive platform designed to enhance your understanding of maze algorithms and graph traversal techniques in computer science. This guide will assist you in navigating and utilising the features of our application effectively.</span></p>\n"
"<h2 style=\" margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Features and How to Use</span></h2>\n"
"<h3 style=\" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Main Menu</span></h3>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:8pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Generate Maze</span>: Create a new maze with customizable settings.</li></ul>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Help</span>: Access instructions, FAQs, and user tips.</li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Quit</span>: Exit the application.</li></ul>\n"
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
        self.label.setText(_translate("HelpMenu", "Help for CompSciMazeMaster"))

    # Resize Event to adjust font size
    def resizeEvent(self, event):
        newFont = self.font()
        newFont.setPointSize(max(8, int(self.width() / 80)))  # Adjust this ratio as needed
        #self.label.setFont(newFont)
        self.textBrowser.setFont(newFont)
        super(Ui_HelpMenu, self).resizeEvent(event)

