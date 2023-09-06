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
        self.mouse_pos_x, self.mouse_pos_y = pg.mouse.get_pos()
        if self.maze.type == "square":
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
        elif self.maze.type == "hexagonal":
            for p in self.points:
                if self.mouse_pos_x > self.maze_width and self.mouse_pos_y > self.maze_height:
                    break
                if self.is_inside_polygon(self.mouse_pos_x, self.mouse_pos_y, p):
                    
                    self.cell_x = self.points.index(p)
                    counter = 0
                    flag = False
                    
                    for y in range(self.maze.size):
                        
                        for x in range(len(self.maze.grid[y])):
              
                            if counter == self.cell_x:
                                self.cell = self.maze.grid[y][x]
                                

                                flag = True
                                break
                            counter += 1
                        if flag:
                            break                            
                    pg.draw.polygon(self.screen, self.HOVER_COLOUR, p, 2)
                    pg.mouse.set_cursor(*pg.cursors.broken_x)
                    if clicked:
                        return self.cell
                    break
                

    def displaySide(self):
        pg.draw.rect(self.screen, (200, 200, 200), (self.maze_width, 0, self.side_width, self.side_height))
        self.title_font = pg.font.SysFont('Arial', 30)
        
        self.title_text = self.TITLE_DICT[self.maze.solve_algorithm_name]

        # center align in the side panel
        self.render_text(self.title_font, [self.title_text], self.maze_width + self.side_width//2 - self.title_font.size(self.title_text)[0]//2, 50, self.BLACK)       
        self.render_instructions()

    def highlightVisitedCells(self):
        for cell in self.token_visited_cells_coords:
            if self.maze.type == "square":
                pg.draw.rect(self.screen, self.YELLOW, (cell[0], cell[1], self.cell_width - self.cell_width*0.2, self.cell_height - self.cell_height*0.2), 2)
            elif self.maze.type == "hexagonal":
                self.drawHexagon(cell[0]+self.cell_width*0.1, cell[1]+self.cell_width*0.1, self.cell_side_length - self.cell_side_length*0.2, self.YELLOW)

    def drawHexagon(self, x, y, size, color=(0, 0, 0)):
        hexagon_points = []
        for i in range(6):
            angle_deg = 60 * i -30
            angle_rad = math.pi / 180 * angle_deg
            hexagon_points.append((x + size * math.cos(angle_rad), y + size * math.sin(angle_rad)))
        pg.draw.polygon(self.screen, color, hexagon_points, 2)
        self.points.append(hexagon_points)



    def draw_hexagon_connection(self, cell1, cell2, x, y, size):
        # draw a white line between the two cells
        self.cell1_x, self.cell1_y = x, y
        self.cell2_x, self.cell2_y = cell2.id
        self.cell2_x, self.cell2_y = (self.cell2_x * self.cell_width) + (self.cell_width/2) + self.maze_width*0.025, self.cell2_y * self.cell_height + self.maze_height*0.025 + self.cell_width/2
        

        if cell2.id[1] % 2 == 1:
            self.cell2_x += 0.5 * self.cell_width
        
        #pg.draw.line(self.screen, self.GREEN, (self.cell1_x, self.cell1_y), (self.cell2_x, self.cell2_y), 2)

        if int(self.cell1_y) == int(self.cell2_y):
           
            self.start_x = min([self.cell1_x, self.cell2_x]) + self.cell_width/2
            self.end_x = self.start_x
            self.start_y = self.cell1_y - self.cell_side_length/2 
            self.end_y = self.start_y + self.cell_side_length 
        else:
            if self.cell1_y < self.cell2_y:
                self.start_x = self.cell2_x 
                self.end_x = self.cell1_x
                self.start_y = self.cell2_y - self.cell_side_length
                self.end_y = self.cell1_y + self.cell_side_length
            else:
                self.start_x = self.cell1_x 
                self.end_x = self.cell2_x
                self.start_y = self.cell1_y - self.cell_side_length
                self.end_y = self.cell2_y + self.cell_side_length

        pg.draw.line(self.screen, self.WHITE, (self.start_x, self.start_y), (self.end_x, self.end_y), 4)

    def get_triangle_base_points(self, x, y):
        
        base_point_1 = [(x * self.cell_width)  + self.maze_width*0.025, (y * (self.cell_height))  + self.maze_height*0.025]
        base_point_2 = [base_point_1[0]+self.cell_side_length, (y * (self.cell_height))  + self.maze_height*0.025]
        if not(x % 2 == 1 and y%2 == 1) and (x % 2 == 1 or y%2 == 1):
            base_point_1[1] += self.cell_height
            base_point_2[1] += self.cell_height
      

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
        pg.draw.polygon(self.screen, color, triangle_points, 2)
        self.points.append(triangle_points)        


    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def draw_triangle_connection(self, cell1, cell2, size):
        cell1_base_point_1, cell1_base_point_2 = self.get_triangle_base_points(cell1.id[0], cell1.id[1])
        cell2_base_point_1, cell2_base_point_2 = self.get_triangle_base_points(cell2.id[0], cell2.id[1])
     
        if list(map(int, cell1_base_point_1)) == list(map(int, cell2_base_point_1)):
            line_start = cell1_base_point_1
            line_end = cell1_base_point_2
        elif self.distance(cell1_base_point_1[0], cell1_base_point_1[1], cell2_base_point_2[0], cell2_base_point_2[0] ) < self.distance(cell1_base_point_2[0], cell1_base_point_2[1], cell2_base_point_1[0], cell2_base_point_1[0] ):
            line_start = cell1_base_point_1
            line_end = cell2_base_point_2
        else:
            line_start = cell1_base_point_2
            line_end = cell2_base_point_1
        pg.draw.line(self.screen, self.BLUE, line_start, line_end, 2)
        
       
       

    def displayMaze(self):
        self.screen.fill(self.WHITE)
        if self.maze.type == "square":
            self.cell_width = self.maze_width / self.maze.size
            self.cell_height = self.maze_width / self.maze.size

            for y in range(self.maze.size):
                for x in range(self.maze.size):
                    cell = self.maze.grid[y][x]
                    
                    if y == 0 or self.maze.grid[y-1][x] not in cell.connections:
                        pg.draw.line(self.screen, self.BLACK, (x *  self.cell_width, y *  self.cell_height), 
                                                    ((x+1) *  self.cell_width, y *  self.cell_height))
                
                    if x == 0 or not(str(self.maze.grid[y][x-1]) in [str(i) for i in cell.connections]):
                        pg.draw.line(self.screen, self.RED, (x *  self.cell_width, y *  self.cell_height), 
                                                    (x *  self.cell_width, (y+1) *  self.cell_height))
            
            pg.draw.circle(self.screen, self.GREEN, (self.current_cell.id[0] * self.cell_width + self.cell_width/2, self.current_cell.id[1] * self.cell_height + self.cell_height/2), self.cell_width/4)
            self.token_visited_cells_coords.append((self.current_cell.id[0] * self.cell_width + self.cell_width*0.1, self.current_cell.id[1] * self.cell_height + self.cell_height*0.1))
            self.highlightVisitedCells()
        elif self.maze.type == "hexagonal":
            self.points = []
            self.cell_width = ((self.maze_width*0.95) / self.maze.size)
            self.cell_side_length =  2*((self.cell_width / 2) / math.tan(math.pi / 3))
            self.cell_height = (self.cell_side_length * 2) - (self.cell_side_length / 2)


            for y in range(self.maze.size):
                for x in range(self.maze.size):
                    if y % 2 == 1 and x == self.maze.size - 1:
                        break
                    cell = self.maze.grid[y][x]
                    self.curr_x =  (x * self.cell_width) + (self.cell_width/2) + self.maze_width*0.025
                    self.curr_y = (y * (self.cell_height)) + (self.cell_width/2)  + self.maze_height*0.025
                    if y % 2 == 1:
                        self.curr_x += 0.5 * self.cell_width

                    self.drawHexagon(self.curr_x, self.curr_y, self.cell_side_length)
                    self.cell_connections = cell.connections

                    for c in self.cell_connections:
                        self.draw_hexagon_connection(self.maze.grid[y][x], c, self.curr_x, self.curr_y, self.cell_side_length)

            self.circle_x = self.current_cell.id[0] * self.cell_width + self.cell_width/2 + self.maze_width*0.025
            self.circle_y = self.current_cell.id[1] * self.cell_height + self.cell_height/2 + self.maze_height*0.025
            if self.current_cell.id[1] % 2 == 1:
                self.circle_x += 0.5 * self.cell_width
            pg.draw.circle(self.screen, self.GREEN, (self.circle_x, self.circle_y), self.cell_width/4)
            self.token_visited_cells_coords.append((self.circle_x - self.cell_width*0.1, self.circle_y - self.cell_height*0.1))
            self.highlightVisitedCells()
        elif self.maze.type == "triangular":
            self.points = []
            self.cell_height = ((self.maze_height*0.95) / (self.maze.size))
            self.cell_side_length = self.cell_height / math.sin(math.pi/3)
            self.cell_width = self.cell_side_length / 2
            for y in range(self.maze.size):
                for x in range(len(self.maze.grid[y])):
                    self.flipped = False
                    cell = self.maze.grid[y][x]
                    self.base_1, self.base_2 = self.get_triangle_base_points(x, y)
                    if x % 2 == 1:
                        self.flipped = True
                    if y%2 == 1:
                        self.flipped = not self.flipped

                    self.drawTriangle(self.base_1, self.base_2, self.cell_side_length, self.flipped)
              
                    self.cell_connections = cell.connections
                    for c in self.cell_connections:
                         self.draw_triangle_connection(self.maze.grid[y][x], c, self.cell_side_length)

    def pygameLoop(self):
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
            if self.maze.type == "square":
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
            elif self.maze.type == "hexagonal":
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.running = False
                    
                    elif event.type == pg.MOUSEBUTTONDOWN:
                        x, y = pg.mouse.get_pos()
                        if x < self.maze_width:
                            self.clicked_cell = self.cell_hover(clicked=True)
                            if self.clicked_cell != None:
                                self.solve_step_return_value = self.maze.solve_step(self.cell_hover(clicked=True).id , self.current_cell)
                                if self.solve_step_return_value == "end":
                                    self.current_cell = self.maze.grid[self.maze.size-1][len(self.maze.grid[self.maze.size-1])-1]
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
                            else:
                                print("Invalid move!")
                self.screen.fill(self.WHITE)

        pg.quit()


    def run(self):
        pass


class TerminalUI(UI):

    def __init__(self):
        self.maze = None
        pg.init()
        self.infoObject = pg.display.Info()

        self.width, self.height = self.infoObject.current_w*0.8, self.infoObject.current_h*0.8

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
        
        mazeType = input("Please input the type of the maze, 1 for square, 2 for hexagonal, 3 for triangular: ")
        if mazeType not in ["1", "2", "3"]:
            mazeType = input("Please input a valid option, 1 for square, 2 for hexagonal, 3 for triangular: ")

        mazeSize = input("Please input the size of the maze: ")
        if not mazeSize.isdigit() or int(mazeSize) < 5 or int(mazeSize) > 100:
            mazeSize = input("Please input a valid size, between 5 and 100: ")


        self.maze = Mazes.Maze(mazeType=int(mazeType), size=int(mazeSize), gen_algorithm=self.gen_algorithms[int(genAlgorithm)-1], solve_algorithm=self.solve_algorithms[int(solveAlgorithm)-1])

        self.maze.generate()
        
        self.pygameLoop()

    

