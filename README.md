# Gym for Contra

![image](https://haoyue.xyz/2019/07/24/5d380b686b1ca.png)

An [OpenAI](https://github.com/openai/gym) Gym environment for Contra.  on The Nintendo Entertainment System (NES) using the [nes-py emulator](https://github.com/Kautenja/nes-py).

[Project address](https://github.com/OuYanghaoyue/gym_contra)

# Installation
The preferred installation of Contra is from pip:
```shell
pip install gym-contra
```
# Usage
## Python
You must import ContraEnv before trying to make an environment. This is because gym environments are registered at runtime. By default, ContraEnv use the full NES action space of 256 discrete actions. To contstrain this,ContraEnv.actions provides three actions lists (RIGHT_ONLY, SIMPLE_MOVEMENT, and COMPLEX_MOVEMENT) for the nes_py.wrappers.JoypadSpace wrapper. See [Contra/actions.py](https://github.com/OuYanghaoyue/gym_contra/blob/master/Contra/actions.py) for a breakdown of the legal actions in each of these three lists.


```Python
from nes_py.wrappers import JoypadSpace
import gym
from Contra.actions import SIMPLE_MOVEMENT, COMPLEX_MOVEMENT, RIGHT_ONLY

env = gym.make('Contra-v0')
env = JoypadSpace(env, RIGHT_ONLY)

print("actions", env.action_space)
print("observation_space ", env.observation_space.shape[0])

done = False
env.reset()
for step in range(5000):
    if done:
        print("Over")
        break
    state, reward, done, info = env.step(env.action_space.sample())
    env.render()

env.close()
```

> NOTE: ContraEnv.make is just an alias to gym.make for convenience.
> 
> NOTE: remove calls to render in training code for a nontrivial speedup.

## Command Line
Prepare to write please wait

> NOTE: by default,-m is set to human.

## Environments
These environments allow 3 attempts (lives) to play in the game. The environments only send reward-able game-play frames to agents; No cut-scenes, loading screens, etc. are sent from the NES emulator to an agent nor can an agent perform actions during these instances. If a cut-scene is not able to be skipped by hacking the NES's RAM, the environment will lock the Python process until the emulator is ready for the next action.

## Step
> Info about the rewards and info returned by the step method.

### Reward Function
The reward function assumes the objective of the game is to move as far right as possible (increase the agent's x value), as fast as possible, without dying. To model this game, three separate variables compose the reward:

1. v: the difference in agent x values between states
- in this case this is instantaneous velocity for the given step
- v = x1 - x0
    - x0 is the x position before the step
    - x1 is the x position after the step
- moving right ⇔ v > 0
- moving left ⇔ v < 0
- not moving ⇔ v = 0

2. d: a death penalty that penalizes the agent for dying in a state
    - this penalty encourages the agent to avoid death
    - alive ⇔ d = 0
    - dead ⇔ d = -15
3. b : if the agent defeated the boss 
    - this reword will encourages the agent to defeat boss as possible
    - no defeated ⇔ 0
    - defeated ⇔ 30

So the reward function is:

r = v + d + b


> Note:The reward is clipped into the range (-15, 15).

## info dictionary
The info dictionary returned by the step method contains the following keys:


```Python
life=self._life,
dead=self._is_dead,
done=self._get_done(),
score=self._score(),
status=self._player_state,
x_pos=self._x_position,
y_pos=self._y_position,defeated=self._get_boss_defeated,

```

Key  | Type | Description |
---|--- | ---
life | int | The number of lives left, i.e., {3, 2, 1}
dead | Bool | Get The palyer is dead
done | Bool | Get the game is game over
score | int | Get the player's score
status | Bool | Alive Status (00 - Dead, 01 - Alive, 02 - Dying)
x_pos | int | Player's x position in the stage (from the left)
y_pos |	int	| Player's y position in the stage (from the bottom)
defeated | Bool| self._get_boss_defeated

# 🎮 Contra-PPO: Reinforcement Learning Agent for Contra using PPO

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)]()
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-red.svg)]()
[![Gymnasium](https://img.shields.io/badge/Gymnasium-Latest-green.svg)]()
[![Stable-Baselines3](https://img.shields.io/badge/Stable--Baselines3-PPO-orange.svg)]()

A Reinforcement Learning project that trains an autonomous agent to play **Contra** using the **Proximal Policy Optimization (PPO)** algorithm. The project is built with **Gymnasium**, **PyTorch**, and **Stable-Baselines3**, providing a complete pipeline from environment creation, training, evaluation, and model visualization.

---

## 📌 Project Overview

Contra is a classic side-scrolling shooting game that requires the player to:

- Navigate through obstacles
- Avoid enemy attacks
- Defeat enemies
- Reach the end of each stage

Traditional rule-based AI struggles with such dynamic environments. Therefore, this project applies **Deep Reinforcement Learning (DRL)**, allowing an agent to learn optimal behaviors directly through interactions with the game.

The PPO algorithm is chosen because it provides stable learning, high sample efficiency, and strong performance in continuous optimization problems.

---

## 🎯 Objectives

- Build a custom Gymnasium environment for Contra.
- Train an RL agent using PPO.
- Design an effective reward function.
- Evaluate the trained model.
- Visualize agent performance.

---

## 🧠 Reinforcement Learning Framework

The agent follows the standard RL interaction loop:

```
Environment
      │
      ▼
 Observation
      │
      ▼
    PPO Agent
      │
      ▼
    Action
      │
      ▼
 Environment
      │
      ▼
Reward + Next State
```

The policy is optimized using **Proximal Policy Optimization (PPO)** from Stable-Baselines3.

---

## 📂 Project Structure

```
contra-PPO/
│
├── env/
│   ├── contra_env.py          # Custom Gymnasium environment
│   ├── wrappers.py
│   └── utils.py
│
├── models/
│   ├── best_model.zip
│   └── checkpoints/
│
├── train.py                   # PPO training
├── evaluate.py                # Model evaluation
├── play.py                    # Watch trained agent
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

## ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/pikamanh/contra-PPO.git
cd contra-PPO
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Training

Start training the PPO agent

```bash
python train.py
```

The model checkpoints will be saved automatically.

---

## ▶️ Evaluation

Evaluate the trained model

```bash
python evaluate.py
```

Metrics include

- Average reward
- Episode length
- Success rate

---

## 🎥 Play with the Trained Agent

```bash
python play.py
```

The trained PPO agent will control the character automatically.

---

## 🏆 PPO Hyperparameters

| Parameter | Value |
|------------|--------|
| Algorithm | PPO |
| Policy | CNN / MLP |
| Learning Rate | 3e-4 |
| Gamma | 0.99 |
| GAE Lambda | 0.95 |
| Clip Range | 0.2 |
| Batch Size | 64 |
| n_steps | 2048 |
| Total Timesteps | Configurable |

---

## 🎯 Reward Design

The reward function encourages the following behaviors:

Positive Rewards

- Moving forward
- Defeating enemies
- Collecting power-ups
- Completing a stage

Negative Rewards

- Taking damage
- Dying
- Standing still
- Moving backward for too long

This reward shaping helps the agent learn faster while avoiding reward exploitation.

---

## 📈 Results

After training, the PPO agent is capable of:

- Navigating the map
- Avoiding enemy attacks
- Eliminating enemies
- Progressing through the level autonomously

Performance can be further improved through reward tuning and longer training.

---

## 🛠 Technologies

- Python
- PyTorch
- Stable-Baselines3
- Gymnasium
- NumPy
- OpenCV
- Matplotlib

---

## 📚 References

- Schulman et al. (2017), **Proximal Policy Optimization Algorithms**
- Stable-Baselines3 Documentation
- Gymnasium Documentation
- OpenAI Reinforcement Learning Resources

---

## 👨‍💻 Author

**Minh Phuc, Manh Hung**

GitHub: https://github.com/pikamanh

---

## 📄 License

This project is intended for educational and research purposes.
