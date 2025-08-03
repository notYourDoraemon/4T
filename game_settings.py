class GameSettings:
    def __init__(self):
        self.time_limit_enabled = False
        self.time_limit_seconds = 10
        self.decay_rule_enabled = True
        
    def get_time_limit_options(self):
        return [2, 5, 10, 15, 20, 30, 0]  # 0 means no timeout
    
    def get_time_limit_display(self):
        if self.time_limit_seconds == 0:
            return "No Timeout"
        return f"{self.time_limit_seconds}s"
