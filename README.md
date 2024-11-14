
# Super Mario Land Monitor and AI

<img src="logo.png" alt="logo" align="middle">

This Python project allows monitoring and interacting with the game state of the classic Game Boy game "Super Mario Land" using the PyBoy emulator. It also incorporates an AI agent for training and reinforcement learning to play the game.

The `MarioLandMonitor` class is responsible for reading and parsing the game's memory to extract information about Mario's state, the game timer, collected coins, and active enemies. The training component uses a DQN (Deep Q-Network) agent to learn how to play the game.

## Features
- **Game State Monitoring**:
  - Tracks Mario's position, direction, jump state, speed, and grounded status.
  - Monitors game-wide data like the current world/stage, score, lives, coins, and timer.
  - Scans for active enemies and their properties (type, health, position, pose, timer).
  - Detects and prints changes in the game state between updates.

- **AI Training**:
  - Uses a Deep Q-Network (DQN) agent to interact with the game and learn optimal actions.
  - Tracks performance metrics such as total reward and epsilon (exploration rate) over episodes.
  - Saves model checkpoints periodically during training.

- **Visualization**:
  - Displays the current game screen using PyBoy and visualizes Mario’s and enemy’s positions on the screen.
  - Draws red and yellow dots to mark Mario’s and enemies' positions, respectively.
  - Updates the display with a rotated and scaled screen buffer for better visualization.

## Prerequisites
- Python 3.7 or later
- PyBoy library
- pygame for rendering
- rich for console output and monitoring

## How it Works

### Game State Monitoring
The `MarioLandMonitor` class uses the PyBoy emulator to access the game's memory and extract relevant information. The `get_game_state()` method reads the following data:

- Mario's position, direction, jump state, vertical speed, and grounded status.
- Game-wide data like the current world/stage, score, lives, coins, and timer.
- A list of active enemies, including their type, health, position, pose, and timer.

The `print_state_changes()` method compares the current game state with the previous state and prints any changes that have occurred, such as:

- Mario's position, direction, and jump state.
- Changes in game-wide data like the score, lives, and timer.
- Enemies that have appeared or disappeared from the screen.

### AI Training
The AI training is based on a DQN (Deep Q-Network) agent. During training, the agent interacts with the game environment, observing the current state, taking actions, and receiving rewards. The agent learns the optimal policy over time by minimizing the loss between predicted Q-values and target Q-values.

Key components include:

- **Agent**: The `EnhancedDQNAgent` class handles decision-making, experience replay, and model updates.
- **Model**: The model is a neural network used to approximate the Q-values for different actions.
- **Training Loop**: The agent interacts with the game environment over multiple episodes, saving the model periodically.

### Visualization
The visualization part uses `pygame` to render the game screen. The `draw_game_state` function handles rendering the current game state on the screen, including:

- Scaling and rotating the PyBoy screen buffer for better display.
- Drawing Mario's position as a red circle and enemies' positions as yellow circles.
- Drawing rectangles around Mario and enemies to indicate their boundaries.
- Displaying collision status and other relevant information for each enemy.

## Documentation
For more details on the game's memory map and how the data is accessed, refer to the official documentation:

- [Super Mario Land RAM Map](https://datacrystal.tcrf.net/wiki/Super_Mario_Land/RAM_map)

## Contributing
If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request. Contributions are welcome!

## License
This project is licensed under the [MIT License](LICENSE).
