#===================================================================================================================================
#=====================IMPORT MODULES================================================================================================
#===================================================================================================================================

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
    """
    The UI class is an abstract class that defines the methods and attributes that are common to all UI classes.
    It's responsible for drawing the maze on the screen and handling user input.
    It also contains methods for calculating and displaying performance metrics.
    """
#===================================================================================================================================
#===================== CONSTANTS ==================================================================================================
#===================================================================================================================================

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

#===================================================================================================================================
#=====================CELL METHODS==================================================================================================
#===================================================================================================================================

    def drawSquare(self, cell, width, height, color=(0, 0, 0), character=False, fill=False):
        """
        Draws a square on the screen with the specified position, size, and color.

            Args:
                cell (Cell): The cell to be drawn.
                width (int): The width of the square.
                height (int): The height of the square.
                color (Tuple[int, int, int], optional): The color of the square. Defaults to (0, 0, 0).
                character (bool, optional): Whether to add the square to the list of points. Defaults to False.
                fill (bool, optional): Whether to fill the square with color. Defaults to False.
            Returns:
                None
        """
        # Get the cells id and calculate the x and y coordinates
        x, y = cell.getID()
        x, y = x * width, y * height

        # Draw the square
        if fill:
            pg.draw.rect(self.__screen, color, (x, y, width, height), 0)
        else:
            pg.draw.rect(self.__screen, color, (x, y, width, height), self.__squareMazeThickness)
        
        # Add the square to the list of points if it is not a character (it's not a player)
        if not character:
            self.__points.append([(x, y), (x+width, y), (x+width, y+height), (x, y+height)])

    def drawTriangle(self, cell, size, color=(0, 0, 0), fill=False, character=False):
        """
        Draws a triangle on the screen with the specified position, size, and color.
        Also saves the triangle vertices to the list of points.

        Args:
            cell (Cell): The cell to be drawn.
            size (float): The size of the triangle.
            color (Tuple[int, int, int], optional): The color of the triangle. Defaults to (0, 0, 0).
            fill (bool, optional): Whether to fill the triangle with color. Defaults to False.
            character (bool, optional): Whether to add the triangle to the list of points. Defaults to False.

        Returns:
            None
        """
        # Get the base points of the triangle
        base_point_1, base_point_2 = self.get_triangle_base_points(cell)
        # Check if the cell is flipped
        flipped = self.getCellFlipped(cell)
        # Create a list to store the triangle points
        triangle_points = [base_point_1, base_point_2]
        # Calculate the height of the triangle
        height = math.sqrt((size**2) - ((size/2)**2))
        x = (base_point_1[0] + base_point_2[0])/2
        # Calculate the y-coordinate based on whether the cell is flipped or not
        if flipped:
            y = base_point_1[1] - height
        else:
            y = base_point_1[1] + height
        # Add the top point of the triangle to the list of points
        triangle_points.append((x, y))
        # Draw the triangle on the screen
        if fill:
            pg.draw.polygon(self.__screen, color, triangle_points, 0)
        else:
            pg.draw.polygon(self.__screen, color, triangle_points, self.__triangularMazeThickness)
        # Add the triangle to the list of points if it is not a character and not already in the list
        if not character and not (triangle_points in self.__points):
            self.__points.append(triangle_points)

    def drawHexagon(self, cell, size, color=(0, 0, 0), character=False, fill=False):
        """
        Draws a hexagon on the screen with the specified position, size, and color.

        Args:
            cell (Cell): The cell to be drawn.
            size (int): The size of the hexagon.
            color (Tuple[int, int, int], optional): The color of the hexagon. Defaults to (0, 0, 0).
            character (bool, optional): Whether to add the hexagon to the list of points. Defaults to False.
            fill (bool, optional): Whether to fill the hexagon with color. Defaults to False.

        Returns:
            None
        """
        # Get the x and y coordinates of the cell
        x, y = cell.getID()
        # Calculate the center coordinates of the hexagon
        x, y = (x * self.__cell_width) + self.__cell_width/2 + self.__offsetWidth, y * self.__cell_height  + self.__cell_height/2 + self.__offsetHeight
        # Adjust the x coordinate for odd rows
        if cell.getID()[1] % 2 == 1:
            x += 0.5 * self.__cell_width

        # Calculate the points of the hexagon
        hexagon_points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            hexagon_points.append((x + size * math.cos(angle_rad), y + size * math.sin(angle_rad)))

        # Draw the hexagon
        if fill:
            pg.draw.polygon(self.__screen, color, hexagon_points, 0)
        else:
            pg.draw.polygon(self.__screen, color, hexagon_points, self.__hexagonMazeThickness)

        # Add the hexagon points to the list if character is True (it's not a player)
        if not character:
            self.__points.append(hexagon_points)

    def draw_hexagon_connection(self, cell1, cell2, offsetWidth, offsetHeight):
        """
        Draws a connection between two hexagonal cells on the screen.

        Args:
            cell1: The first cell.
            cell2: The second cell.
            offsetWidth (int): The offset width.
            offsetHeight (int): The offset height.

        Returns:
            None
        """
        # Get the coordinates of cell1
        self.__cell1_x, self.__cell1_y = cell1.getID()
        # Calculate the x and y coordinates of cell1 on the screen
        self.__cell1_x, self.__cell1_y = (self.__cell1_x * self.__cell_width) + offsetWidth + (self.__cell_width/2) , self.__cell1_y * self.__cell_height  + self.__cell_height/2 + offsetHeight
        # Get the coordinates of cell2
        self.__cell2_x, self.__cell2_y = cell2.getID()
        # Calculate the x and y coordinates of cell2 on the screen
        self.__cell2_x, self.__cell2_y = (self.__cell2_x * self.__cell_width) + offsetWidth + (self.__cell_width/2) , self.__cell2_y * self.__cell_height  + self.__cell_height/2 + offsetHeight
        
        # Adjust the x coordinate of cell1 if it is in an odd row
        if cell1.getID()[1] % 2 == 1:
            self.__cell1_x += 0.5 * self.__cell_width
        # Adjust the x coordinate of cell2 if it is in an odd row
        if cell2.getID()[1] % 2 == 1:
            self.__cell2_x += 0.5 * self.__cell_width
        
        # Check if the cells are in the same row
        if int(self.__cell1_y) == int(self.__cell2_y):
            # Set the start and end x coordinates to be in the middle of the cells
            self.__start_x = min([self.__cell1_x, self.__cell2_x]) + self.__cell_width/2
            self.__end_x = self.__start_x
            # Set the start and end y coordinates to be at the top and bottom of the cells
            self.__start_y = self.__cell1_y - self.__cell_side_length/2 
            self.__end_y = self.__start_y + self.__cell_side_length 
        else:
            # Check if cell1 is above cell2
            if self.__cell1_y < self.__cell2_y:
                # Set the start and end x coordinates to be the x coordinate of cell2 and cell1, respectively
                self.__start_x = self.__cell2_x 
                self.__end_x = self.__cell1_x
                # Set the start and end y coordinates to be at the top and bottom of cell2 and cell1, respectively
                self.__start_y = self.__cell2_y - self.__cell_side_length
                self.__end_y = self.__cell1_y + self.__cell_side_length
            else:
                # Set the start and end x coordinates to be the x coordinate of cell1 and cell2, respectively
                self.__start_x = self.__cell1_x 
                self.__end_x = self.__cell2_x
                # Set the start and end y coordinates to be at the top and bottom of cell1 and cell2, respectively
                self.__start_y = self.__cell1_y - self.__cell_side_length
                self.__end_y = self.__cell2_y + self.__cell_side_length
        
        # Draw a line connecting the two cells on the screen
        pg.draw.line(self.__screen, self.__WHITE, (self.__start_x, self.__start_y), (self.__end_x, self.__end_y), self.__hexagonMazeThickness)

    def draw_triangle_connection(self, cell1, cell2):
        """
        Draws a line connecting two triangle cells on the screen.

        Args:
            cell1: The first cell.
            cell2: The second cell.

        Returns:
            None
        """

        # Check if there is a connection between cell1 and cell2
        if cell1.checkConnection(cell2):
            # Get the base points of the triangles for cell1 and cell2
            self.__cell1_base_point_1, self.__cell1_base_point_2 = self.get_triangle_base_points(cell1)
            self.__cell2_base_point_1, self.__cell2_base_point_2 = self.get_triangle_base_points(cell2)
            
            # Determine the line start and line end points based on the base points
            if list(map(int, self.__cell1_base_point_1)) == list(map(int, self.__cell2_base_point_1)):
                # If the base points are the same, use the first base point of cell1 and the second base point of cell1
                line_start = self.__cell1_base_point_1
                line_end = self.__cell1_base_point_2
            elif self.distance(self.__cell1_base_point_1[0], self.__cell1_base_point_1[1], self.__cell2_base_point_2[0], self.__cell2_base_point_2[1]) < self.distance(self.__cell1_base_point_2[0], self.__cell1_base_point_2[1], self.__cell2_base_point_1[0], self.__cell2_base_point_1[1]):
                # If the distance between the first base point of cell1 and the second base point of cell2 is less than the distance between the second base point of cell1 and the first base point of cell2, use the first base point of cell1 and the second base point of cell2
                line_start = self.__cell1_base_point_1
                line_end = self.__cell2_base_point_2
            else:
                # Otherwise, use the second base point of cell1 and the first base point of cell2
                line_start = self.__cell1_base_point_2
                line_end = self.__cell2_base_point_1
            
            # Draw a line on the screen connecting the line start and line end points
            pg.draw.line(self.__screen, self.__WHITE, line_start, line_end, self.__triangularMazeThickness)

    def getCellFromPointsIndex(self, index):
        """
        Returns the cell from the grid based on the given index in the points array.

        Args:
            index (int): The index of the cell in the points array.

        Returns:
            Cell: The cell corresponding to the given index.
        """

        # Initialize counter and flag variables
        counter = 0
        flag = False

        # Iterate through each row in the maze grid
        for y in range(self.__maze.getMazeHeight()):
            # Iterate through each column in the current row
            for x in range(len(self.__maze.getGrid()[y])):
                # Check if the counter matches the given index
                if counter == index:
                    # Get the cell from the maze grid
                    cell = self.__maze.getGrid()[y][x]
                    flag = True
                    break
                counter += 1
            if flag:
                break

        # Return the cell corresponding to the given index
        return cell
    
    def cell_hover(self, clicked=False):
        """
        Highlights the cell that the mouse is hovering over and returns the cell if clicked.

        Args:
            clicked (bool, optional): Indicates if the cell was clicked. Defaults to False.

        Returns:
            Cell: The cell that was hovered over if clicked, otherwise None.
        """

        # Get the current mouse position
        self.__mouse_pos_x, self.__mouse_pos_y = pg.mouse.get_pos()

        # Iterate through each point in the grid
        for p in self.__points:
            # Check if the mouse position is outside the maze area
            if self.__mouse_pos_x > self.__maze_width and self.__mouse_pos_y > self.__maze_height:
                break

            # Check if the mouse position is inside the current polygon
            if self.is_inside_polygon(self.__mouse_pos_x, self.__mouse_pos_y, p):
                # Get the index of the cell based on the point index
                self.__cell_x = self.__points.index(p)
                self.__cell = self.getCellFromPointsIndex(self.__cell_x)

                # Highlight the cell based on the maze type
                if self.__maze.getMazeType() == "square":
                    self.drawSquare(self.__cell, self.__cell_width, self.__cell_height, self.__HOVER_COLOUR, self.__squareMazeThickness)
                elif self.__maze.getMazeType() == "hexagonal":
                    pg.draw.polygon(self.__screen, self.__HOVER_COLOUR, p, self.__hexagonMazeThickness)
                elif self.__maze.getMazeType() == "triangular":
                    pg.draw.polygon(self.__screen, self.__HOVER_COLOUR, p, self.__triangularMazeThickness)

                # Set the mouse cursor to a broken X shape
                pg.mouse.set_cursor(*pg.cursors.broken_x)

                # Return the cell if clicked
                if clicked:
                    return self.__cell
                break

    def highlightVisitedCells(self):
        """
        Highlights the visited cells in the maze.

        This function iterates through the list of visited cells and highlights them based on the maze type.
        For square mazes, it calls the drawSquare() method to draw a square with the specified color, width, height, and fill.
        For hexagonal mazes, it calls the drawHexagon() method to draw a hexagon with the specified color, side length, and fill.
        For triangular mazes, it calls the drawTriangle() method to draw a triangle with the specified color, side length, and fill.

        Returns:
            None
        """
        for cell in self.__token_visited_cells_coords:
            if self.__maze.getMazeType() == "square":
                # Highlight the cell as a square
                self.drawSquare(cell, self.__cell_width, self.__cell_height, self.__HIGHLIGHT_COLOUR, character=True, fill=True)
            elif self.__maze.getMazeType() == "hexagonal":
                # Highlight the cell as a hexagon
                self.drawHexagon(cell, self.__cell_side_length, self.__HIGHLIGHT_COLOUR, character=True, fill=True)
            elif self.__maze.getMazeType() == "triangular":
                # Highlight the cell as a triangle
                self.drawTriangle(cell, self.__cell_side_length, self.__HIGHLIGHT_COLOUR, fill=True, character=True)

    def highlightCell(self, cell, colour=None):
        """
        Highlights the specified cell in the maze with the given colour.
        
        Args:
            cell (Cell): The cell object to be highlighted.
            colour (str, optional): The colour to be used for highlighting. 
                If not provided, the default highlight colour will be used.
        """
        if self.__maze.getMazeType() == "square":
            # If no colour is provided, use the default highlight colour
            if colour == None:
                colour = self.__HIGHLIGHT_COLOUR
            # Draw a square with the specified cell coordinates, width, height, colour, and fill
            self.drawSquare(cell, self.__cell_width, self.__cell_height, colour, character=True, fill=True)
        elif self.__maze.getMazeType() == "hexagonal":
            # Draw a hexagon with the specified cell coordinates, side length, colour, and fill
            self.drawHexagon(cell, self.__cell_side_length, colour, character=True, fill=True)
        elif self.__maze.getMazeType() == "triangular":
            # Draw a triangle with the specified cell coordinates, side length, colour, fill, and character
            self.drawTriangle(cell, self.__cell_side_length, colour, fill=True, character=True)

#===================================================================================================================================
#=====================MATH FUNCTIONS===============================================================================================
#===================================================================================================================================
            
    def is_inside_polygon(self, x, y, poly):
            """
            Checks if a point (x, y) is inside a polygon defined by a list of vertices using the ray casting algorithm.

            The ray casting algorithm works by drawing a horizontal ray from the point to the right and counting the number of times it intersects with the edges of the polygon. If the number of intersections is odd, the point is inside the polygon. If the number of intersections is even, the point is outside the polygon.

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

    def get_triangle_base_points(self, cell):
        """
        Get the base points of a triangle based on the given cell.

        Args:
            cell (Cell): The cell object.

        Returns:
            Tuple[List[float], List[float]]: The base points of the triangle.

        Comments:
        - The base points are calculated based on the cell's ID and dimensions.
        - If the cell is flipped, the y-coordinate of the base points is adjusted.

        """
        x, y = cell.getID()
        base_point_1 = [(x * self.__cell_width), (y * (self.__cell_height))]
        base_point_2 = [base_point_1[0] + self.__cell_side_length, (y * (self.__cell_height))]
        flipped = self.getCellFlipped(cell)
        if flipped:
            base_point_1[1] += self.__cell_height
            base_point_2[1] += self.__cell_height
        return base_point_1, base_point_2


    def distance(self, x1, y1, x2, y2):
        """
        Calculate the Euclidean distance between two points in a 2D plane.

        Parameters:
        x1 (float): The x-coordinate of the first point.
        y1 (float): The y-coordinate of the first point.
        x2 (float): The x-coordinate of the second point.
        y2 (float): The y-coordinate of the second point.

        Returns:
        float: The Euclidean distance between the two points.
        """
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def getCellFlipped(self, cell):
        """
        Determine if a cell is flipped based on its ID.

        Args:
            cell (Cell): The cell object.

        Returns:
            bool: True if the cell is flipped, False otherwise.

        Comments:
        - A cell is considered flipped if its x-coordinate is odd.
        - If the y-coordinate is odd, the flipped status is inverted.
        """
        x, y = cell.getID()
        flipped = False
        if x % 2 == 1:
            flipped = True
        if y % 2 == 1:
            flipped = not flipped
        return flipped

    def getDistanceColour(self, distance):
        """
        Calculates the RGB color based on the given distance.

        Args:
            distance (float): The distance value.

        Returns:
            tuple: The RGB color tuple.

        Raises:
            None

        This function is used when calculating the distance map. It takes a distance value and calculates the corresponding RGB color based on that distance. The color is determined by interpolating between green and orange for distances less than 0.5, and between orange and red for distances greater than or equal to 0.5.

        The RGB color tuple is returned as (r, g, b), where r, g, and b are integers representing the red, green, and blue components of the color respectively.
        """
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
    
#===================================================================================================================================
#=====================PERFORMANCE METRIC METHODS====================================================================================
#===================================================================================================================================
    def showHint(self):
        """
        Displays a hint for the current cell in the maze.

        Args:
            None

        Returns:
            None

        Raises:
            None

        This function retrieves a hint for the current cell in the maze and displays it on the UI. If a hint is available, the cell will be highlighted with a specific color. If no hint is available, a dialog box will be shown with a message indicating that there are no hints for the current maze.

        Note: This function updates the hint-related attributes of the UI class.

        """

        # Retrieve the hint for the current cell
        self.__hint_cell = self.__maze.getHint(self.__current_cell)

        # Increment the hint usage count if the hint is being shown for the first time
        if not self.__show_hint:
            self.__hints_used += 1

        # Set the flag to indicate that the hint is being shown
        self.__show_hint = True

        # Check if a hint cell is available
        if self.__hint_cell != None:
            # Highlight the hint cell with a specific color
            self.highlightCell(self.__hint_cell, colour=self.__HINT_COLOUR)
        else:
            # Show a dialog box indicating that no hints are available for the current maze
            self.__dialog = Ui_Dialog("There are no hints available for this maze. Try solving it yourself!", self.__DESKTOP_WIDTH, self.__DESKTOP_HEIGHT)
            self.__dialog.show()

    def showDistanceMap(self):
        """
        Displays the distance map on the UI.

        Args:
            None

        Returns:
            None

        Raises:
            None

        This function retrieves the distance map for the current cell in the maze and displays it on the UI. The distance map is a representation of the distances from the current cell to all other cells in the maze. The cells are highlighted with colors based on their normalized distance values.

        Note: This function updates the distance map-related attributes of the UI class.

        """

        # Retrieve the distance map for the current cell
        if self.__distanceMap == None:
            self.__distanceMap = self.__maze.getDistanceMap(self.__current_cell)

        # Set the flag to indicate that the distance map is being shown
        self.__show_distance_map = True

        # Calculate the dividing factor for normalizing the distance values
        self.__dividing_factor = max(self.__distanceMap.values())

        # Normalize the distance map values
        self.__normalised_distance_map = dict()
        for cell, distance in self.__distanceMap.items():
            self.__normalised_distance_map[cell] = distance / self.__dividing_factor

        # Highlight the cells on the UI based on their normalized distance values
        for cell, distance in self.__normalised_distance_map.items():
            self.highlightCell(self.__maze.getGrid()[cell[1]][cell[0]], colour=self.getDistanceColour(distance))
    def hideDistanceMap(self):
            """
            Hides the distance map on the UI.

            Args:
                None

            Returns:
                None

            Raises:
                None

            This function hides the distance map that is being displayed on the UI.

            """

            # Set the flag to indicate that the distance map is not being shown
            self.__show_distance_map = False

            # Reset the distance map attribute
            self.__distanceMap = None

    def showSolution(self):
        """
        Displays the solution on the UI by highlighting the cells in the solution path.

        Args:
            None

        Returns:
            None

        Raises:
            None

        This function retrieves the solution path from the maze object and highlights each cell in the solution path on the UI.

        """
        if self.__solution == None:
            self.__solution = self.__maze.getSolution()
        self.__show_solution = True
        for cell in self.__solution:
            self.highlightCell(cell, colour=self.__YELLOW)
        self.__solutionShown = True

    def hideSolution(self):
        """
        Hides the solution path on the UI.

        Args:
            None

        Returns:
            None

        This function hides the solution path that is being displayed on the UI.

        """
        # Set the flag to indicate that the solution path is not being shown
        self.__show_solution = False

        # Reset the solution attribute
        self.__solution = None

    def generatePerformanceMetrics(self):
        """
        Calculates and updates the performance metrics of the maze-solving algorithm.

        Args:
            None

        Returns:
            None

        Raises:
            None

        This function calculates the solution length, optimality score, and moves per second of the maze-solving algorithm.
        The solution length is the number of cells in the solution path.
        The optimality score is calculated as the ratio of the solution length to the sum of the solution length and the number of incorrect moves.
        The moves per second is calculated as the ratio of the number of cell times to the sum of the cell times.

        """
        # Calculate the solution length
        self.__solutionLength = len(self.__maze.getSolution())

        # Calculate the optimality score
        self.__optimalityScore = self.__solutionLength / (self.__solutionLength + self.__incorrect_moves)

        # Calculate the moves per second
        self.__movesPerSecond = len(self.__cellTimes) / sum(self.__cellTimes)

    def updateMovesPerSecond(self):
        """
        Updates the moves per second by calculating the time taken for each move.

        This method calculates the time taken for each move by subtracting the previous cell time from the current time.
        It then appends the calculated time to the list of cell times and updates the current cell time.

        Parameters:
        - self: The instance of the class.

        Returns:
        - None
        """
        # Calculate the time taken for each move
        self.__cellTimes.append(time.time() - self.__CellTime)
        # Update the current cell time
        self.__CellTime = time.time()

#===================================================================================================================================
#=====================PYGAME RENDERING==============================================================================================
#===================================================================================================================================
        
    def scale_thickness(self):
        """
        Scales the thickness of different maze types based on the desktop width.

        This method calculates and sets the thickness of square, hexagon, and triangular mazes based on the desktop width.
        The thickness is determined by the potential thickness values and the ratio of the desktop width to the maze width.

        Parameters:
        - self: The instance of the class.

        Returns:
        - None
        """

        # Define potential thickness values for different maze types
        self.__potentialSquareMazeThickness = list(range(1, 7))
        self.__potentialHexagonMazeThickness = list(range(1, 4))
        self.__potentialTriangularMazeThickness = list(range(1, 6))

        # Calculate and set the thickness of square mazes
        self.__squareMazeThickness = self.__potentialSquareMazeThickness[::-1][min(int(self.__DESKTOP_WIDTH/ self.__width)-1, len(self.__potentialSquareMazeThickness)-1)]

        # Calculate and set the thickness of hexagon mazes
        self.__hexagonMazeThickness = self.__potentialHexagonMazeThickness[::-1][min(int(self.__DESKTOP_WIDTH/ self.__width)-1, len(self.__potentialHexagonMazeThickness)-1)]

        # Calculate and set the thickness of triangular mazes
        self.__triangularMazeThickness = self.__potentialTriangularMazeThickness[::-1][min(int(self.__DESKTOP_WIDTH/ self.__width)-1, len(self.__potentialTriangularMazeThickness)-1)]

    def displayMaze(self):
        """
        Displays the maze on the screen based on the maze type.

        Args:
            self: The instance of the UI class.

        Returns:
            None
        """
        self.__screen.fill(self.__WHITE)

        # Show distance map if enabled
        if self.__show_distance_map:
            self.showDistanceMap()

        # Show solution if enabled
        if self.__show_solution:
            self.showSolution()

        # Display maze based on maze type
        if self.__maze.getMazeType() == "square":
            self.__points = []
            self.__cell_width = self.__maze_width / self.__maze.getMazeWidth()
            self.__cell_height = self.__maze_height / self.__maze.getMazeHeight()

            # Highlight visited cells
            self.highlightVisitedCells()

            # Highlight opponent's current cell if enabled
            if self.__display_opponent_move and self.__opponent_current_cell is not None:
                self.highlightCell(self.__opponent_current_cell, colour=self.__OPPONENTCOLOUR)

            # Highlight hint cell if enabled
            if self.__show_hint:
                self.highlightCell(self.__hint_cell, colour=self.__HINT_COLOUR)

            # Draw character's current cell
            self.drawSquare(self.__current_cell, self.__cell_width, self.__cell_height, self.__CHARACTERCOLOUR, fill=True, character=True)
            self.__token_visited_cells_coords.append(self.__current_cell)

            # Draw maze grid
            for y in range(self.__maze.getMazeHeight()):
                for x in range(len(self.__maze.getGrid()[y])):
                    cell = self.__maze.getGrid()[y][x]
                    self.__curr_points = [(x * self.__cell_width, y * self.__cell_height), ((x+1) * self.__cell_width, y * self.__cell_height), ((x+1) * self.__cell_width, (y+1) * self.__cell_height), (x * self.__cell_width, (y+1) * self.__cell_height)]
                    self.__points.append(self.__curr_points)

                    # Draw horizontal walls
                    if y == 0 or self.__maze.getGrid()[y-1][x] not in cell.getConnections():
                        pg.draw.line(self.__screen, self.__BLACK, (x *  self.__cell_width, y *  self.__cell_height), 
                                                    ((x+1) *  self.__cell_width, y *  self.__cell_height), self.__squareMazeThickness)

                    # Draw vertical walls
                    if x == 0 or not(str(self.__maze.getGrid()[y][x-1]) in [str(i) for i in cell.getConnections()]):
                        pg.draw.line(self.__screen, self.__BLACK, (x *  self.__cell_width, y *  self.__cell_height), 
                                                    (x *  self.__cell_width, (y+1) *  self.__cell_height), self.__squareMazeThickness)

        elif self.__maze.getMazeType() == "hexagonal":
            self.__points = []
            self.__offsetWidth = self.__maze_width*0.025
            self.__offsetHeight = self.__maze_height*0.025
            self.__cell_width = ((self.__maze_width*0.65) / self.__maze.getMazeWidth())
            self.__cell_side_length =  2*((self.__cell_width / 2) / math.tan(math.pi / 3))
            self.__cell_height = (self.__cell_side_length * 2) - (self.__cell_side_length / 2)
            self.__token_visited_cells_coords.append(self.__current_cell)

            # Highlight visited cells
            self.highlightVisitedCells()

            # Highlight opponent's current cell if enabled
            if self.__display_opponent_move and self.__opponent_current_cell is not None:
                self.highlightCell(self.__opponent_current_cell, colour=self.__OPPONENTCOLOUR)

            # Highlight hint cell if enabled
            if self.__show_hint:
                self.highlightCell(self.__hint_cell, colour=self.__HINT_COLOUR)

            # Draw character's current cell
            self.drawHexagon(self.__current_cell, self.__cell_side_length, self.__CHARACTERCOLOUR, character=True, fill=True)

            # Draw maze grid
            for y in range(self.__maze.getMazeHeight()):
                for x in range(len(self.__maze.getGrid()[y])):
                    cell = self.__maze.getGrid()[y][x]
                    self.__cell_connections = cell.getConnections()

                    # Draw hexagon outline
                    self.drawHexagon(cell, self.__cell_side_length, color=self.__BLACK, fill=False)

                    # Draw connections between hexagons
                    for c in self.__cell_connections:
                        self.draw_hexagon_connection(cell, c, self.__offsetWidth, self.__offsetHeight)

        elif self.__maze.getMazeType() == "triangular":
            self.__points = []
            self.__cell_height = ((self.__maze_height*0.95) / (self.__maze.getMazeHeight()))
            self.__cell_side_length = self.__cell_height / math.sin(math.pi/3)
            self.__cell_width = self.__cell_side_length / 2

            # Highlight visited cells
            self.highlightVisitedCells()

            # Highlight opponent's current cell if enabled
            if self.__display_opponent_move and self.__opponent_current_cell is not None:
                self.highlightCell(self.__opponent_current_cell, colour=self.__OPPONENTCOLOUR)

            # Highlight hint cell if enabled
            if self.__show_hint:
                self.highlightCell(self.__hint_cell, colour=self.__HINT_COLOUR)

            # Draw character's current cell
            self.drawTriangle(self.__current_cell, self.__cell_side_length, self.__CHARACTERCOLOUR, fill=True, character=True)
            self.__token_visited_cells_coords.append(self.__current_cell)

            # Draw maze grid
            for y in range(self.__maze.getMazeHeight()):
                for x in range(len(self.__maze.getGrid()[y])):
                    cell = self.__maze.getGrid()[y][x]

                    # Draw triangle
                    self.drawTriangle(cell, self.__cell_side_length, self.__BLACK)

                    self.__cell_connections = cell.getConnections()

                    # Draw connections between triangles
                    for c in self.__cell_connections:
                         self.draw_triangle_connection(cell, c)
    
    def initPygame(self, maze=None, gui=False):
        """
        Initializes the Pygame library and sets up the game window.

        Parameters:
        - maze (optional): The maze object to be used in the game.
        - gui (optional): Boolean value indicating whether the game is in GUI mode or not.
        """
        pg.init()  # Initialize Pygame library

        if gui:
            self.__UiType = "GUI"  # Set the UI type to GUI

        self.__maze = maze  # Set the maze object
        self.__infoObject = pg.display.Info()  # Get information about the display
        self.__width, self.__height = self.__DESKTOP_WIDTH*0.7, self.__DESKTOP_HEIGHT*0.7  # Set the width and height of the game window

        self.__show_distance_map = False  # Flag to indicate whether to show the distance map
        self.__maze_width, self.__maze_height = self.__width, self.__height  # Set the width and height of the maze

        self.__display_opponent_move = True  # Flag to indicate whether to display opponent's move

        self.__opponent_current_cell = None  # Variable to store opponent's current cell
        self.__addedPoints = False  # Flag to indicate whether points have been added
        self.__incorrect_moves = 0  # Counter for incorrect moves
        self.__show_hint = False  # Flag to indicate whether to show a hint
        self.__hints_used = 0  # Counter for hints used
        self.__distanceMap = None  # Variable to store the distance map
        self.__solution = None  # Variable to store the solution path
        self.__show_solution = False  # Flag to indicate whether to show the solution
        self.__solutionShown = False  # Flag to indicate whether the solution has been shown
        self.__points = []  # List to store points

        self.__squareMazeThickness = 6  # Thickness of square maze walls
        self.__hexagonMazeThickness = 3  # Thickness of hexagon maze walls
        self.__triangularMazeThickness = 5  # Thickness of triangular maze walls

        self.__time_taken = time.time()  # Variable to store the current time
        self.__CellTime = time.time()  # Variable to store the time for each cell
        self.__cellTimes = []  # List to store the time for each cell
        self.__screen = pg.display.set_mode((self.__width, self.__height), pg.RESIZABLE)  # Create the game window
        pg.display.set_caption("CompSci Maze Master")  # Set the window caption

        self.__screen.fill(self.__WHITE)  # Fill the window with white color
        self.__current_cell = self.__maze.getGrid()[0][0]  # Set the current cell to the top-left cell of the maze
        self.__token_visited_cells_coords = []  # List to store the coordinates of visited cells
        self.__running = True  # Flag to indicate whether the game is running or not

    def updatePygame(self):
        """
        Updates the Pygame display and handles user input events.

        Returns:
        - True if the game is completed, False otherwise.
        """
        if self.__running:
            self.displayMaze()  # Display the maze
            self.cell_hover()  # Highlight the hovered cell
            pg.display.flip()  # Update the display

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.__running = False  # Quit the game if the window is closed
                elif event.type == pg.MOUSEBUTTONDOWN:
                    x, y = pg.mouse.get_pos()
                    if x < self.__maze_width:
                        self.__clicked_cell = self.cell_hover(clicked=True)  # Get the clicked cell
                        if self.__clicked_cell != None:
                            self.__solve_step_return_value = self.__maze.solve_step(self.cell_hover(clicked=True).getID(), self.__current_cell)
                            if self.__solve_step_return_value == "end":
                                self.__current_cell = self.__maze.getGrid()[self.__maze.getMazeHeight()-1][self.__maze.getMazeWidth()-1]
                                self.displayMaze()
                                self.__running = False
                                return True  # Return True to indicate game completion
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
                            self.updateMovesPerSecond()  # Update moves per second counter
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
                    self.scale_thickness()  # Scale the thickness of maze walls based on the new window size

            self.__screen.fill(self.__WHITE)  # Fill the window with white color

    def quitPygame(self):
        """
        Quits the Pygame application and generates performance metrics.

        Returns:
            dict: A dictionary containing the summary statistics of the application.
        """
        # Generate performance metrics
        self.generatePerformanceMetrics()

        # Create a dictionary of summary statistics
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
        
#===================================================================================================================================
#=====================UTILITY METHODS===============================================================================================
#===================================================================================================================================

    def downloadMaze(self):
        """
        Saves a screenshot of the maze as a PNG file.

        Returns:
            bool: True if the screenshot is successfully saved, False otherwise.
        """
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
        
    def updateOpponentMove(self, cellID):
        """
        Updates the opponent's current cell based on the given cell ID.

        Args:
            cellID (tuple): The ID of the cell in the maze grid.

        Returns:
            None
        """
        # Get the maze grid
        maze_grid = self.__maze.getGrid()

        # Update the opponent's current cell
        self.__opponent_current_cell = maze_grid[cellID[1]][cellID[0]]
    def updateOpponentMove(self, cellID):
        self.__opponent_current_cell = self.__maze.getGrid()[cellID[1]][cellID[0]]

#===================================================================================================================================
#=====================GETTERS AND ADMIN=============================================================================================
#===================================================================================================================================

    def getHintsUsed(self):
        """
        Get the number of hints used.

        Returns:
            int: The number of hints used.
        """
        return self.__hints_used
    
    def getDistanceMapStatus(self):
        """
        Get the status of the distance map display.

        Returns:
            bool: True if the distance map is being shown, False otherwise.
        """
        return self.__show_distance_map
    
    def getIncorrectMoves(self):
        """
        Get the number of incorrect moves made.

        Returns:
            int: The number of incorrect moves made.
        """
        return self.__incorrect_moves
    
    def getTimeTaken(self):
        """
        Get the time taken to solve the maze.

        Returns:
            float: The time taken in seconds.
        """
        return time.time() - self.__time_taken
    
    def getPseudocodeText(self, solve_algorithm):
        """
        Get the pseudocode text for the specified solve algorithm.

        Args:
            solve_algorithm (str): The solve algorithm name.

        Returns:
            str: The pseudocode text.
        """
        return self.__PSUEDOCODE[self.__TITLE_DICT[solve_algorithm]]

    def getProgramStateText(self):
        """
        Get the program state text.

        This method retrieves the current neighbors, stack/queue, and cell ID of the maze solver.
        The program state text includes information about the current neighbors, stack/queue, and cell ID.

        Returns:
            tuple: A tuple containing the program state text for the current neighbors, stack/queue, and cell ID.
        """
        self.__currentNeighbours, self.__currentStackQueue = self.__maze.getProgramState(self.__current_cell)
        self.__currentNeighboursText = "Current neighbours: " + str(self.__currentNeighbours)
        if self.__maze.getSolveAlgorithmName() == "depth_first":
            self.__currentStackQueueText = "Current stack: " + str(self.__currentStackQueue)
        else:
            self.__currentStackQueueText = "Current queue: " + str(self.__currentStackQueue)
        self.__currentCellText = "Current cell: " + str(self.__current_cell.getID())
        return self.__currentNeighboursText, self.__currentStackQueueText, self.__currentCellText

    def getCurrentCell(self):
        """
        Get the current cell.

        Returns:
            Cell: The current cell object.
        """
        return self.__current_cell    

    def closeProgram(self):
        """
        Close the program.

        This function quits the Pygame loop and terminates the program.
        """
        pg.quit()


#===================================================================================================================================
#=====================GUI CLASSES===================================================================================================
#===================================================================================================================================
        
class Ui_MazeSolveWindow(QMainWindow):
    def __init__(self, desktopWidth, desktopHeight, genAlgorithm, solveAlgorithm, mazeType, mazeWidth, mazeHeight, mazeGrid=None, LANInstance=None, online=False):
        """
        Initialize the MazeSolveWindow.

        Args:
            desktopWidth (int): The width of the desktop.
            desktopHeight (int): The height of the desktop.
            genAlgorithm (str): The generation algorithm name.
            solveAlgorithm (str): The solve algorithm name.
            mazeType (str): The type of maze.
            mazeWidth (int): The width of the maze.
            mazeHeight (int): The height of the maze.
            mazeGrid (optional): The maze grid.
            LANInstance (optional): The LAN instance.
            online (bool): Flag indicating if the program is running online.
        """
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
        with open("style.css", "r") as f:
            self.setStyleSheet(f.read())
        self.startPygameLoop()
        self.show()

    def setupUi(self):
        """
        Set up the user interface.
        """
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
        """
        Handle the resize event of the window.

        Args:
            event: The resize event.
        """
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

#===================================================================================================================================
#=====================ONLINE FUNCTIONALITY==========================================================================================
#===================================================================================================================================
    def mazeToJSON(self, maze):
        """
        Convert a Maze object to a JSON representation.

        Args:
            maze (Maze): The Maze object to convert.

        Returns:
            dict: A dictionary representing the Maze object in JSON format.
        """
        self.__mazeType = maze.getMazeType()

        # Convert maze type to numeric representation
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

        # Convert each cell in the maze to a dictionary representation
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
    
    def updateOpponent(self):
        """
        Updates the opponent's current cell and sends it to the LAN instance.
        """
        self.__currentCellID = self.__UIinstance.getCurrentCell().getID()
        self.__LANInstance.sendCurrentCell(self.__currentCellID)


    def checkOpponentWin(self):
        """
        Checks if the opponent has won the game and handles the appropriate actions.
        """
        if self.__LANInstance.checkOpponentWin():
            self.__opponentWon = True
            self.__opponentWonDialog = Ui_OpponentWonDialog("Your opponent has won!", self.__desktopWidth, self.__desktopHeight)
            self.__opponentWonDialog.show()
            while self.__opponentWonDialog.getContinuePlayingState() == None:
                QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 1000)
            if self.__opponentWonDialog.getContinuePlayingState():
                self.__opponentWonDialog.close()
            else:
                self.__opponentWonDialog.close()
                self.quitSolving()    
            
    def checkOpponentDisconnected(self):
        """
        Checks if the opponent has disconnected from the game and handles the appropriate actions.

        Returns:
            None
        """
        if self.__LANInstance.checkOpponentDisconnected():
            # If the opponent has disconnected, send a win signal to the LAN instance
            self.__LANInstance.sendWin()
            # Set the opponentWon flag to True
            self.__opponentWon = True

    #===================================================================================================================================
    #=====================PERFORMANCE METRIC METHODS====================================================================================
    #===================================================================================================================================

    def showHint(self):
        """
        Displays a hint to the user and updates the hints used label.

        Returns:
            None
        """
        # Display a hint using the UI instance
        self.__UIinstance.showHint()
        # Update the hints used label with the current number of hints used
        self.__hintsUsedLabel.setText("Hints used: " + str(self.__UIinstance.getHintsUsed()))
    
    def showDistanceMap(self):
        """
        Shows or hides the distance map based on the current state of the show distance map button.

        Returns:
            None
        """
        # Check the current text of the show distance map button
        if self.__showDistanceMapButton.text() == "Show Distance Map":
            # If the button text is "Show Distance Map", update it to "Hide Distance Map"
            self.__showDistanceMapButton.setText("Hide Distance Map")
            # Show the distance map using the UI instance
            self.__UIinstance.showDistanceMap()
        else:
            # If the button text is not "Show Distance Map", update it to "Show Distance Map"
            self.__showDistanceMapButton.setText("Show Distance Map")
            # Hide the distance map using the UI instance
            self.__UIinstance.hideDistanceMap()

    def updateIncorrectMoves(self):
        """
        Updates the label displaying the number of incorrect moves made by the user.

        Returns:
            None
        """
        self.__incorrectMovesLabel.setText("Incorrect Moves: " + str(self.__UIinstance.getIncorrectMoves()))

    def showSolution(self):
        """
        Shows or hides the solution based on the current state of the show solution button.

        Returns:
            None
        """
        if self.__showSolutionButton.text() == "Show solution":
            # If the button text is "Show solution", update it to "Hide solution"
            self.__showSolutionButton.setText("Hide solution")
            # Show the solution using the UI instance
            self.__UIinstance.showSolution()
        else:
            # If the button text is not "Show solution", update it to "Show solution"
            self.__showSolutionButton.setText("Show solution")
            # Hide the solution using the UI instance
            self.__UIinstance.hideSolution()

#===================================================================================================================================
#=====================PYGAME LOOP===================================================================================================
#===================================================================================================================================

    def startPygameLoop(self):
        """
        Starts the pygame loop and initializes timers for various tasks.

        This function generates a maze, initializes the pygame GUI, and starts timers for updating the opponent's move,
        checking opponent's win, and checking opponent's disconnection if the game is being played online.

        Parameters:
        - None

        Returns:
        - None
        """

        # Generate maze
        if self.__mazeGrid != None:
            self.__maze = Mazes.Maze(mazeType=self.__mazeType, gen_algorithm=self.__genAlgorithm, solve_algorithm=self.__solveAlgorithm, mazeWidth=self.__mazeWidth, mazeHeight=self.__mazeHeight, mazeGrid=self.__mazeGrid)
        else:
            self.__maze = Mazes.Maze(mazeType=self.__mazeType, gen_algorithm=self.__genAlgorithm, solve_algorithm=self.__solveAlgorithm, mazeWidth=self.__mazeWidth, mazeHeight=self.__mazeHeight)
        self.__maze.generate()

        # Send maze to opponent if playing online
        if self.__online and self.__mazeGrid == None:
            self.__LANInstance.sendMaze(self.mazeToJSON(self.__maze))

        # Initialize pygame GUI
        self.__UIinstance.initPygame(self.__maze, gui=True)

        # Start pygame timer for updating the GUI
        self.__pygame_timer = QTimer(self)
        self.__pygame_timer.timeout.connect(lambda: self.updatePygame())
        self.__pygame_timer.start(33)  # 30 fps

        # Start timers for online gameplay tasks
        if self.__online:
            # Timer for updating opponent's move
            self.__update_opponent_timer = QTimer(self)
            self.__update_opponent_timer.timeout.connect(lambda: self.updateOpponent())
            self.__update_opponent_timer.start(100)

            # Timer for getting opponent's move
            self.__get_opponent_move_timer = QTimer(self)
            self.__get_opponent_move_timer.timeout.connect(lambda: self.getOpponentMove())
            self.__get_opponent_move_timer.start(100)

            # Timer for checking opponent's win
            self.__check_opponent_win_timer = QTimer(self)
            self.__check_opponent_win_timer.timeout.connect(lambda: self.checkOpponentWin())
            self.__check_opponent_win_timer.start(1000)

            # Timer for checking opponent's disconnection
            self.__check_opponent_disconnected_timer = QTimer(self)
            self.__check_opponent_disconnected_timer.timeout.connect(lambda: self.checkOpponentDisconnected())
            self.__check_opponent_disconnected_timer.start(1000)

    def updatePygame(self):
        """
        Updates the Pygame display and handles the necessary actions when the Pygame loop is finished.

        Returns:
            summaryStats (dict): A dictionary containing summary statistics of the game.
        """
        if self.__UIinstance.updatePygame(): # If the game is completed
            # Stop timers
            self.__pygame_timer.stop()
            self.__hide_distance_map_timer.stop()
            self.__get_time_taken_timer.stop()

            # Quit Pygame and get summary statistics
            self.__summaryStats = self.__UIinstance.quitPygame()

            if self.__solveAlgorithm != "manual":
                # Stop timers related to solving algorithm
                self.__update_program_state_timer.stop()
                self.__incorrect_moves_timer.stop()

            if self.__online:
                # Stop timers related to online multiplayer
                self.__update_opponent_timer.stop()
                self.__get_opponent_move_timer.stop()
                self.__check_opponent_win_timer.stop()

                if not self.__opponentWon:
                    # Send win signal to opponent if not already won
                    self.__LANInstance.sendWin()

            # Hide the current window
            self.hide()

            # Open the next window to display the solved maze
            self.__NextWindow = Ui_DialogMazeSolved(self.__desktopWidth, self.__desktopHeight, self.__summaryStats, self.__UIinstance, self.__LANInstance, self.__online)
            self.__NextWindow.show()

    def quitSolving(self):
        """
        Stops the solving process and performs necessary cleanup tasks.

        If the solve algorithm is not "manual", it stops the timers for incorrect moves and program state updates.
        If the application is running in online mode, it stops the timers for opponent updates, opponent moves, opponent win check, and opponent disconnection check.
        It also logs out from the LAN instance.
        Stops the timers for pygame, hiding the distance map, and getting the time taken.
        Closes the UI instance and shows the main menu window.
        """
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

    #===================================================================================================================================
    #=====================GETTER METHODS===================================================================================================
    #===================================================================================================================================

    def getPseudocode(self, algorithm):
        return self.__UIinstance.getPseudocodeText(algorithm)

    def getProgramState(self):
        self.__currentNeighboursText, self.__currentStackQueueText, self.__currentCellText = self.__UIinstance.getProgramStateText()
        self.__programStateLabel.setText(self.__currentCellText + "\n" + self.__currentNeighboursText + "\n" + self.__currentStackQueueText)

    def getOpponentMove(self):
        """
        Retrieves the opponent's move from the LAN instance and updates the UI accordingly.
        """
        self.__opponentMove = self.__LANInstance.getOpponentMove()
        if self.__opponentMove != None:
            self.__UIinstance.updateOpponentMove(self.__opponentMove)

    def getDistanceMapStatus(self):
        """
        Checks the status of the distance map and updates the show distance map button if necessary.

        Returns:
            None
        """
        # Check if the distance map is not currently shown
        if not self.__UIinstance.getDistanceMapStatus():
            # Update the show distance map button text to "Show Distance Map"
            self.__showDistanceMapButton.setText("Show Distance Map")

    def getTimeTaken(self):
        """
        Updates the label displaying the time taken to solve the maze.

        Returns:
            None
        """
        self.__timeTakenLabel.setText("Time: " + str(int(self.__UIinstance.getTimeTaken())) + "s")
        
    def about_action_triggered(self):
        pass

    def exit_action_triggered(self):
        sys.exit()


class Ui_DialogMazeSolved(QMainWindow):
    """
    This class represents the UI dialog for displaying the summary of a solved maze.

    Args:
        desktopWidth (int): The width of the desktop screen.
        desktopHeight (int): The height of the desktop screen.
        summaryStats (dict): A dictionary containing the summary statistics of the solved maze.
        UIinstance (object): An instance of the main UI class.
        LANInstance (object, optional): An instance of the LAN class. Defaults to None.
        online (bool, optional): Indicates if the application is running in online mode. Defaults to False.
    """

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
        with open("style.css", "r") as f:
            self.setStyleSheet(f.read())
        self.show()

    def setupUi(self):
        """
        Set up the user interface for the dialog.
        """
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
        """
        Set the texts for all the labels and buttons as per your requirement.
        """
        _translate = QtCore.QCoreApplication.translate
        # Set the texts for all the labels and buttons as per your requirement

    def onResize(self, event):
        """
        Event handler for resizing the dialog. Adjusts the font size and style of the UI elements.
        """
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
        """
        Event handler for the "Return to Menu" button. Closes the current dialog and returns to the main menu.
        """
        self.__UIinstance.closeProgram()
        if self.__online:
            self.__LANInstance.logout()
        self.hide()
        self.__BackWindow = Ui_MainMenu(self.__desktopWidth, self.__desktopHeight)
        self.__BackWindow.show()

    def downloadMaze(self):
        """
        Event handler for the "Download Maze" button. Downloads the maze if available.
        """
        if not self.__UIinstance.downloadMaze():
            self.errorDialog = Ui_Dialog("Error downloading maze! Try again.")
            self.errorself.show()

class TerminalUI(UI):
    """
    This class represents the terminal user interface for generating and solving mazes.

    Attributes:
        __gen_algorithms (list): A list of available maze generation algorithms.
        __solve_algorithms (list): A list of available maze solving algorithms.
        __maze (Maze): An instance of the Maze class representing the generated maze.

    Methods:
        run(): Runs the terminal user interface for generating and solving mazes.
    """

    def __init__(self):
        """
        Initializes the TerminalUI class.
        """
        self.__gen_algorithms = ["sidewinder", "binary_tree"]
        self.__solve_algorithms = ["depth_first", "breadth_first", "manual"]

    def run(self):
        """
        Runs the terminal user interface for generating and solving mazes.
        """
        # Prompt the user to choose a maze generation algorithm
        genAlgorithm = input("Please choose an algorithm to generate the maze, 1 for sidewinder, 2 for binary tree: ")
        while genAlgorithm != "1" and genAlgorithm != "2":
            genAlgorithm = input("Please input a valid option, 1 for sidewinder, 2 for binary tree: ")
        
        # Prompt the user to choose a maze solving algorithm
        solveAlgorithm = input("Please choose an algorithm to solve the maze, 1 for DFS, 2 for BFS, 3 for solving manually: ")
        while solveAlgorithm not in ["1", "2", "3"]:
            solveAlgorithm = input("Please input a valid option, 1 for DFS, 2 for BFS, 3 for manual solving: ")
        
        # Prompt the user to choose the type of maze
        mazeType = input("Please input the type of the maze, 1 for square, 2 for hexagonal, 3 for triangular: ")
        while mazeType not in ["1", "2", "3"]:
            mazeType = input("Please input a valid option, 1 for square, 2 for hexagonal, 3 for triangular: ")

        # Prompt the user to input the width of the maze
        mazeWidth = input("Please input the width of the maze: ")
        while not mazeWidth.isdigit() or int(mazeWidth) < 5 or int(mazeWidth) > 100:
            mazeWidth = input("Please input a valid size, between 5 and 100: ")
        
        # Prompt the user to input the height of the maze
        mazeHeight = input("Please input the height of the maze: ")
        while not mazeHeight.isdigit() or int(mazeHeight) < 5 or int(mazeHeight) > 100:
            mazeHeight = input("Please input a valid size, between 5 and 100: ")
        
        # Generate the maze based on user inputs
        self.__maze = Mazes.Maze(mazeType=int(mazeType), gen_algorithm=self.__gen_algorithms[int(genAlgorithm)-1], solve_algorithm=self.__solve_algorithms[int(solveAlgorithm)-1], mazeWidth=int(mazeWidth), mazeHeight=int(mazeHeight))

        # Generate the maze
        self.__maze.generate()

        # Initialize the pygame module
        self.initPygame(self.__maze)

        # Set the user interface type to "terminal"
        self.UiType = "terminal"

        while True:
            # Update the pygame display and check if the maze is solved
            if self.updatePygame():
                print("Congratulations! You solved the maze!")
                break




class GUI(UI):
    def __init__(self):
        """
        Initializes the GUI class.

        Args:
            None

        Returns:
            None
        """
        self.__app = QApplication(sys.argv)

        # Get the screen width and height
        self.__screenWidth = self.__app.desktop().screenGeometry().width()
        self.__screenHeight = self.__app.desktop().screenGeometry().height()

        self.UiType = "GUI"
        self.__GUI = Ui_MainMenu(self.__screenWidth, self.__screenHeight)

    def run(self):
        """
        Runs the GUI application.

        Args:
            None

        Returns:
            None
        """
        self.__GUI.show()
        self.__app.exec_()

class Ui_MainMenu(QMainWindow):
    def __init__(self, desktopWidth, desktopHeight):
        """
        Initializes the Ui_MainMenu class.

        Args:
            desktopWidth (int): The width of the desktop screen.
            desktopHeight (int): The height of the desktop screen.
        """
        super(Ui_MainMenu, self).__init__()
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.setWindowTitle("Main Menu: CompSci Maze Master")
        self.setupUi(self.__desktopWidth, self.__desktopHeight)
        with open("style.css", "r") as f:
            self.setStyleSheet(f.read())

    def setupUi(self, desktopWidth, desktopHeight):
        """
        Sets up the user interface for the main menu.

        Args:
            desktopWidth (int): The width of the desktop screen.
            desktopHeight (int): The height of the desktop screen.
        """
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
        """
        Translates the user interface texts.
        """
        _translate = QtCore.QCoreApplication.translate
        self.__TitleLabel.setText(_translate("MainMenu", "CompSci Maze Master"))
        self.__StartButton.setText(_translate("MainMenu", "Generate New Maze"))
        self.__menuHelp.setTitle(_translate("MainMenu", "Help"))
        self.__menuExit.setTitle(_translate("MainMenu", "Exit"))
        self.__StartButton.clicked.connect(self.StartButton_clicked)
        self.__PlayOverLANButton.clicked.connect(self.PlayOverLANButton_clicked)

    def StartButton_clicked(self):
        """
        Slot function for the StartButton clicked event.
        Hides the main menu and shows the GenerateMazeMenu.
        """
        self.hide()
        self.__ForwardWindow = Ui_GenerateMazeMenu(self.__desktopWidth, self.__desktopHeight)
        self.__ForwardWindow.show()

    def PlayOverLANButton_clicked(self):
        """
        Slot function for the PlayOverLANButton clicked event.
        Hides the main menu and shows the Login window.
        """
        self.hide()
        self.__ForwardWindow = Ui_Login(self.__desktopWidth, self.__desktopHeight)
        self.__ForwardWindow.show()

    def about_action_triggered(self):
        """
        Slot function for the About action triggered event.
        Shows the HelpMenu window.
        """
        self.__helpMenu = Ui_HelpMenu(self.__desktopWidth, self.__desktopHeight)
        self.__helpMenu.show()

    def exit_action_triggered(self):
        """
        Slot function for the Exit action triggered event.
        Exits the application.
        """
        sys.exit()

class Ui_GenerateMazeMenu(QtWidgets.QMainWindow):
    """
    Class representing the UI for generating a new maze.
    Inherits from QtWidgets.QMainWindow.
    """

    def __init__(self, desktopWidth, desktopHeight, LANInstance=None, online=False):
        """
        Initializes the Ui_GenerateMazeMenu object.

        Parameters:
        - desktopWidth (int): The width of the desktop screen.
        - desktopHeight (int): The height of the desktop screen.
        - LANInstance (object): An instance of the LAN class (optional).
        - online (bool): Indicates if the application is running in online mode (optional).
        """
        super(Ui_GenerateMazeMenu, self).__init__()
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.__LANInstance = LANInstance
        self.__online = online
        self.setWindowTitle("Generate New Maze: CompSci Maze Master")
        self.setupUi(self.__desktopWidth, self.__desktopHeight)
        with open("style.css", "r") as f:
            self.setStyleSheet(f.read())

    def setupUi(self, desktopWidth, desktopHeight):
        """
        Sets up the user interface for generating a new maze.

        Parameters:
        - desktopWidth (int): The width of the desktop screen.
        - desktopHeight (int): The height of the desktop screen.
        """
        self.resize(self.__desktopWidth * 0.6, self.__desktopHeight * 0.6)
        self.setObjectName("GenerateMazeMenu")
        self.__centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.__centralwidget)
        self.__BackButton = QtWidgets.QPushButton("Back", self)
        self.__BackButton.setGeometry(20, 60, 100, 80)  # Adjust size and position as needed
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
        """
        Sets the text for the UI elements.
        """
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
        """
        Slot function for the MazeSizeSliderX value changed event.
        Updates the text of the maze width label.
        """
        self.__mazeSizeTextX.setText("Maze Width: " + str(self.__mazeSizeSliderX.value()))


    def MazeSizeSliderY_valueChanged(self):
        """
        Callback function for when the value of the Maze Size Slider Y changes.
        Updates the text of the Maze Size Text Y label with the new value.

        Parameters:
        - self: The instance of the UI class.

        Returns:
        - None
        """
        # Update the text of the Maze Size Text Y label with the new value
        self.__mazeSizeTextY.setText("Maze Height: " + str(self.__mazeSizeSliderY.value()))

    def getMazeConfig(self):
        """
        Returns the maze configuration.

        Returns:
        - The maze configuration if it is not None.
        - None if the maze configuration is None.
        """
        if self.__mazeConfig != None:
            return self.__mazeConfig
        else:
            return None
        
    def about_action_triggered(self):
        """
        Slot function for the About action triggered event.
        Shows the HelpMenu window.
        """
        self.__helpMenu = Ui_HelpMenu(self.__desktopWidth, self.__desktopHeight)
        self.__helpMenu.show()

    def exit_action_triggered(self):
        """
        Slot function for the Exit action triggered event.
        Exits the application.
        """
        sys.exit()

    def BackButton_clicked(self):
        """
        Callback function for the Back Button clicked event.
        Hides the current window and shows the Main Menu window.
        """
        self.hide()
        self.__BackWindow = Ui_MainMenu(self.__desktopWidth, self.__desktopHeight)
        self.__BackWindow.show()

    def GenerateMazeButton_clicked(self):
        """
        Callback function for the Generate Maze Button clicked event.
        Retrieves the selected options for maze generation, solving algorithm, and maze type.
        If all options are selected, hides the current window and shows the Maze Solve Window.
        Otherwise, displays an error dialog prompting the user to select all options.
        """
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
            # If all options are selected, hide the current window and show the Maze Solve Window
            self.hide()
            self.__ForwardWindow = Ui_MazeSolveWindow(self.__desktopWidth, self.__desktopHeight, self.__genAlgorithm, self.__solveAlgorithm, self.__mazeType, self.__mazeSizeSliderX.value(), self.__mazeSizeSliderY.value(), LANInstance=self.__LANInstance, online=self.__online)
            self.__ForwardWindow.show()
        else:
            # If any option is not selected, display an error dialog
            self.__Dialog = QtWidgets.QDialog()
            self.__error = Ui_Dialog("Please select all options!", self.__desktopWidth, self.__desktopHeight)
            self.__error.show()



class Ui_Dialog(QDialog):
    """
    This class represents a custom dialog window for displaying a popup message.

    Args:
        text (str): The text to be displayed in the dialog.
        desktopWidth (int): The width of the desktop screen.
        desktopHeight (int): The height of the desktop screen.
    """

    def __init__(self, text, desktopWidth, desktopHeight):
        super(Ui_Dialog, self).__init__()
        self.__text = text
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.setWindowTitle("Popup")
        self.setupUi()
        with open("style.css", "r") as f:
            self.setStyleSheet(f.read())

    def setupUi(self):
        """
        Sets up the user interface of the dialog window.
        """
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
    """
    This class represents a custom dialog window for requesting to play a game.

    Args:
        text (str): The text to be displayed in the dialog.
        desktopWidth (int): The width of the desktop screen.
        desktopHeight (int): The height of the desktop screen.
    """

    def __init__(self, text, desktopWidth, desktopHeight):
        super(Ui_RequestToPlayDialog, self).__init__()
        self.__text = text
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.__acceptGameState = None
        self.setWindowTitle("Popup")
        self.setupUi()
        with open("style.css", "r") as f:
            self.setStyleSheet(f.read())

    def setupUi(self):
        """
        Sets up the user interface of the dialog window.
        """
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
        """
        Sets the text of the dialog window and label.
        """
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Dialog"))
        self.__label.setText(_translate("Dialog", self.__text))

    def acceptGame(self):
        """
        Sets the accept game state to True when the 'Accept' button is clicked.
        """
        self.__acceptGameState = True

    def rejectGame(self):
        """
        Sets the accept game state to False when the 'Reject' button is clicked.
        """
        self.__acceptGameState = False

    def getAcceptGame(self):
        """
        Returns the accept game state.

        Returns:
            bool: The accept game state.
        """
        return self.__acceptGameState

class Ui_OpponentWonDialog(QDialog):
    def __init__(self, text, desktopWidth, desktopHeight):
        """
        Initializes the Ui_OpponentWonDialog class.

        Args:
            text (str): The text to be displayed in the dialog.
            desktopWidth (int): The width of the desktop screen.
            desktopHeight (int): The height of the desktop screen.
        """
        super(Ui_OpponentWonDialog, self).__init__()
        self.__text = text
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.__continuePlayingState = None
        self.setWindowTitle("Popup")
        self.setupUi()
        with open("style.css", "r") as f:
            self.setStyleSheet(f.read())

    def setupUi(self):
        """
        Sets up the user interface for the opponent won dialog.
        """
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
        """
        Sets the text of the dialog window and label.
        """
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Dialog"))
        self.__label.setText(_translate("Dialog", self.__text))

    def continuePlaying(self):
        """
        Sets the continue playing state to True when the 'Continue playing' button is clicked.
        """
        self.__continuePlayingState = True

    def backToMenu(self):
        """
        Closes the current dialog and opens the main menu when the 'Back to menu' button is clicked.
        Sets the continue playing state to False.
        """
        self.__mainMenu = Ui_MainMenu(self.__desktopWidth, self.__desktopHeight)
        self.__mainMenu.show()
        self.close()
        self.__continuePlayingState = False
    
    def getContinuePlayingState(self):
        """
        Returns the continue playing state.

        Returns:
            bool: The continue playing state.
        """
        return self.__continuePlayingState

    
class Ui_LANAndWebSockets(QtWidgets.QMainWindow):
    def __init__(self, desktopWidth, desktopHeight, username):
        """
        Initializes the Ui_LANAndWebSockets class.
        This class represents the user interface for playing over LAN using WebSockets.

        Args:
            desktopWidth (int): The width of the desktop.
            desktopHeight (int): The height of the desktop.
            username (str): The username of the user.
        """
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
        with open("style.css", "r") as f:
            self.setStyleSheet(f.read())

    def setupUi(self, desktopWidth, desktopHeight):
        """
        Sets up the user interface.

        Args:
            desktopWidth (int): The width of the desktop.
            desktopHeight (int): The height of the desktop.
        """
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
    #=======================================================================================================================
    #=========================WEBSOCKET METHODS=============================================================================
    #=======================================================================================================================
    def connectToWebSocket(self):
        """
        Connects to the WebSocket server.
        """
        #self.__websocket.open(QUrl("ws://192.168.68.102:8080"))
        self.__websocket.open(QUrl("ws://localhost:8080"))

    def websocket_error(self, error):
        """
        Handles WebSocket connection errors.

        Args:
            error: The error object.
        """
        self.__errorDialog = Ui_Dialog("Error connecting to server! Try restarting the server.", self.__desktopWidth, self.__desktopHeight)
        self.__errorDialog.show()
        self.connectToWebSocket()

    def sendWebSocketMessage(self, message):
        """
        Sends a message to the WebSocket server.

        Args:
            message: The message to send.
        """
        self.__websocket.sendTextMessage(json.dumps(message))

    def websocket_connected(self):
        """
        Handles the WebSocket connection success.
        """
        print("Connected to websocket")
        self.__logout = False
        self.__websocket.sendTextMessage(json.dumps({"type": "login", "user": self.__username}))
    
    def websocket_disconnected(self):
        """
        Handles the WebSocket disconnection.
        """
        if not(self.__logout):
            self.__errorDialog = Ui_Dialog("Disconnected from server! Try restarting the server.", self.__desktopWidth, self.__desktopHeight)
            self.__errorDialog.show()

    def websocket_message(self, message):
        """
        Handles the received messages from the WebSocket server.

        Args:
            message (str): The received message.

        Returns:
            None

        Raises:
            json.JSONDecodeError: If there is an error decoding the JSON message.
        """
        try:
            message_data = json.loads(message)
            # Handle login message
            if message_data["type"] == "login":
                if message_data["success"]:
                    self.getAvailablePlayers(message_data["connectedUsers"])
                else:
                    # If the username is taken, show an error dialog and go send back to Main menu
                    self.__BackWindow = Ui_MainMenu(self.__desktopWidth, self.__desktopHeight)
                    self.__BackWindow.show()
                    self.hide()
                    self.__errorDialog = Ui_Dialog("Username Taken! Try another name.", self.__desktopWidth, self.__desktopHeight)
                    self.__errorDialog.show()
                
            # Handle logout message
            elif message_data["type"] == "logout":
                if message_data["success"]:
                    self.hide()
                    self.__BackWindow = Ui_MainMenu(self.__desktopWidth, self.__desktopHeight)
                    self.__BackWindow.show()
                else:
                    self.__errorDialog = Ui_Dialog("Error logging out!")
                    self.__errorDialog.show()

            # Handle new user message
            elif message_data["type"] == "newUser":
                self.getAvailablePlayers(message_data["connectedUsers"])

            # Handle play request message
            elif message_data["type"] == "playRequest":
                self.requestToPlayDialog = Ui_RequestToPlayDialog(f"{message_data['user']} wants to play with you!", self.__desktopWidth, self.__desktopHeight)
                self.requestToPlayDialog.show()

                self.hideUserButton(message_data["user"])

                self.check_accept_game_timer = QtCore.QTimer()
                self.check_accept_game_timer.timeout.connect(lambda: self.checkAcceptGame(message_data))
                self.check_accept_game_timer.start(1000)

            # Handle confirmation accept request message
            elif message_data["type"] == "confirmationAcceptRequest":
                self.__currentOpponent = message_data["user"] 
                self.hide()
                self.__ForwardWindow = Ui_GenerateMazeMenu(self.__desktopWidth, self.__desktopHeight, self, online=True)
                self.__ForwardWindow.show()

            # Handle confirmation reject request message
            elif message_data["type"] == "confirmationRejectRequest":
                try:
                    self.__errorDialog = Ui_Dialog("Game rejected!")
                    self.__errorDialog.show()
                except Exception as e:
                    print(e)
                    self.__errorDialog = Ui_Dialog("Error rejecting game! Try again.", self.__desktopWidth, self.__desktopHeight)
                    self.__errorDialog.show()
            # Handle maze message
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

            # Handle move message
            elif message_data["type"] == "move":
                self.__currentOpponentCellID = message_data["move"]

            # Handle win message
            elif message_data["type"] == "win":
                self.__opponentWon = True

            # Handle keepalive message
            elif message_data["type"] == "keepalive":
                self.sendWebSocketMessage({"type": "keepalive", "user": self.__username, "alive": True})

            # Handle opponent disconnected message
            elif message_data["type"] == "opponentDisconnected":
                self.__opponentDisconnected = True
                self.opponentDisconnectedDialog = Ui_Dialog("Opponent disconnected!", self.__desktopWidth, self.__desktopHeight)
                self.opponentDisconnectedDialog.show()

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    def logout(self):
        """
        Logs out the user by sending a logout message to the WebSocket server,
        closing the WebSocket connection, and setting the logout flag to True.
        """
        self.sendWebSocketMessage({"type": "logout", "user": self.__username})
        self.__logout = True
        self.__websocket.close()

    #=======================================================================================================================
    #=========================MAZE ONLINE METHODS===========================================================================
    #=======================================================================================================================
            
    def sendCurrentCell(self, currentCellID):
        """
        Sends the current cell ID to the WebSocket server.

        Args:
            currentCellID: The ID of the current cell.
        """
        self.sendWebSocketMessage({"type": "sendMove", "user": self.__username, "opponent": self.__currentOpponent, "currentCell": currentCellID})

    def getOpponentMove(self):
        """
        Returns the move made by the opponent.

        Returns:
            The move made by the opponent.
        """
        return self.__currentOpponentCellID

    def checkOpponentWin(self):
        """
        Checks if the opponent has won.

        Returns:
            True if the opponent has won, False otherwise.
        """
        return self.__opponentWon

    def checkOpponentDisconnected(self):
        """
        Checks if the opponent has disconnected.

        Returns:
            True if the opponent has disconnected, False otherwise.
        """
        return self.__opponentDisconnected
    
    def checkAcceptGame(self, message_data):
        """
        Checks if the game request has been accepted or rejected.

        Args:
            message_data (dict): The message data received from the WebSocket server.
        """
        # Check if the game request has been accepted or rejected
        if self.requestToPlayDialog.getAcceptGame() != None:
            if self.requestToPlayDialog.getAcceptGame():
                # Send a WebSocket message to accept the game request
                self.sendWebSocketMessage({"type": "acceptGame", "user": self.__username, "opponent": message_data["user"]})
                self.__currentOpponent = message_data["user"]
            else:
                # Send a WebSocket message to reject the game request
                self.sendWebSocketMessage({"type": "rejectGame", "user": self.__username, "opponent": message_data["user"]})
            
            # Close the requestToPlayDialog
            self.requestToPlayDialog.close()
            self.check_accept_game_timer.stop()
            
            # Show a loading dialog while waiting for the opponent to create a maze
            self.loadingDialog = Ui_Dialog("Waiting for opponent to create maze...", self.__desktopWidth, self.__desktopHeight)
            self.loadingDialog.show()

    def getAvailablePlayers(self, players):
        """
        Gets the available players from the WebSocket server.

        Args:
            players: The list of available players.
        """
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

    def hideUserButton(self, user):
        """
        Hides the button of the specified user.

        Args:
            user: The user whose button will be hidden.
        """
        self.__playerButtonDict[user].hide()


    def getOpponentName(self):
        """
        Returns the name of the current opponent.

        Returns:
            The name of the current opponent.
        """
        return self.__currentOpponent

    def getCurrentOpponentCellID(self):
        """
        Returns the current opponent's cell ID.

        Returns:
            The current opponent's cell ID.
        """
        return self.__currentOpponentCellID

    def sendMaze(self, maze):
        """
        Sends the maze to the current opponent.

        Args:
            maze: The maze to be sent.
        """
        self.sendWebSocketMessage({"type": "sendMaze", "user": self.__username, "opponent": self.__currentOpponent, "maze": maze})

    def sendWin(self):
        """
        Sends a win message to the WebSocket server.

        This function sends a message to the WebSocket server indicating that the player has won the game.

        Args:
            None

        Returns:
            None
        """
        self.sendWebSocketMessage({"type": "win", "user": self.__username, "opponent": self.__currentOpponent})

    #=======================================================================================================================
    #=========================MISCELLANEOUS UI METHODS======================================================================
    #=======================================================================================================================
            
    def BackButton_clicked(self):
        """
        Handles the click event of the back button.
        Performs logout, hides the current window, and shows the main menu window.
        """
        self.logout()
        self.hide()
        self.__BackWindow = Ui_MainMenu(self.__desktopWidth, self.__desktopHeight)
        self.__BackWindow.show()

    def playerButtonClicked(self, player):
        """
        Handles the click event of a player button.
        Sets the current opponent and sends a request to play message to the WebSocket server.

        Args:
            player: The name of the selected player.
        """
        self.__currentOpponent = player
        # Send a request to play message to the WebSocket server
        self.sendWebSocketMessage({"type": "requestToPlay", "user": self.__username, "opponent": player})

    def resizeEvent(self, event):
        """
        Overrides the resizeEvent function of QMainWindow.

        This function is called when the window is resized. It adjusts the position of the back button.

        Args:
            event: The resize event.

        Returns:
            None
        """
        QtWidgets.QMainWindow.resizeEvent(self, event)
        # Adjust the back button position on resize
        self.__BackButton.move(20, 20)

class Ui_Login(QtWidgets.QDialog):
    """
    This class represents the login dialog UI.

    Args:
        desktopWidth (int): The width of the desktop screen.
        desktopHeight (int): The height of the desktop screen.
    """

    def __init__(self, desktopWidth, desktopHeight):
        super(Ui_Login, self).__init__()
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.setupUi()
        with open("style.css", "r") as f:
            self.setStyleSheet(f.read())

    def setupUi(self):
        """
        Sets up the user interface for the login dialog.
        """
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
        """
        Translates the text of the UI elements.
        """
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Login"))
        self.__groupBox_2.setTitle(_translate("Dialog", "Enter Username:"))

    def onResize(self, event):
        """
        Event handler for the resize event of the dialog.
        Adjusts the font size based on the window size.
        """
        # Adjust font size based on window size
        fontSize = max(8, min(self.width(), self.height()) // 50)
        font = QtGui.QFont("Arial", fontSize)
        self.__groupBox_2.setFont(font)
        self.__lineEdit.setFont(font)
    
    def login(self):
        """
        Performs the login operation.
        If the entered username is valid, hides the login dialog and shows the main application window.
        Otherwise, shows an error dialog.
        """
        # Get the entered username from the line edit
        self.__username = self.__lineEdit.text()

        # Regular expression pattern to validate the username
        self.__usernameRegex = '^[a-zA-Z0-9]+$'

        # Check if the entered username matches the regex pattern
        if re.match(self.__usernameRegex, self.__username):
            # Hide the login dialog
            self.hide()

            # Create an instance of the main application window
            self.__ForwardWindow = Ui_LANAndWebSockets(self.__desktopWidth, self.__desktopHeight, self.__username)

            # Show the main application window
            self.__ForwardWindow.show()
        else:
            # Show an error dialog if the username is invalid
            self.__errorDialog = Ui_Dialog("Please enter a valid username!")
            self.__errorDialog.show()

    def backToMainMenu(self):
        """
        Goes back to the main menu.
        Hides the login dialog and shows the main menu window.
        """
        self.hide()
        self.__BackWindow = Ui_MainMenu(self.__desktopWidth, self.__desktopHeight)
        self.__BackWindow.show()


class Ui_HelpMenu(QMainWindow):
    def __init__(self, desktopWidth, desktopHeight):
        """
        Initializes the HelpMenu UI class.

        Args:
            desktopWidth (int): The width of the desktop screen.
            desktopHeight (int): The height of the desktop screen.
        """
        super(Ui_HelpMenu, self).__init__()
        self.__desktopWidth = desktopWidth
        self.__desktopHeight = desktopHeight
        self.setupUi()
        with open("style.css", "r") as f:
            self.setStyleSheet(f.read())

    def setupUi(self):
        """
        Sets up the UI components and layout.
        """
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
        """
        This function is responsible for retranslating the UI elements.

        It sets the window title, HTML content for a text browser, and label text.
        It also adjusts the font size based on the width of the window.

        Args:
            self: The instance of the class.

        Returns:
            None
        """
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
        """
        This function is triggered when the window is resized.

        It adjusts the font size of the label and text browser based on the width of the window.

        Args:
            self: The instance of the class.
            event: The resize event.

        Returns:
            None
        """
        newFont = self.__label.font()
        newFont.setPointSize(max(8, int(self.width() / 80)))  # Adjust this ratio as needed
        self.__label.setFont(newFont)
        self.__textBrowser.setFont(newFont)
        super(Ui_HelpMenu, self).resizeEvent(event)
