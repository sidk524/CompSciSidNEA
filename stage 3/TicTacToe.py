from Ui import Gui, Terminal, SGui
from sys import argv

def usage():   
    print(f"""
Usage: {argv[0]} [g | t | s]
g : play with the GUI
s : play with the Simple GUI
t : play with the Terminal""")
    quit()

if __name__ == "__main__":
    if len(argv) != 2:
        usage()
    elif argv[1] == 'g':
        ui = Gui()
    elif argv[1] == 's':
        ui = SGui()
    elif argv[1] == 't':
        ui = Terminal()
    else:
        usage()

    ui.run()
