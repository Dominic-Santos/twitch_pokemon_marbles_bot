import tkinter

from main_menu.MainMenu import MainMenu


def main():
    app = tkinter.Tk()
    menu = MainMenu(app)
    menu.run()


if __name__ == "__main__":
    main()
