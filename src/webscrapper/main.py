from webscrapper.terminal.main import main as terminal_main
from webscrapper.window.main import main as window_main

START_APP = "WINDOW"


def main():
    global START_APP
    while True:
        if START_APP == "WINDOW":
            START_APP = window_main()
        elif START_APP == "TERMINAL":
            START_APP = terminal_main()
        else:
            return


if __name__ == "__main__":
    main()
