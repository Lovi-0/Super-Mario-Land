# 30.10.24

import os
import time

# External libraries
from pyboy import PyBoy
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box 


# Internal utilities
from Src.engine import MarioLandMonitor


def main():
    pyboy = PyBoy(os.path.join('rom', 'mario.gb'))
    monitor = MarioLandMonitor(pyboy)
    console = Console()

    try:
        while True:
            pyboy.tick()

            # Fetch the game state
            localPlayer, landGame, entityList = monitor.get_game_state()

            # Use a rich panel to display the game state title and description
            console.print(Panel(f"[bold blue]Game State[/bold blue] - World {landGame.current_world}, Stage {landGame.current_stage}", style="bold green"))

            # Create a table to display local player details
            player_table = Table(title="Local Player Info", box=box.ROUNDED)
            player_table.add_column("Attribute", justify="center", style="cyan", no_wrap=True)
            player_table.add_column("Value", justify="center", style="magenta")
            
            # Add rows with player data
            player_table.add_row("Position (X, Y)", f"({localPlayer.position.x}, {localPlayer.position.y})")
            player_table.add_row("Pose", str(localPlayer.pose))
            player_table.add_row("Direction", localPlayer.direction)
            player_table.add_row("Jump State", localPlayer.jump_state)
            player_table.add_row("Speed Y", str(localPlayer.speed_y))
            player_table.add_row("Grounded", str(localPlayer.grounded))
            player_table.add_row("Starman Timer", str(localPlayer.starman_timer))
            player_table.add_row("Powerup Status", str(localPlayer.powerup_status))
            player_table.add_row("Hard Mode", str(localPlayer.hard_mode))
            player_table.add_row("Powerup Status Timer", str(localPlayer.powerup_status_timer))
            player_table.add_row("Has Superball", str(localPlayer.has_superball))
            console.print(player_table)

            # Display Land Game Info in a rich panel
            land_game_info = f"Score: {landGame.score} | Lives: {landGame.lives} | Coins: {landGame.coins} | Timer: {landGame.timer.minutes}:{landGame.timer.seconds:02d}"
            console.print(Panel(land_game_info, title="Land Game Info", style="bold yellow"))

            # Display entity list
            if entityList:
                console.print(Panel("[bold green]Entities in Game[/bold green]"))
                entity_table = Table(title="Active Enemies", box=box.ROUNDED)
                entity_table.add_column("Enemy Type", justify="center", style="cyan", no_wrap=True)
                entity_table.add_column("HP", justify="center", style="magenta")
                entity_table.add_column("Pos X", justify="center", style="cyan")
                entity_table.add_column("Pos Y", justify="center", style="magenta")
                entity_table.add_column("Pose", justify="center", style="green")
                entity_table.add_column("Timer", justify="center", style="yellow")

                for enemy in entityList:
                    entity_table.add_row(
                        enemy['type'],
                        str(enemy['hp']),
                        str(enemy['pos_x']),
                        str(enemy['pos_y']),
                        str(enemy['pose']),
                        str(enemy['timer'])
                    )
                console.print(entity_table)

            else:
                console.print("[bold red]No enemies detected[/bold red]", style="bold red")

            time.sleep(0.01)
            os.system('cls')

    except KeyboardInterrupt:
        console.print("\n[bold red]Stopped ...[/bold red]", style="bold red")
        
    finally:
        pyboy.stop()


if __name__ == "__main__":
    main()
