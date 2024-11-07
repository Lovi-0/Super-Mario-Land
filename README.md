
<img src="logo.png" alt="logo" align="middle">

This is a Python project that monitors the game state of the classic Game Boy game "Super Mario Land" using the PyBoy emulator. The `MarioLandMonitor` class is responsible for reading and parsing the game's memory to extract information about Mario's state, the game timer, collected coins, and active enemies.

## Features
- Tracks Mario's position, direction, jump state, speed, and grounded status
- Monitors game-wide data like the current world/stage, score, lives, coins, and timer
- Scans for active enemies and their properties (type, health, position, pose, timer)
- Detects and prints changes in the game state between updates

## Prerequisites
- Python 3.7 or later
- PyBoy library and rich

## Usage
1. Clone the repository:

   ```
   git clone https://github.com/your-username/mario-land-monitor.git
   ```

2. Navigate to the project directory:

   ```
   cd mario-land-monitor
   ```

3. Place the Super Mario Land ROM file in the `rom` directory.

4. Run the main script:

   ```
   python run.py
   ```

   This will start the game state monitor. The console will display the current game state, including Mario's status, the game timer, collected coins, and active enemies. The output will update every frame.

5. Press `Ctrl+C` to stop the monitor.

## How it Works
The `MarioLandMonitor` class uses the PyBoy emulator to access the game's memory and extract relevant information. The `get_game_state()` method reads the following data:

- Mario's position, direction, jump state, vertical speed, and grounded status
- Game-wide data like the current world/stage, score, lives, coins, and timer
- A list of active enemies, including their type, health, position, pose, and timer

The `print_state_changes()` method compares the current game state with the previous state and prints any changes that have occurred, such as:

- Mario's position, direction, and jump state
- Changes in game-wide data like the score, lives, and timer
- Enemies that have appeared or disappeared from the screen

This allows the user to monitor the game's progress and events in real-time.

The `Offset` class and `EntityProperty` class define the memory addresses and offsets used to access the game's data, while the `ENEMY_TYPES` dictionary in the `enemy.py` file maps enemy type codes to their respective names.


## Documentation
https://datacrystal.tcrf.net/wiki/Super_Mario_Land/RAM_map


## Contributing
If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request. Contributions are welcome!

## License
This project is licensed under the [MIT License](LICENSE).
