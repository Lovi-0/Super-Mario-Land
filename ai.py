import os
import cv2
import gym
import sys
import time
import numpy as np
from pyboy import PyBoy
from pyboy.utils import WindowEvent

from Src.Engine.engine import MarioLandMonitor
from Src.Engine.dataclass import LocalPlayer, Entity
from Src.model import EnhancedDQNAgent


emulate_speed = 20


class MarioEnvironment(gym.Env):
    def __init__(self, rom_path):
        super().__init__()
        self.rom_path = rom_path
        self.pyboy = PyBoy(rom_path, window="SDL2", debug=False)
        self.monitor = MarioLandMonitor(self.pyboy)
        self.pyboy.set_emulation_speed(emulate_speed)
        
        self.action_space = gym.spaces.Discrete(5)
        #self.observation_space = gym.spaces.Box(low=0, high=255, shape=(84, 84, 1), dtype=np.uint8)

        # Aumentiamo lo state space per includere:
        # - Frame processato (84x84x1)
        # - Informazioni del giocatore (9 features)
        # - Informazioni dei nemici (5 features per nemico, max 10 nemici)
        self.observation_space = gym.spaces.Dict({
            'image': gym.spaces.Box(low=0, high=255, shape=(84, 84, 1), dtype=np.uint8),
            'player_state': gym.spaces.Box(low=-np.inf, high=np.inf, shape=(10,), dtype=np.float32),
            'enemies_state': gym.spaces.Box(low=-np.inf, high=np.inf, shape=(11, 10), dtype=np.float32)
        })
        
        self.screen_dims = self.pyboy.screen.raw_buffer_dims
        self.inactivity_episodes = 0
        self.consecutive_stuck_episodes = 0
        self.long_jump_mode = False
        
        self.actions = {
            0: [],  # No action
            1: [(WindowEvent.PRESS_ARROW_RIGHT, None)],  # Continuous right movement
            2: [(WindowEvent.PRESS_ARROW_LEFT, None)],   # Continuous left movement
            3: [(WindowEvent.PRESS_BUTTON_A, WindowEvent.RELEASE_BUTTON_A)],  # Normal jump
            4: [(WindowEvent.PRESS_ARROW_RIGHT, None), (WindowEvent.PRESS_BUTTON_A, WindowEvent.RELEASE_BUTTON_A)]  # Jump + Right
        }
        
        self.last_position = 0
        self.last_score = 0
        self.stuck_counter = 0
        self.max_steps_per_level = 2000
        self.current_steps = 0
        self.was_alive = True

    def process_player_state(self, player: LocalPlayer):
        """Converte lo stato del giocatore in un array numpy"""
        return np.array([
            player.position.x,
            player.position.y,
            player.rect.left,
            player.rect.top,
            player.rect.width,
            player.rect.height,
            1.0 if player.direction == 'Right' else 0.0,
            1.0 if player.jump_state == 'Jumping' else 0.0,
            player.grounded,
            player.starman_timer
        ], dtype=np.float32)
    
    def process_enemies_state(self, enemies):
        """Converte lo stato dei nemici in un array numpy"""
        enemy_array = np.zeros((10, 11), dtype=np.float32)  # Max 5 nemici, 5 features per nemico
        
        for i, enemy in enumerate(enemies[:10]):  # Limitiamo a 5 nemici
            enemy: Entity = enemy

            enemy_array[i] = [
                enemy.i_type,
                enemy.position.x,
                enemy.position.y,
                enemy.rect.left,
                enemy.rect.top,
                enemy.rect.width,
                enemy.rect.height,
                enemy.hp,
                enemy.pose,
                enemy.distance,
                enemy.collisione
            ]
            
        return enemy_array

    def get_state(self, player, enemies):
        """Combina tutti gli stati in un dizionario"""
        return {
            'image': self.preprocess_frame(),
            'player_state': self.process_player_state(player),
            'enemies_state': self.process_enemies_state(enemies)
        }
    
    def _init_game(self):
        """Inizializza il gioco solo se siamo nella schermata iniziale"""
        if self.pyboy.memory[0xFFB3] == 15:  # Siamo nella schermata iniziale
            self.pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
            self.pyboy.tick()
            self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
            
            # Aspetta che il gioco inizi effettivamente
            for _ in range(60):
                self.pyboy.tick()

    def preprocess_frame(self):
        screen = np.frombuffer(self.pyboy.screen.raw_buffer, dtype=np.uint8).reshape(*self.screen_dims, 4)
        gray = screen[:, :, 0]
        resized = cv2.resize(gray, (84, 84), interpolation=cv2.INTER_AREA)
        return resized.reshape(84, 84, 1) / 255.0
        
    def is_alive(self):
        GAME_STATES_DEAD = (1, 3, 4, 60)
        TIMER_DEATH = 0x90

        if self.pyboy.memory[0xFFB3] in GAME_STATES_DEAD:
            return False
    
        if self.pyboy.memory[0xFFA6] == TIMER_DEATH:
            return False

        return True
        
    def calculate_danger_reward(self, player, enemies):
        """Calcola reward basato sulla vicinanza ai nemici"""
        danger_reward = 0
        player_x = player.position.x
        player_y = player.position.y
        
        for enemy in enemies:
            enemy: Entity = enemy
            distance = enemy.distance
            
            if distance < 30:  # Nemico molto vicino
                danger_reward -= 5

            elif distance < 45:  # Nemico abbastanza vicino
                danger_reward -= 2

            elif enemy.collisione:
                danger_reward -= 100
            
            # Bonus per evitare nemici saltando
            if player.jump_state == 'Jumping' and distance < 40:
                danger_reward += 3
                
        return danger_reward
    
    def step(self, action):
        self._init_game()
        self.current_steps += 1
        localPlayer, landGame, entityList = self.monitor.get_game_state()
        
        # Gestione speciale del salto in modalità long_jump
        if self.long_jump_mode and action in [3, 4]:
            # Tieni premuto A più a lungo per salti più lunghi
            for _ in range(20):  # Aumentato da 12 a 20 frames
                if not self.is_alive():
                    break
                self.pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
                if action == 4:  # Se è un salto con movimento, mantieni premuto anche destra
                    self.pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
                self.pyboy.tick()
            self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)
        else:
            # Esegui l'azione normalmente
            for press_event, release_event in self.actions[action]:
                self.pyboy.send_input(press_event)
                self.pyboy.tick()
                if release_event:
                    self.pyboy.send_input(release_event)
        
        # Rilascia i tasti solo se l'azione non è di movimento continuo
        if action not in [1, 2]:
            self.pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
            self.pyboy.send_input(WindowEvent.RELEASE_ARROW_LEFT)
        
        # Ottieni nuovo stato
        mario_x = localPlayer.position.x
        mario_y = localPlayer.position.y
        score = self.pyboy.game_wrapper.score
        lives = landGame.lives
        
        # Calcola reward con valori più bilanciati
        reward = 0
        done = False
        x_progress = mario_x - self.last_position
        
        # Controlla se Mario è fermo
        if abs(x_progress) < 1:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
            
        # Penalità per inattività
        if self.stuck_counter > 600:
            reward -= 500
            self.inactivity_episodes += 1
            self.consecutive_stuck_episodes += 1
            print(f"Episode terminated due to inactivity! (Stuck episodes: {self.consecutive_stuck_episodes})")
            
            # Attiva la modalità long jump se troppi episodi consecutivi bloccati
            if self.consecutive_stuck_episodes >= 3:
                self.long_jump_mode = True
                print("Activating long jump mode to overcome obstacles!")
        else:
            # Se completiamo un episodio senza bloccarci, resettiamo il contatore
            self.consecutive_stuck_episodes = 0
            
        # Reward extra per salti lunghi quando necessari
        if self.long_jump_mode and action in [3, 4]:
            initial_y = mario_y
            max_height_reached = False
            jump_distance = 0
            
            # Traccia l'altezza e la distanza del salto
            if mario_y < initial_y:  # Sta salendo
                max_height_reached = True
            elif max_height_reached and mario_y > initial_y:  # Sta scendendo
                jump_distance = abs(mario_x - self.last_position)
                
            # Reward per salti più lunghi
            if jump_distance > 20:  # Soglia per un "salto lungo"
                reward += jump_distance * 0.5
                print(f"Good long jump! Distance: {jump_distance}")
        
        # Reward standard per movimento
        if x_progress > 0:
            reward += x_progress * 0.1
        else:
            reward -= abs(x_progress)
            
        # Reward per score
        if score > self.last_score:
            reward += (score - self.last_score) * 0.5
            
        # Reward per salto riuscito
        if self.is_jumping_successful(mario_y) and action in [3, 4]:
            reward += 2
         
        # Penalità per salti eccessivi (solo quando non in long_jump_mode)
        if not self.long_jump_mode and action in [3, 4] and not self.is_jumping_necessary(entityList):
            reward -= 1
        
        # Danger reward
        danger_reward = self.calculate_danger_reward(localPlayer, entityList)
        reward += danger_reward
        
        # Punizione per morte
        if not self.is_alive():
            reward = -100
            done = True
            
        self.last_position = mario_x
        self.last_score = score
        
        return self.get_state(localPlayer, entityList), reward, done, {
            'x_pos': mario_x,
            'y_pos': mario_y,
            'score': score,
            'lives': lives,
            'steps': self.current_steps,
            'is_alive': self.is_alive(),
            'stuck_time': self.stuck_counter,
            'long_jump_mode': self.long_jump_mode
        }
        
    def is_jumping_necessary(self, enemies):
        """Verifica se il salto è necessario in base alla presenza di nemici o ostacoli"""
        for enemy in enemies:
            if enemy.distance < 40:
                return True
        return False

    def is_jumping_successful(self, mario_y):
        return mario_y < 100
        
    def reset_level(self):
        """Reset completo del livello"""
        self.pyboy.set_emulation_speed(1)
        
        # Attendi che il gioco sia pronto per il reset
        wait_frames = 0
        max_wait_frames = 120
        
        while not self.is_alive() and wait_frames < max_wait_frames:
            self._init_game()  # Controlla e inizializza se necessario
            self.pyboy.tick()
            wait_frames += 1
        
        # Aspetta alcuni frame per stabilizzare
        for _ in range(30):
            self._init_game()  # Controlla e inizializza se necessario
            self.pyboy.tick()
        
        # Ripristina la velocità normale
        self.pyboy.set_emulation_speed(emulate_speed)
        self.current_steps = 0
        self.stuck_counter = 0
        self.was_alive = True
        self.last_position = 0
        self.last_score = 0

    def reset(self):
        if not hasattr(self, 'pyboy'):
            self.pyboy = PyBoy(self.rom_path, window="SDL2")
            self.monitor = MarioLandMonitor(self.pyboy)
            self.pyboy.set_emulation_speed(emulate_speed)
            for _ in range(30):
                self._init_game()  # Controlla e inizializza se necessario
                self.pyboy.tick()
        else:
            self.reset_level()
        
        self.last_position = 0
        self.last_score = 0
        self.current_steps = 0
        self.stuck_counter = 0
        self.was_alive = True

        # Reset della modalità long jump solo se abbiamo completato con successo
        if not self.consecutive_stuck_episodes >= 3:
            self.long_jump_mode = False
        
        return self.preprocess_frame()
    
    def close(self):
        if hasattr(self, 'pyboy'):
            self.pyboy.stop()

def train():
    env = MarioEnvironment(os.path.join('rom', 'mario.gb'))
    action_size = 5
    agent = EnhancedDQNAgent(action_size)
    batch_size = 1024
    episodes = 1000
    
    save_dir = "mario_saves"
    os.makedirs(save_dir, exist_ok=True)

    start_time = time.time()
    save_interval = 120

    try:
        for episode in range(episodes):
            state = env.reset()
            total_reward = 0
            
            while True:
                action = agent.act(state)
                next_state, reward, done, info = env.step(action)

                agent.remember(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward
            
                if time.time() - start_time >= save_interval:
                    if len(agent.memory) > batch_size:
                        agent.replay(batch_size)
                    agent.model.save(os.path.join(save_dir, f"mario_model_episode_{episode + 1}.h5"))
                    print(f"\nModel saved: {os.path.join(save_dir, f'mario_model_episode_{episode + 1}.h5')}")
                    start_time = time.time()

                if done:
                    print(f"\nLevel Reset! Lives remaining: {info['lives']}")
                    break
                    
            agent.update_target_model()
            print(f"\nEpisode: {episode + 1}/{episodes}, Total Reward: {total_reward:.1f}, Epsilon: {agent.epsilon:.3f}")

    except KeyboardInterrupt:
        print("\nStopped ...")
        sys.exit(0)

    finally:
        env.close()

if __name__ == "__main__":
    train()