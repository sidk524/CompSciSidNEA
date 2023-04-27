from tkinter import Button, Tk, Toplevel, Frame, N,S,E,W,X,Y, LEFT,RIGHT, END, Scrollbar, Text, Message, Grid, StringVar
from Game import Game, GameError
from sys import stderr
from itertools import product
from abc import ABC, abstractmethod
import PySimpleGUI as sg

class Ui(ABC):

    @abstractmethod
    def run(self):
        raise NotImplementedError

class SGui(Ui):
    def __init__(self) -> None:
        self.__game = Game()

        # Define layout for game board
        board_layout = [
            [sg.Button("", size=(10, 5), key=(i, j)) for j in range(3)] for i in range(3)
        ]

        # Define layout for main window
        player = self.__game.player
        layout = [
            [sg.Text(f"Player {player}'s turn", font=("Arial", 16), key="-TURN-")],
            [sg.Column(board_layout, element_justification="center")],
            [sg.Button("Restart", key="-RESTART-"), sg.Button("Exit", key="-EXIT-")],
        ]

        # Create window
        self.__window = sg.Window("Tic Tac Toe", layout)

    def run(self) -> None:
        while True:
            event, _ = self.__window.read()
            if event in (sg.WIN_CLOSED, "-EXIT-"):
                break
            if event == "-RESTART-":
                self.__game = Game()
                for cell in product(range(3),range(3)):
                    self.__window[cell].update("")
            elif self.__game.winner == None:
                row, col = event
                player = self.__game.player
                self.__window[(row, col)].update(player)
                self.__game.play(row+1, col+1)

                if self.__game.winner == Game.DRAW:
                    sg.popup(f"Draw!")
                elif self.__game.winner in [Game.P1,Game.P2]:
                    sg.popup(f"Player {player} wins!")

            player = self.__game.player
            self.__window["-TURN-"].update(f"Player {player}'s turn")

        # Close window
        self.__window.close()

class Gui(Ui):
    def __init__(self):
        root = Tk()
        root.title("Tic Tac Toe")
        frame = Frame(root)
        frame.pack()

        Button(
            frame,
            text='Show Help',
            command= self._help_callback).pack(fill=X)

        Button(
            frame,
            text='Play Game',
            command= self._play_callback).pack(fill=X)

        Button(
            frame,
            text='Quit',
            command=root.quit).pack(fill=X)

        self._root = root

    def _help_callback(self):
        pass

    def _play_callback(self):
        self._game = Game()

        game_win = Toplevel(self._root)
        game_win.title("Game")
        frame = Frame(game_win)
        frame.grid(row=0,column=0)

        dim = self._game.dim()
        self._buttons = [[None for _ in range(dim)] for _ in range(dim)]

        for row,col in product(range(dim),range(dim)):
            b = StringVar()
            b.set(self._game.at(row+1,col+1))

            cmd = lambda r=row,c=col : self._play_and_refresh(r,c)

            Button(
                frame,
                textvariable=b,
                command=cmd).grid(row=row,column=col)

            self._buttons[row][col] = b

        Button(game_win, text="Dismiss", command=game_win.destroy).grid(row=1,column=0)

    def _play_and_refresh(self,row,col):
        try:
            self._game.play(row+1,col+1)
        except GameError as e:
            print(e)

        dim = self._game.dim()
        for r,c in product(range(dim),range(dim)):
            text = self._game.at(r+1,c+1)
            self._buttons[r][c].set(text)

        w = self._game.winner 
        if w is not None:
            if w is Game.DRAW:
                print("The game was drawn")
            else:
                print(f"The winner is {w}")

    def run(self):
        self._root.mainloop()

class Terminal(Ui):
    def __init__(self):
        self._game = Game()

    def run(self):
        while not self._game.winner:
            while True:
                print(self._game)
                try:
                    row = int(input("Which row? "))
                    col = int(input("Which column? "))
                except ValueError:
                    print(f"Row and Column should be numbers in the range 1-{self._game.dim()}.")
                    continue
                try:
                    self._game.play(row,col)
                    break
                except GameError as e:
                    print(f"Game error {e}",file=stderr)

        print(self._game)
        w = self._game.winner
        if w is Game.DRAW:
            print("The game was drawn")
        else:
            print(f"The winner was {w}")
