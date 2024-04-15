import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import gym
import matplotlib.pyplot as plt

# Define the environment
class CameraControlEnv(gym.Env):
    def __init__(self):
        super(CameraControlEnv, self).__init__()
        self.target_location = np.array([50, 50])  # Target location (pixel coordinates)
        self.current_location = np.array([0, 0])  # Initial location of camera center (pixel coordinates)
        self.action_space = gym.spaces.Discrete(4)  # Actions: move up, down, left, or right
        self.observation_space = gym.spaces.Box(low=0, high=100, shape=(4,), dtype=np.float32)  # [current_x, current_y, target_x, target_y]

    def reset(self):
        # Reset the camera location
        self.current_location = np.array([0, 0])
        return np.concatenate([self.current_location, self.target_location])

    def step(self, action):
        # Apply action to move the camera
        if action == 0:  # Move up
            self.current_location[1] += 1
        elif action == 1:  # Move down
            self.current_location[1] -= 1
        elif action == 2:  # Move left
            self.current_location[0] -= 1
        elif action == 3:  # Move right
            self.current_location[0] += 1

        # Calculate reward
        distance_to_target = np.linalg.norm(self.current_location - self.target_location)
        reward = -distance_to_target  # Penalize distance from target
        done = (distance_to_target < 1)  # Terminate if close to target
        return np.concatenate([self.current_location, self.target_location]), reward, done, {}

# Define the Deep Q-Network
class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Initialize environment and DQN
env = CameraControlEnv()
input_dim = env.observation_space.shape[0]
output_dim = env.action_space.n
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = DQN(input_dim, output_dim).to(device)
optimizer = optim.Adam(model.parameters(), lr=0.0001)
loss_fn = nn.MSELoss()

# Training parameters
num_episodes = 1000
epsilon = 0.1  # Epsilon-greedy exploration

# Initialize lists to store location history
current_location_history = []
target_location_history = []

# Training loop
for episode in range(num_episodes):
    state = env.reset()
    state = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(device)
    done = False
    total_reward = 0

    while not done:
        # Append current location and target location to history
        current_location_history.append(state.cpu().numpy()[0][:2])
        target_location_history.append(state.cpu().numpy()[0][2:])
        
        # Epsilon-greedy action selection
        if np.random.rand() < epsilon:
            action = env.action_space.sample()  # Explore
        else:
            with torch.no_grad():
                q_values = model(state)
                action = torch.argmax(q_values).item()  # Exploit

        # Take action
        next_state, reward, done, _ = env.step(action)
        next_state = torch.tensor(next_state, dtype=torch.float32).unsqueeze(0).to(device)
        total_reward += reward

        # Compute TD target
        with torch.no_grad():
            next_q_values = model(next_state)
            td_target = reward + 0.99 * torch.max(next_q_values)

        # Compute TD error
        q_values = model(state)
        td_error = td_target - q_values[0, action]

        # Update model
        optimizer.zero_grad()
        loss = loss_fn(q_values[0, action], td_target)
        loss.backward()
        optimizer.step()

        state = next_state

    if episode % 10 == 0:
        print(f"Episode {episode}, Total Reward: {total_reward}")
# Convert location history to NumPy arrays for plotting
current_location_history = np.array(current_location_history)
target_location_history = np.array(target_location_history)

# Plot location history
plt.figure(figsize=(8, 6))
plt.plot(current_location_history[:, 0], current_location_history[:, 1], label="Current Location", color='blue')
plt.plot(target_location_history[:, 0], target_location_history[:, 1], label="Target Location", color='red')
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Camera Location History")
plt.legend()
plt.grid(True)
plt.show()
# Test the trained model
state = env.reset()
done = False
while not done:
    state = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(device)
    with torch.no_grad():
        q_values = model(state)
        action = torch.argmax(q_values).item()
    next_state, reward, done, _ = env.step(action)
    state = next_state
    print(f"Action: {action}, Reward: {reward}, Camera Position: {state[:2]}, Target Position: {state[2:]}")
