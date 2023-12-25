import pygame as pg
import Mazes
import time
from abc import ABC, abstractmethod
import math

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
        self.__instructions_text = self.__INSTRUCTIONS[self.__title_text].split(" ")
        self.__render_text(self.__instructions_font, self.__instructions_text, self.__maze_width + 10, 100, self.__BLACK)
        self.__psuedocode_font = pg.font.SysFont('Arial', 20)
        self.__psuedocode_text = self.__PSUEDOCODE[self.__title_text]
        self.__render_multiline_text(self.__psuedocode_font, self.__psuedocode_text, self.__maze_width + 10, 300, self.__BLACK)
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
        if self.__maze.type == "square":
            if self.__mouse_pos_x < self.__maze_width and self.__mouse_pos_y < self.__maze_height and self.__mouse_pos_x > 0 and self.__mouse_pos_y > 0:
                try:
                    self.__cell_width = self.__maze_width // self.__maze.size
                    self.__cell_height = self.__maze_height // self.__maze.size
                    self.__cell_x = self.__mouse_pos_x // self.__cell_width
                    self.__cell_y = self.__mouse_pos_y // self.__cell_height
                    self.__cell = self.__maze.grid[self.__cell_y][self.__cell_x]
                    pg.draw.rect(self.__screen, self.__HOVER_COLOUR , (self.__cell_x * self.__cell_width, self.__cell_y * self.__cell_height, self.__cell_width, self.__cell_height), 2)
                    pg.mouse.set_cursor(*pg.cursors.broken_x)
                except:
                    pass
        elif self.__maze.type == "hexagonal":
            for p in self.__points:
                if self.__mouse_pos_x > self.__maze_width and self.__mouse_pos_y > self.__maze_height:
                    break
                if self.__is_inside_polygon(self.__mouse_pos_x, self.__mouse_pos_y, p):
                    
                    self.__cell_x = self.__points.index(p)
                    counter = 0
                    flag = False
                    
                    for y in range(self.__maze.size):
                        
                        for x in range(len(self.__maze.grid[y])):
              
                            if counter == self.__cell_x:
                                self.__cell = self.__maze.grid[y][x]
                                

                                flag = True
                                break
                            counter += 1
                        if flag:
                            break                            
                    pg.draw.polygon(self.__screen, self.__HOVER_COLOUR, p, 2)
                    pg.mouse.set_cursor(*pg.cursors.broken_x)
                    if clicked:
                        return self.__cell
                    break
                

    def displaySide(self):
        pg.draw.rect(self.__screen, (200, 200, 200), (self.__maze_width, 0, self.__side_width, self.__side_height))
        self.__title_font = pg.font.SysFont('Arial', 30)
        
        self.__title_text = self.__TITLE_DICT[self.__maze.solve_algorithm_name]

        # center align in the side panel
        self.__render_text(self.__title_font, [self.__title_text], self.__maze_width + self.__side_width//2 - self.__title_font.size(self.__title_text)[0]//2, 50, self.__BLACK)       
        self.__render_instructions()

    def highlightVisitedCells(self):
        for cell in self.__token_visited_cells_coords:
            if self.__maze.type == "square":
                pg.draw.rect(self.__screen, self.__YELLOW, (cell[0], cell[1], self.__cell_width - self.__cell_width*0.2, self.__cell_height - self.__cell_height*0.2), 2)
            elif self.__maze.type == "hexagonal":
                self.__drawHexagon(cell[0]+self.__cell_width*0.1, cell[1]+self.__cell_width*0.1, self.__cell_side_length - self.__cell_side_length*0.2, self.__YELLOW)

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
        self.__cell2_x, self.__cell2_y = cell2.id
        self.__cell2_x, self.__cell2_y = (self.__cell2_x * self.__cell_width) + (self.__cell_width/2) + self.__maze_width*0.025, self.__cell2_y * self.__cell_height + self.__maze_height*0.025 + self.__cell_width/2
        

        if cell2.id[1] % 2 == 1:
            self.__cell2_x += 0.5 * self.__cell_width
        
        #pg.draw.line(self.__screen, self.__GREEN, (self.__cell1_x, self.__cell1_y), (self.__cell2_x, self.__cell2_y), 2)

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

        pg.draw.line(self.__screen, self.__WHITE, (self.__start_x, self.__start_y), (self.__end_x, self.__end_y), 4)

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
        cell1_base_point_1, cell1_base_point_2 = self.__get_triangle_base_points(cell1.id[0], cell1.id[1])
        cell2_base_point_1, cell2_base_point_2 = self.__get_triangle_base_points(cell2.id[0], cell2.id[1])

        if list(map(int, cell1_base_point_1)) == list(map(int, cell2_base_point_1)):
            line_start = cell1_base_point_1
            line_end = cell1_base_point_2

        elif self.__distance(cell1_base_point_1[0], cell1_base_point_1[1], cell2_base_point_2[0], cell2_base_point_2[1] ) < self.__distance(cell1_base_point_2[0], cell1_base_point_2[1], cell2_base_point_1[0], cell2_base_point_1[1] ):
            line_start = cell1_base_point_1
            line_end = cell2_base_point_2
        else:
            line_start = cell1_base_point_2
            line_end = cell2_base_point_1
        pg.draw.line(self.__screen, self.__WHITE, line_start, line_end, 2)


    def displayMaze(self):
        self.__screen.fill(self.__WHITE)
        if self.__maze.type == "square":
            self.__cell_width = self.__maze_width / self.__maze.size
            self.__cell_height = self.__maze_width / self.__maze.size

            for y in range(self.__maze.size):
                for x in range(self.__maze.size):
                    cell = self.__maze.grid[y][x]
                    
                    if y == 0 or self.__maze.grid[y-1][x] not in cell.connections:
                        pg.draw.line(self.__screen, self.__BLACK, (x *  self.__cell_width, y *  self.__cell_height), 
                                                    ((x+1) *  self.__cell_width, y *  self.__cell_height))
                
                    if x == 0 or not(str(self.__maze.grid[y][x-1]) in [str(i) for i in cell.connections]):
                        pg.draw.line(self.__screen, self.__RED, (x *  self.__cell_width, y *  self.__cell_height), 
                                                    (x *  self.__cell_width, (y+1) *  self.__cell_height))
            
            pg.draw.circle(self.__screen, self.__GREEN, (self.__current_cell.id[0] * self.__cell_width + self.__cell_width/2, self.__current_cell.id[1] * self.__cell_height + self.__cell_height/2), self.__cell_width/4)
            self.__token_visited_cells_coords.append((self.__current_cell.id[0] * self.__cell_width + self.__cell_width*0.1, self.__current_cell.id[1] * self.__cell_height + self.__cell_height*0.1))
            self.__highlightVisitedCells()
        elif self.__maze.type == "hexagonal":
            self.__points = []
            self.__cell_width = ((self.__maze_width*0.95) / self.__maze.size)
            self.__cell_side_length =  2*((self.__cell_width / 2) / math.tan(math.pi / 3))
            self.__cell_height = (self.__cell_side_length * 2) - (self.__cell_side_length / 2)


            for y in range(self.__maze.size):
                for x in range(self.__maze.size):
                    if y % 2 == 1 and x == self.__maze.size - 1:
                        break
                    cell = self.__maze.grid[y][x]
                    self.__curr_x =  (x * self.__cell_width) + (self.__cell_width/2) + self.__maze_width*0.025
                    self.__curr_y = (y * (self.__cell_height)) + (self.__cell_width/2)  + self.__maze_height*0.025
                    if y % 2 == 1:
                        self.__curr_x += 0.5 * self.__cell_width

                    self.__drawHexagon(self.__curr_x, self.__curr_y, self.__cell_side_length)
                    self.__cell_connections = cell.connections

                    for c in self.__cell_connections:
                        self.__draw_hexagon_connection(self.__maze.grid[y][x], c, self.__curr_x, self.__curr_y, self.__cell_side_length)

            self.__circle_x = self.__current_cell.id[0] * self.__cell_width + self.__cell_width/2 + self.__maze_width*0.025
            self.__circle_y = self.__current_cell.id[1] * self.__cell_height + self.__cell_height/2 + self.__maze_height*0.025
            if self.__current_cell.id[1] % 2 == 1:
                self.__circle_x += 0.5 * self.__cell_width
            pg.draw.circle(self.__screen, self.__GREEN, (self.__circle_x, self.__circle_y), self.__cell_width/4)
            self.__token_visited_cells_coords.append((self.__circle_x - self.__cell_width*0.1, self.__circle_y - self.__cell_height*0.1))
            self.__highlightVisitedCells()
            
        elif self.__maze.type == "triangular":
            self.__points = []
            self.__cell_height = ((self.__maze_height*0.95) / (self.__maze.size))
            self.__cell_side_length = self.__cell_height / math.sin(math.pi/3)
            self.__cell_width = self.__cell_side_length / 2
            for y in range(self.__maze.size):
                for x in range(len(self.__maze.grid[y])):
                    self.__flipped = False
                    cell = self.__maze.grid[y][x]
                    self.__base_1, self.__base_2 = self.__get_triangle_base_points(x, y)
                    if x % 2 == 1:
                        self.__flipped = True
                    if y%2 == 1:
                        self.__flipped = not self.__flipped

                    self.__drawTriangle(self.__base_1, self.__base_2, self.__cell_side_length, self.__flipped)
              
                    self.__cell_connections = cell.connections
                    for c in self.__cell_connections:
                         self.__draw_triangle_connection(self.__maze.grid[y][x], c, self.__cell_side_length)

    def pygameLoop(self):
        self.__screen = pg.display.set_mode((self.__width, self.__height))
        self.__running = True
        self.__screen.fill(self.__WHITE)
        self.__current_cell = self.__maze.grid[0][0]
        self.__token_visited_cells_coords = []
        while self.__running:
            self.__displayMaze()  
            self.__displaySide()
            self.__cell_hover()
            pg.display.flip()
            if self.__maze.type == "square":
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.__running = False
                    elif event.type == pg.KEYDOWN:
                        
                        if event.key == pg.K_LEFT:
                            self.__solve_step_return_value = self.__maze.solve_step((self.__current_cell.id[0]-1, self.__current_cell.id[1]), self.__current_cell)
                        elif event.key == pg.K_RIGHT:
                            self.__solve_step_return_value = self.__maze.solve_step((self.__current_cell.id[0]+1, self.__current_cell.id[1]), self.__current_cell)
                        elif event.key == pg.K_UP:
                            self.__solve_step_return_value = self.__maze.solve_step((self.__current_cell.id[0], self.__current_cell.id[1]-1), self.__current_cell)
                        elif event.key == pg.K_DOWN:
                            self.__solve_step_return_value = self.__maze.solve_step((self.__current_cell.id[0], self.__current_cell.id[1]+1), self.__current_cell)
                        elif event.key == pg.K_SPACE:
                            self.__solve_step_return_value = self.__maze.solve_step("space", self.__current_cell)
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
                            self.__solve_step_return_value = self.__maze.solve_step((x//self.__cell_width, y//self.__cell_height), self.__current_cell)
                            if self.__solve_step_return_value == "end":
                                self.__current_cell = self.__maze.grid[self.__maze.size-1][self.__maze.size-1]
                                self.__displayMaze()
                                pg.display.flip()
                                print("Congratulations! You solved the maze!")
                                self.__running = False
                            elif self.__solve_step_return_value == "invalid_move":
                                print("Invalid move!")
                            elif self.__solve_step_return_value == "wrong_move":
                                print("Wrong move!")
                            else:
                                self.__current_cell = self.__solve_step_return_value
                self.__screen.fill(self.__WHITE)
            elif self.__maze.type == "hexagonal":
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.__running = False
                    
                    elif event.type == pg.MOUSEBUTTONDOWN:
                        x, y = pg.mouse.get_pos()
                        if x < self.__maze_width:
                            self.__clicked_cell = self.__cell_hover(clicked=True)
                            if self.__clicked_cell != None:
                                self.__solve_step_return_value = self.__maze.solve_step(self.__cell_hover(clicked=True).id , self.__current_cell)
                                if self.__solve_step_return_value == "end":
                                    self.__current_cell = self.__maze.grid[self.__maze.size-1][len(self.__maze.grid[self.__maze.size-1])-1]
                                    self.__displayMaze()
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
                self.__screen.fill(self.__WHITE)

        pg.quit()


    def run(self):
        pass


class TerminalUI(UI):

    def __init__(self):
        self.__maze = None
        pg.init()
        self.__infoObject = pg.display.Info()

        self.__width, self.__height = self.__infoObject.current_w*0.8, self.__infoObject.current_h*0.8

        self.__maze_width, self.__maze_height = 2*(self.__width//3), self.__height
        self.__side_width, self.__side_height = self.__width - self.__maze_width, self.__height
    
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


        self.__maze = Mazes.Maze(mazeType=int(mazeType), size=int(mazeSize), gen_algorithm=self.__gen_algorithms[int(genAlgorithm)-1], solve_algorithm=self.__solve_algorithms[int(solveAlgorithm)-1])

        self.__maze.generate()
        
        self.__pygameLoop()

    

