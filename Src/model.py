import random
import numpy as np
from collections import deque
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Conv2D, Dense, Flatten, Input, concatenate
from tensorflow.keras.optimizers import Adam



class EnhancedDQNAgent:
    def __init__(self, action_size):
        # Parametri base
        self.action_size = action_size
        self.memory = deque(maxlen=50000)
        
        # Parametri di learning
        self.gamma = 0.95  # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9995
        self.learning_rate = 0.00025
        self.tau = 0.001  # Per soft update del target network
        
        # Dimensioni degli input
        self.image_shape = (84, 84, 1)
        self.player_state_size = 9
        self.enemy_state_size = (5, 5)  # 5 nemici max, 5 features per nemico
        
        # Reti neurali
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.align_target_model()

    def _build_model(self):
        # Input layers
        image_input = Input(shape=self.image_shape, name='image_input')
        player_input = Input(shape=(self.player_state_size,), name='player_input')
        enemy_input = Input(shape=self.enemy_state_size, name='enemy_input')
        
        # CNN per processare l'immagine
        conv1 = Conv2D(32, (8, 8), strides=(4, 4), activation='relu')(image_input)
        conv2 = Conv2D(64, (4, 4), strides=(2, 2), activation='relu')(conv1)
        conv3 = Conv2D(64, (3, 3), strides=(1, 1), activation='relu')(conv2)
        conv_flat = Flatten()(conv3)
        
        # Dense network per processare lo stato del player
        player_dense = Dense(64, activation='relu')(player_input)
        
        # Dense network per processare i nemici
        enemy_flat = Flatten()(enemy_input)
        enemy_dense = Dense(128, activation='relu')(enemy_flat)
        
        # Concatena tutti i features
        merged = concatenate([conv_flat, player_dense, enemy_dense])
        
        # Layers finali
        dense1 = Dense(512, activation='relu')(merged)
        dense2 = Dense(256, activation='relu')(dense1)
        output = Dense(self.action_size, activation='linear')(dense2)
        
        model = Model(inputs=[image_input, player_input, enemy_input], 
                     outputs=output)
        model.compile(loss='huber_loss', optimizer=Adam(learning_rate=self.learning_rate))
        
        return model

    def align_target_model(self):
        """Hard update del target model"""
        self.target_model.set_weights(self.model.get_weights())

    def update_target_model(self):
        """Soft update del target model"""
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = self.tau * weights[i] + (1 - self.tau) * target_weights[i]
        self.target_model.set_weights(target_weights)

    def remember(self, state, action, reward, next_state, done):
        """Salva l'esperienza nel replay buffer"""
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, training=True):
        """Seleziona un'azione usando epsilon-greedy policy"""
        if training and random.random() < self.epsilon:
            return random.randrange(self.action_size)
        
        state_dict = {
            'image_input': np.expand_dims(state['image'], axis=0),
            'player_input': np.expand_dims(state['player_state'], axis=0),
            'enemy_input': np.expand_dims(state['enemies_state'], axis=0)
        }
        
        act_values = self.model.predict(state_dict, verbose=0)
        return np.argmax(act_values[0])

    def replay(self, batch_size):
        """Esegue il training su un batch di esperienze"""
        if len(self.memory) < batch_size:
            return
        
        # Campiona un batch random dalla memoria
        minibatch = random.sample(self.memory, batch_size)
        
        # Prepara i batch di input
        state_images = np.zeros((batch_size,) + self.image_shape)
        state_players = np.zeros((batch_size, self.player_state_size))
        state_enemies = np.zeros((batch_size,) + self.enemy_state_size)
        
        next_state_images = np.zeros((batch_size,) + self.image_shape)
        next_state_players = np.zeros((batch_size, self.player_state_size))
        next_state_enemies = np.zeros((batch_size,) + self.enemy_state_size)
        
        actions = np.zeros(batch_size, dtype=np.int32)
        rewards = np.zeros(batch_size)
        dones = np.zeros(batch_size, dtype=bool)
        
        # Popola i batch
        try:
            for i, (state, action, reward, next_state, done) in enumerate(minibatch):
                state_images[i] = state['image']
                state_players[i] = state['player_state']
                state_enemies[i] = state['enemies_state']
                
                next_state_images[i] = next_state['image']
                next_state_players[i] = next_state['player_state']
                next_state_enemies[i] = next_state['enemies_state']
                
                actions[i] = action
                rewards[i] = reward
                dones[i] = done
        
            # Predici i Q-values correnti e futuri
            current_q = self.model.predict({
                'image_input': state_images,
                'player_input': state_players,
                'enemy_input': state_enemies
            }, verbose=0)
            
            future_q = self.target_model.predict({
                'image_input': next_state_images,
                'player_input': next_state_players,
                'enemy_input': next_state_enemies
            }, verbose=0)
            
            # Aggiorna i target Q-values
            for i in range(batch_size):
                if dones[i]:
                    current_q[i][actions[i]] = rewards[i]
                else:
                    current_q[i][actions[i]] = rewards[i] + self.gamma * np.max(future_q[i])
            
            # Train del modello
            self.model.fit({
                'image_input': state_images,
                'player_input': state_players,
                'enemy_input': state_enemies
            }, current_q, epochs=1, verbose=0)
            
            # Aggiorna epsilon
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
            
            # Soft update del target network
            self.update_target_model()

        except:
            print("None data")

    def load(self, name):
        """Carica i pesi del modello"""
        self.model.load_weights(name)
        self.target_model.load_weights(name)

    def save(self, name):
        """Salva i pesi del modello"""
        self.model.save_weights(name)