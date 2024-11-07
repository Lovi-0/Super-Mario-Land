# 28.10.24

class EntityProperty:
    TYPE = 0x0
    HP = 0x1
    Y_POS = 0x2
    X_POS = 0x3
    POSE = 0x6
    TIMER = 0x8

class Offset:

    # Mario's Position and Game Information
    LEVEL_BLOCK = 0xC205
    MARIO_X_POS = 0xC202
    MARIO_Y_POS = 0xC201
    SCROLL_X = 0xFF43
    MARIO_POSE = 0xC203
    JUMP_STATE = 0xC207
    Y_SPEED = 0xC208
    GROUNDED = 0xC20A

    # Game State Offsets
    SCORE = 0x9820       # 6 bytes for score (0x9820 - 0x9825)
    LIVES = 0xDA15
    CURRENT_WORLD = 0x982C
    CURRENT_STAGE = 0x982E
    IN_GAME = 0xC0A4
    STARMAN_TIMER = 0x9830
    GAME_OVER = 0xFFB3

    # Coin Counters
    COINS = 0xFFFA
    COINS_TENS = 0x9829
    COINS_ONES = 0x982A

    # Timer Display
    TIMER_HUNDREDS = 0x9831
    TIMER_TENS = 0x9832
    TIMER_ONES = 0x9833

    # Entity Information
    ENTITY_LIST = 0xD100

    # Other offsets
    POWERUP_STATUS = 0xFF99
    HARD_MODE_FLAG = 0xFF9A
    POWERUP_STATUS_TIMER = 0xFFA6
    HAS_SUPERBALL = 0xFFB5
    AUDIO_CHANNEL = 0xFFD7
    PROCESSED_OBJECT_TYPE = 0xFFFB
