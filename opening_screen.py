from blessed import Terminal
from game_settings import GameSettings

class OpeningScreen:
    def __init__(self):
        self.term = Terminal()
        self.settings = GameSettings()
        self.selected_option = 0
        self.options = [
            ("Time Limit", "time_limit_enabled", "toggle"),
            ("Time Duration", "time_limit_seconds", "time_selector"),
            ("Decay Rule (6-move disappear)", "decay_rule_enabled", "toggle"),
            ("Start Game", "start", "action")
        ]
    
    def clear_screen(self):
        print(self.term.clear)
    
    def draw_title(self):
        title_lines = [
            "╔" + "═" * 50 + "╗",
            "║" + " " * 50 + "║",
            "║" + "TERMINAL TIC-TAC-TOE".center(50) + "║",
            "║" + " " * 50 + "║",
            "╚" + "═" * 50 + "╝"
        ]
        
        for line in title_lines:
            print(self.term.center(self.term.bold + self.term.cyan + line + self.term.normal))
        print()
    
    def draw_settings(self):
        settings_box = [
            "╔" + "═" * 60 + "╗",
            "║" + " " * 23 + "GAME SETTINGS" + " " * 24 + "║",
            "╠" + "═" * 60 + "╣"
        ]
        
        for i, (name, attr, option_type) in enumerate(self.options):
            if i == len(self.options) - 1:
                settings_box.append("╠" + "═" * 60 + "╣")
            
            prefix = "► " if i == self.selected_option else "  "
            
            if option_type == "action":
                line = f"║  {prefix}{name.center(54)}  ║"
            elif option_type == "toggle":
                current_value = getattr(self.settings, attr)
                status = "ON " if current_value else "OFF"
                line = f"║  {prefix}{name:<40} [{status}]     ║"
            elif option_type == "time_selector":
                if not self.settings.time_limit_enabled:
                    status = "DISABLED"
                    line = f"║  {prefix}{name:<40} [{status}] ║"
                else:
                    time_display = self.settings.get_time_limit_display()
                    arrows = "◄ ► " if i == self.selected_option else "    "
                    line = f"║  {prefix}{name:<35} {arrows}[{time_display}]  ║"
            
            settings_box.append(line)
        
        settings_box.append("╚" + "═" * 60 + "╝")
        
        for line in settings_box:
            color = self.term.yellow if "►" in line else self.term.white
            print(self.term.center(color + line + self.term.normal))
        print()
    
    def draw_controls(self):
        controls = [
            "╔" + "═" * 50 + "╗",
            "║" + " " * 19 + "CONTROLS" + " " * 21 + "║",
            "╠" + "═" * 50 + "╣",
            "║  ↑/↓ or W/S: Navigate options              ║",
            "║  Enter/Space: Toggle setting               ║",
            "║  ←/→ or A/D: Change time duration          ║",
            "║  Q: Quit                                   ║",
            "╚" + "═" * 50 + "╝"
        ]
        
        for line in controls:
            print(self.term.center(self.term.green + line + self.term.normal))
    
    def draw(self):
        self.clear_screen()
        self.draw_title()
        self.draw_settings()
        self.draw_controls()
        print()
        print(self.term.center(self.term.italic + "Made with love" + self.term.normal))
    
    def handle_input(self, key):
        if key.lower() == 'q':
            return False, None
        
        if key.name == 'KEY_UP' or key.lower() == 'w':
            self.selected_option = max(0, self.selected_option - 1)
        elif key.name == 'KEY_DOWN' or key.lower() == 's':
            self.selected_option = min(len(self.options) - 1, self.selected_option + 1)
        elif key.name == 'KEY_ENTER' or key == ' ':
            option_name, attr, option_type = self.options[self.selected_option]
            
            if option_type == "action":
                return True, self.settings
            elif option_type == "toggle":
                current_value = getattr(self.settings, attr)
                setattr(self.settings, attr, not current_value)
        elif key.name == 'KEY_LEFT' or key.lower() == 'a':
            self.handle_time_adjustment(-1)
        elif key.name == 'KEY_RIGHT' or key.lower() == 'd':
            self.handle_time_adjustment(1)
        
        return None, None
    
    def handle_time_adjustment(self, direction):
        option_name, attr, option_type = self.options[self.selected_option]
        
        if option_type == "time_selector" and self.settings.time_limit_enabled:
            time_options = self.settings.get_time_limit_options()
            current_index = time_options.index(self.settings.time_limit_seconds)
            
            if direction == -1:  # Left arrow
                new_index = max(0, current_index - 1)
            else:  # Right arrow
                new_index = min(len(time_options) - 1, current_index + 1)
            
            self.settings.time_limit_seconds = time_options[new_index]
    
    def run(self):
        try:
            with self.term.cbreak(), self.term.hidden_cursor():
                while True:
                    self.draw()
                    key = self.term.inkey()
                    
                    if key:
                        result, settings = self.handle_input(key)
                        if result is False:
                            return None
                        elif result is True:
                            return settings
        
        except KeyboardInterrupt:
            return None
