from tkinter import Button, Tk, Toplevel, Frame, N,S,E,W,X,Y, LEFT,RIGHT, END, Scrollbar, Text, Message, Grid, StringVar
from Game import Game, GameError
from sys import stderr
from itertools import product
from abc import ABC, abstractmethod
from Client import Client
from asyncio import sleep
from aioconsole import ainput

class Ui(ABC):

    @abstractmethod
    def run(self):
        raise NotImplementedError

class Gui(Ui):
    def __init__(self,network=False):
        self._help_win = None
        self._game_win = None
        self._client = Client() if network else None

        root = Tk()
        root.title("Tic Tac Toe")
        frame = Frame(root)
        frame.pack()

        Button(
            frame,
            text='Show Help',
            command=self._help_callback).pack(fill=X)

        Button(
            frame,
            text='Play Game',
            command=self._play_callback).pack(fill=X)

        Button(
            frame,
            text='Quit',
            command=self._quit).pack(fill=X)

        scroll = Scrollbar(frame)
        console = Text(frame, height=4, width=50)
        scroll.pack(side=RIGHT, fill=Y)
        console.pack(side=LEFT, fill=Y)

        scroll.config(command=console.yview)
        console.config(yscrollcommand=scroll.set)

        self._root = root
        self._console = console

    def _quit(self):
        self._quit = True
        if self._client:
            self._client.quit()

    def _help_close(self):
        self._help_win.destroy()
        self._help_win = None

    def _help_callback(self):
        if self._help_win:
            return

        help_win = Toplevel(self._root)
        help_win.title("Help")

        help_text = "It's Tic Tac Toe. C'mon - you know the rules"

        Message(help_win, text=help_text).pack(fill=X)
        Button(help_win, text="Dismiss", command=self._help_close).pack(fill=X)
        self._help_win = help_win

    def _game_close(self):
        self._game_win.destroy()
        self._game_win = None

    def _play_callback(self):
        if self._game_win:
            return

        self._game = Game()
        self._finished = False

        game_win = Toplevel(self._root)
        game_win.title("Game")
        frame = Frame(game_win)

        # To allow resizing
        Grid.columnconfigure(game_win, 0, weight=1)
        Grid.rowconfigure(game_win, 0, weight=1)
        frame.grid(row=0,column=0,sticky=N + S + E + W)

        dim = self._game.dim()
        self._buttons = [[None for _ in range(dim)] for _ in range(dim)]

        for row,col in product(range(dim),range(dim)):
            b = StringVar()
            b.set(self._game.at(row+1,col+1))

            cmd = lambda r=row,c=col : self._play_and_refresh(r,c)

            Button(
                frame,
                textvariable=b,
                command=cmd).grid(row=row,column=col,sticky=N + S + E + W)

            self._buttons[row][col] = b

        # To allow resizing
        for i in range(dim):
            Grid.rowconfigure(frame, i, weight=1)
            Grid.columnconfigure(frame, i, weight=1)

        Button(game_win, text="Dismiss", command=self._game_close).grid(row=1,column=0)
        self._game_win = game_win

    def _play_and_refresh(self,row,col):
        if self._finished:
            return

        try:
            self._game.play(row+1,col+1)
        except GameError as e:
            self._console.insert(END, f"{e}\n")

        dim = self._game.dim()
        for r,c in product(range(dim),range(dim)):
            text = self._game.at(r+1,c+1)
            self._buttons[r][c].set(text)

        w = self._game.winner 
        if w is not None:
            self._finished = True
            if w is Game.DRAW:
                self._console.insert(END, f"The game was drawn\n")
            else:
                self._console.insert(END, f"The winner is {w}\n")

    async def run(self):
        self._quit = False
        while not self._quit:
            await sleep(0.5)
            self._root.update()
    
    async def run_client(self):
        if self._client:
            await self._client.run()

class Terminal(Ui):
    def __init__(self,network=False):
        self._game = Game()
        self._name = ""
        self._opponent = ""
        self._localturn = True
        self._client = Client() if network else None

    async def run_client(self):
        if self._client:
            await self._client.run()

    async def run(self):
        if self._client:
            self._name = await ainput("Enter user name: ")
            await self._client.send({"from":self._name,"cmd":"join"})
            while not self._opponent:
                msg = await self._client.recv()
                cmd = msg.get("cmd",None)
                if cmd == "join":
                    opponent = msg.get("from",None)
                    if opponent and opponent != self._name:
                        await self._client.send(
                            {
                                "to"   : opponent,
                                "from" : self._name,
                                "cmd"  : "req"
                            })

                elif cmd == "req" and msg.get("to",None) == self._name and not self._opponent:
                    self._opponent = msg.get("from")
                    await self._client.send({"to":self._opponent,"from":self._name,"cmd":"ack"})
                    
                elif cmd == "ack" and msg.get("to",None) == self._name and not self._opponent:
                    self._opponent = msg.get("from")

            print(f"Game is {self._name} vs {self._opponent}")
            self._localturn = (self._name > self._opponent)
            
        while not self._game.winner:
            while True:
                print(self._game)
                if self._localturn:
                    try:
                        row = await ainput("Which row? ")
                        row = int(row)
                        col = await ainput("Which column? ")
                        col = int(col)

                    except ValueError:
                        print(f"Row and Column should be numbers in the range 1-{self._game.dim()}.")
                        continue
                    if self._client:
                        await self._client.send({"from":self._name,"to":self._opponent,"cmd":"move","pos":(row,col)})
                else:
                    print(f"{self._opponent} is playing")
                    row,col = None,None
                    while (row,col) == (None,None):
                        msg = await self._client.recv()
                        if msg.get("cmd",None) == "move" and msg.get("to",None) == self._name and msg.get("from",None) == self._opponent:
                            row,col = msg.get("pos")

                try:
                    self._game.play(row,col)
                    if self._client:
                        self._localturn = not self._localturn
                    break
                except GameError as e:
                    print(f"Game error {e}",file=stderr)

        print(self._game)
        w = self._game.winner
        if w is Game.DRAW:
            print("The game was drawn")
        else:
            print(f"The winner was {w}")

        if self._client:
            await ainput("Press any key to quit")
            self._client.quit()
