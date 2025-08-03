from typing import Optional
from blessed import Terminal
from collections import deque
from game_settings import GameSettings
import time

class TicTacToe:
    def __init__(self, settings: GameSettings):
        self.term = Terminal()
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'
        self.move_history = deque()
        self.game_over = False
        self.winner = None
        self.selected_cell = 0
        self.last_board_state = None
        self.needs_redraw = True
        self.settings = settings
        self.turn_start_time = None
        self.time_remaining = None
        
    def clear_screen(self):
        print(self.term.clear)
        
    def draw_header(self):
        header_lines = [
            "╔" + "═" * 56 + "╗",
            "║" + " " * 16 + "TIC-TAC-TOE GAME" + " " * 24 + "║"
        ]
        
        if self.settings.decay_rule_enabled:
            header_lines.append("║" + " " * 8 + "Special Rule: First move disappears after 6 moves" + " " * 7 + "║")
        else:
            header_lines.append("║" + " " * 18 + "Classic Tic-Tac-Toe" + " " * 19 + "║")
            
        header_lines.append("╠" + "═" * 56 + "╣")
        
        for line in header_lines:
            print(self.term.center(self.term.bold + self.term.cyan + line + self.term.normal))
        print()
        
    def draw_status(self):
        player_color = self.term.red if self.current_player == 'X' else self.term.blue
        
        status_parts = [f"Current Player: {player_color}{self.current_player}{self.term.normal}"]
        
        if self.settings.decay_rule_enabled:
            status_parts.append(f"Total Moves: {len(self.move_history)}")
        
        if self.settings.time_limit_enabled and self.settings.time_limit_seconds > 0 and not self.game_over:
            if self.time_remaining is not None:
                time_color = self.term.red if self.time_remaining <= 3 else self.term.yellow if self.time_remaining <= 5 else self.term.green
                status_parts.append(f"Time: {time_color}{self.time_remaining:.1f}s{self.term.normal}")
        
        status_line = "    ".join(status_parts)
        print(self.term.center(self.term.bold + status_line + self.term.normal))
        print()
        
    def draw_board(self):
        current_state = (self.board[:], self.current_player, self.selected_cell, self.game_over, self.winner, self.time_remaining)
        
        if not self.needs_redraw and self.last_board_state == current_state:
            return True
            
        self.clear_screen()
        self.draw_header()
        self.update_time_remaining()
        self.draw_status()
        
        board_lines = []
        
        for row in range(3):
            line = "║"
            for col in range(3):
                cell_index = row * 3 + col
                cell_content = self.board[cell_index]
                
                if cell_index == self.selected_cell and cell_content == ' ':
                    cell_display = self.term.on_yellow + self.term.black + f"  {cell_index + 1}  " + self.term.normal
                elif cell_content == 'X':
                    cell_display = self.term.red + self.term.bold + "  X  " + self.term.normal
                elif cell_content == 'O':
                    cell_display = self.term.blue + self.term.bold + "  O  " + self.term.normal
                else:
                    cell_display = f"  {cell_index + 1}  "
                
                line += cell_display
                if col < 2:
                    line += "│"
            line += "║"
            board_lines.append(line)
            
            if row < 2:
                board_lines.append("║" + "─────┼─────┼─────" + "║")
        
        frame_top = "╔" + "═" * 17 + "╗"
        frame_bottom = "╚" + "═" * 17 + "╝"
        
        print(self.term.center(self.term.bold + self.term.white + frame_top + self.term.normal))
        for line in board_lines:
            print(self.term.center(self.term.bold + self.term.white + line + self.term.normal))
        print(self.term.center(self.term.bold + self.term.white + frame_bottom + self.term.normal))
        
        print()
        self.draw_controls()
        
        if self.game_over:
            self.draw_game_over()
        
        self.last_board_state = current_state
        self.needs_redraw = False
        return True
    
    def draw_controls(self):
        controls_box = [
            "╔" + "═" * 54 + "╗",
            "║" + " " * 20 + "CONTROLS" + " " * 26 + "║",
            "╠" + "═" * 54 + "╣",
            "║  Keyboard: Arrow keys/WASD to navigate               ║",
            "║  Enter/Space: Select highlighted cell                ║",
            "║  Numbers 1-9: Direct cell selection                  ║",
            "║  Q: Quit game                                        ║",
            "╚" + "═" * 54 + "╝"
        ]
        
        for line in controls_box:
            print(self.term.center(self.term.green + line + self.term.normal))
            
    def draw_game_over(self):
        print()
        if self.winner:
            color = self.term.red if self.winner == 'X' else self.term.blue
            winner_box = [
                "╔" + "═" * 30 + "╗",
                "║" + " " * 30 + "║",
                "║" + f"    PLAYER {self.winner} WINS!".center(30) + "║",
                "║" + " " * 30 + "║",
                "╚" + "═" * 30 + "╝"
            ]
        else:
            color = self.term.yellow
            winner_box = [
                "╔" + "═" * 30 + "╗",
                "║" + " " * 30 + "║",
                "║" + "        IT'S A TIE!".center(30) + "║",
                "║" + " " * 30 + "║",
                "╚" + "═" * 30 + "╝"
            ]
            
        for line in winner_box:
            print(self.term.center(self.term.bold + color + line + self.term.normal))
        
        print()
        print(self.term.center("Press any key to play again, or 'q' to quit"))
    
    def update_time_remaining(self):
        if not self.settings.time_limit_enabled or self.settings.time_limit_seconds == 0 or self.game_over:
            return
            
        if self.turn_start_time is None:
            self.start_turn_timer()
        else:
            elapsed = time.time() - self.turn_start_time
            self.time_remaining = max(0, self.settings.time_limit_seconds - elapsed)
            
            if self.time_remaining <= 0:
                self.handle_timeout()
    
    def start_turn_timer(self):
        if self.settings.time_limit_enabled and self.settings.time_limit_seconds > 0:
            self.turn_start_time = time.time()
            self.time_remaining = self.settings.time_limit_seconds
    
    def handle_timeout(self):
        self.winner = 'O' if self.current_player == 'X' else 'X'
        self.game_over = True
        self.needs_redraw = True
        
    def check_winner(self) -> Optional[str]:
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        
        for combo in winning_combinations:
            if (self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] and 
                self.board[combo[0]] != ' '):
                return self.board[combo[0]]
        
        return None
    
    def is_board_full(self) -> bool:
        return ' ' not in self.board
    
    def make_move(self, position: int) -> bool:
        if position < 0 or position > 8 or self.board[position] != ' ':
            return False
        
        self.board[position] = self.current_player
        self.move_history.append((position, self.current_player))
        
        if self.settings.decay_rule_enabled and len(self.move_history) > 6:
            old_position, old_player = self.move_history.popleft()
            self.board[old_position] = ' '
        
        self.winner = self.check_winner()
        if self.winner or self.is_board_full():
            self.game_over = True
        else:
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            self.start_turn_timer()
        
        self.needs_redraw = True
        return True
    
    def handle_keyboard_input(self, key):
        if key.lower() == 'q':
            return False
        
        if self.game_over:
            if key:
                self.reset_game()
            return True
        
        old_selected = self.selected_cell
        
        if key.name == 'KEY_UP' or key.lower() == 'w':
            self.selected_cell = max(0, self.selected_cell - 3)
        elif key.name == 'KEY_DOWN' or key.lower() == 's':
            self.selected_cell = min(8, self.selected_cell + 3)
        elif key.name == 'KEY_LEFT' or key.lower() == 'a':
            self.selected_cell = max(0, self.selected_cell - 1)
        elif key.name == 'KEY_RIGHT' or key.lower() == 'd':
            self.selected_cell = min(8, self.selected_cell + 1)
        elif key.name == 'KEY_ENTER' or key == ' ':
            self.make_move(self.selected_cell)
        elif key.isdigit():
            num = int(key) - 1
            if 0 <= num <= 8:
                self.make_move(num)
        
        if old_selected != self.selected_cell:
            self.needs_redraw = True
        
        return True
    
    def reset_game(self):
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'
        self.move_history = deque()
        self.game_over = False
        self.winner = None
        self.selected_cell = 0
        self.needs_redraw = True
        self.turn_start_time = None
        self.time_remaining = None
        self.start_turn_timer()
    
    def run(self):
        try:
            with self.term.cbreak(), self.term.hidden_cursor():
                self.start_turn_timer()
                self.draw_board()
                
                while True:
                    timeout = 0.1 if self.settings.time_limit_enabled and self.settings.time_limit_seconds > 0 else 0.5
                    key = self.term.inkey(timeout=timeout)
                    
                    if self.settings.time_limit_enabled and self.settings.time_limit_seconds > 0 and not self.game_over:
                        self.update_time_remaining()
                        if self.time_remaining <= 0:
                            self.needs_redraw = True
                    
                    if key:
                        if not self.handle_keyboard_input(key):
                            break
                    
                    if self.needs_redraw:
                        if not self.draw_board():
                            return
        
        except KeyboardInterrupt:
            pass
        finally:
            self.clear_screen()
            print(self.term.center(self.term.bold + self.term.green + "Thanks for playing!"))
            print()
            print(self.term.center(self.term.italic + "Made with love" + self.term.normal))
