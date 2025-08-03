
from opening_screen import OpeningScreen
from game import TicTacToe

def main():
    print("Terminal Tic-Tac-Toe")
    print("Loading...")
    
    opening_screen = OpeningScreen()
    settings = opening_screen.run()
    
    if settings is None:
        print("Thanks for playing!")
        return
    
    game = TicTacToe(settings)
    
    try:
        game.run()
    finally:
        pass

if __name__ == "__main__":
    main()