import UIclasses

uiType = input("Welcome to CompSciMazeMaster! Enter 't' to run in the terminal, or 'g' to run in the GUI: ").lower()

while uiType != "t" and uiType != "g":
    uiType = input("Please enter a valid option. Enter 't' to run in the terminal, or 'g' to run in the GUI: ").lower()

if uiType == "t":
    UI = UIclasses.TerminalUI()
elif uiType == "g":
    UI = UIclasses.GUI()

UI.run()

