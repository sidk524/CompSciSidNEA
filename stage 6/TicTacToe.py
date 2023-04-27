from Ui import Gui, Terminal
from sys import argv
from asyncio import create_task, run, gather, FIRST_COMPLETED

def usage():   
    print(f"""
Usage: {argv[0]} [g[n] | t[n]]
g  : play with the GUI
t  : play with the Terminal
tn : play with the Terminal over the network
gn : play with the GUI over the network""")
    quit()

async def main():

    if len(argv) != 2:
        usage()

    network = 'n' in argv[1]

    if argv[1] in ('g','gn'):
        ui = Gui(network)
    elif argv[1] in ('t','tn'):
        ui = Terminal(network)
    else:
        usage()

    tasks = [create_task(ui.run())]

    if network:
        tasks.append(create_task(ui.run_client()))

    await gather(*tasks)

if __name__ == "__main__":
    run(main())
