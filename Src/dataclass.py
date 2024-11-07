# 28.10.24

from dataclasses import dataclass

@dataclass
class Position:
    x: int              # Absolute X position
    y: int              # Absolute Y position
    rel_x: int          # Relative X position on screen
    rel_y: int          # Relative Y position on screen
    level_block: int    # Current level block
    scroll_x: int

@dataclass
class Timer:
    hundreds: int
    tens: int
    ones: int

    @property
    def total(self) -> int:
        return self.hundreds * 100 + self.tens * 10 + self.ones
    
    @property
    def minutes(self) -> int:
        return self.total // 60  # Convert total seconds to minutes

    @property
    def seconds(self) -> int:
        return self.total % 60  # Get the remaining seconds after minutes

@dataclass
class LocalPlayer:
    position: Position
    pose: int
    direction: str
    jump_state: str
    speed_y: int
    grounded: bool
    starman_timer: int
    powerup_status: int
    hard_mode: bool 
    powerup_status_timer: int
    has_superball: bool  


@dataclass
class LandGame:
    current_world: int
    current_stage: int
    score: int
    lives: int
    coins: int
    timer: Timer
    in_game: bool
    game_over: bool
