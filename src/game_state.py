class GameState:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.game_over = False
        self.paused = False
        self.level = 1
        self.times_reached_top = 0
        self.high_score = 0
        self.show_instructions = True
        self.won = False
