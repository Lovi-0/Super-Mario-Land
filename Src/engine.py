# 28.10.24

import math
from typing import List, Dict


# External libraries
from pyboy import PyBoy


# Internal utilities
from .offset import Offset, EntityProperty
from .dataclass import Position, Timer, LocalPlayer, LandGame, Entity, Rect
from .enemy import ENEMY_TYPES


# Variable
SCALE = 3


def bcm_to_dec(value: int) -> int:
    return (value >> 4) * 10 + (value & 0x0F)

def create_rect(x: int, y: int, border: int) -> Rect:
    return Rect(x * SCALE, y * SCALE, border * SCALE, border * SCALE)

def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

class MarioLandMonitor:
    def __init__(self, pyboy_instance: PyBoy):
        self.pyboy = pyboy_instance
        self.game_wrapper = self.pyboy.game_wrapper
        self.memory = pyboy_instance.memory
        self.previous_state = None
        self.enemy_types = ENEMY_TYPES
    
    def _calculate_position(self) -> Position:
        #level_block = self.memory[Offset.LEVEL_BLOCK]
        rel_x = self.memory[Offset.MARIO_X_POS] - 16
        rel_y = self.memory[Offset.MARIO_Y_POS] - 20
        scroll_x = self.memory[Offset.SCROLL_X]

        # Calculate real X position
        #real_offset = (scroll_x - 7) % 16 if (scroll_x - 7) % 16 != 0 else 16
        #abs_x = (level_block * 16) + real_offset + rel_x

        return Position(
            x=rel_x,
            y=rel_y,
            scroll_x=scroll_x
        )

    def _read_mario_state(self) -> Dict:
        return {
            'direction': "Left" if self.memory[0xC20D] == 0x20 else "Right",
            'jump_state': {
                0x00: "Not Jumping",
                0x01: "Ascending",
                0x02: "Descending"
            }.get(self.memory[Offset.JUMP_STATE], "Unknown"),
            'y_speed': self.memory[Offset.Y_SPEED],
            'grounded': bool(self.memory[Offset.GROUNDED])
        }

    def _scan_enemy_table(self, mario_position: Position) -> List[Dict]:
        active_enemies = []
        
        for i in range(10):
            ptr_entity = Offset.ENTITY_LIST + (i * 0x10)
            entity = self.memory[ptr_entity]
            health = self.memory[ptr_entity + EntityProperty.HP]
            x_pos = self.memory[ptr_entity + EntityProperty.X_POS] - 9
            y_pos = self.memory[ptr_entity + EntityProperty.Y_POS] - 18

            # Calcola la distanza tra Mario e il nemico
            distance = calculate_distance(mario_position.x * SCALE, mario_position.y * SCALE, x_pos * SCALE, y_pos * SCALE)
            
            if entity == 255:
                continue

            if health == 0:
                continue
            
            active_enemies.append(Entity(
                type=self.enemy_types.get(entity, f"Unknown (0x{entity:02X})"),
                position=Position(x_pos, y_pos, None),
                rect=create_rect(x_pos, y_pos, 10),
                hp=health,
                pose=self.memory[ptr_entity + EntityProperty.POSE],
                distance=distance,
                collisione=(distance < 31)
            ))
            
        return active_enemies

    def _is_alive(self):

        # 58  -> Game over
        # 0   -> LandGame
        # 15  -> StartUp 
        # 1-4 -> Dead
        GAME_STATES_DEAD = (1, 3, 4, 60)
        TIMER_DEATH = 0x90

        if self.pyboy.memory[Offset.GAME_OVER] in GAME_STATES_DEAD:
            return False
    
        if self.pyboy.memory[Offset.POWERUP_STATUS_TIMER] == TIMER_DEATH:
            return False

        return True
    
    def get_game_state(self):
        mario_state = self._read_mario_state()
        mario_position = self._calculate_position()
        active_enemies = self._scan_enemy_table(mario_position)
        int_livesLeft = bcm_to_dec(self.pyboy.memory[0xDA15])

        local_player = LocalPlayer(
            position=mario_position,
            rect=create_rect(mario_position.x, mario_position.y, 16),
            pose=self.memory[Offset.MARIO_POSE],
            direction=mario_state['direction'],
            jump_state=mario_state['jump_state'],
            speed_y=mario_state['y_speed'],
            grounded=mario_state['grounded'],
            starman_timer=self.memory[Offset.STARMAN_TIMER],
            powerup_status=self.memory[Offset.POWERUP_STATUS],
            hard_mode=bool(self.memory[Offset.HARD_MODE_FLAG]),
            powerup_status_timer=self.memory[Offset.POWERUP_STATUS_TIMER],
            has_superball=bool(self.memory[Offset.HAS_SUPERBALL]),
        )

        # Create the Timer instance using hundreds, tens, and ones memory values
        timer = Timer(
            hundreds=self.memory[Offset.TIMER_HUNDREDS],
            tens=self.memory[Offset.TIMER_TENS],
            ones=self.memory[Offset.TIMER_ONES]
        )

        # Calculate the coins value
        coins = (self.memory[Offset.COINS] // 10) * 10 + (self.memory[Offset.COINS] % 10)

        land_game = LandGame(
            current_world=self.memory[Offset.CURRENT_WORLD],
            current_stage=self.memory[Offset.CURRENT_STAGE],
            score=self.game_wrapper.score,
            lives=int_livesLeft,
            coins=coins,
            timer=timer,
            in_game=self.memory[Offset.IN_GAME] != 57,
            game_over=self.memory[Offset.GAME_OVER] == 58,
            is_alive=self._is_alive(),
            is_startup=self.pyboy.memory[Offset.GAME_OVER] == 15
        )

        return local_player, land_game, active_enemies

    def print_state_changes(self, local_player: LocalPlayer, land_game: LandGame, active_enemies: List[Dict]):
        if self.previous_state is None:
            self.previous_state = (local_player, land_game, active_enemies)
            return
        
        prev_local_player, prev_land_game, prev_active_enemies = self.previous_state

        # Check changes in LocalPlayer state
        for field in LocalPlayer.__dataclass_fields__:
            old_val = getattr(prev_local_player, field)
            new_val = getattr(local_player, field)
            
            if old_val != new_val:
                if field == 'position':
                    print(f"Mario position: (abs: {new_val.position.x}, {new_val.position.y}) "
                          f"(rel: {new_val.position.rel_x}, {new_val.position.rel_y}) "
                          f"[block: {new_val.position.level_block}, scroll: {new_val.position.scroll_x}]")
                else:
                    print(f"Changed {field} from {old_val} to {new_val}")

        # Check changes in LandGame state
        for field in LandGame.__dataclass_fields__:
            old_val = getattr(prev_land_game, field)
            new_val = getattr(land_game, field)

            if old_val != new_val:
                if field == 'timer':
                    print(f"Timer changed to: {new_val.timer.total}")
                else:
                    print(f"Changed {field} in game state from {old_val} to {new_val}")

        # Check changes in active enemies
        disappeared = [e for e in prev_active_enemies if e not in active_enemies]
        appeared = [e for e in active_enemies if e not in prev_active_enemies]

        if disappeared or appeared:
            print("\nEnemy changes:")
            for enemy in disappeared:
                print(f"- Enemy removed: {enemy['type']} at ({enemy['pos_x']}, {enemy['pos_y']})")
            for enemy in appeared:
                print(f"+ Enemy spawned: {enemy['type']} at ({enemy['pos_x']}, {enemy['pos_y']})")

        # Update previous state
        self.previous_state = (local_player, land_game, active_enemies)


