# 28.10.24

from dataclasses import dataclass


@dataclass
class Position:
    x: int              # Absolute X position
    y: int              # Absolute Y position
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
class Rect:
    left: int
    top: int
    width: int
    height: int

@dataclass
class LocalPlayer:
    position: Position
    rect: Rect
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
class Entity:
    type: str
    position: Position
    rect: Rect
    hp: int
    pose: int
    distance: float
    collisione: bool


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
    is_alive: bool
    is_startup: bool
