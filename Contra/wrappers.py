"""
Gymnasium-compatible wrapper for ContraEnv.

nes_py uses the old gym API (4-tuple step, obs-only reset).
SB3 2.x requires gymnasium (5-tuple step, (obs, info) reset).
This wrapper bridges the gap and adds frame-skip + grayscale preprocessing.
"""
import cv2
import numpy as np
import gymnasium as gym
from nes_py.wrappers import JoypadSpace

from Contra.contra_env import ContraEnv
from Contra.actions import COMPLEX_MOVEMENT

OBS_SHAPE = (84, 84, 1)   # grayscale, channel-last


class ContraGymnasiumEnv(gym.Env):
    """
    Gymnasium wrapper around ContraEnv + JoypadSpace.

    Preprocessing applied per step:
      - RGB → grayscale
      - Resize to 84×84
      - Return shape (84, 84, 1)  ← SB3 VecFrameStack stacks on axis -1

    Frame skip (default 4):
      The same action is repeated for `frame_skip` emulator frames.
      Rewards are summed; the last frame's observation is returned.
      This reduces compute cost and lets the network see temporally
      coherent motion (combined with VecFrameStack in train.py).
    """

    metadata = {"render_modes": ["rgb_array"]}

    def __init__(self, frame_skip: int = 4, render_mode: str | None = None):
        super().__init__()
        self._env        = JoypadSpace(ContraEnv(), COMPLEX_MOVEMENT)
        self.frame_skip  = frame_skip
        self.render_mode = render_mode

        self.observation_space = gym.spaces.Box(
            low=0, high=255, shape=OBS_SHAPE, dtype=np.uint8
        )
        self.action_space = gym.spaces.Discrete(len(COMPLEX_MOVEMENT))

    # ------------------------------------------------------------------

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        obs = self._env.reset()          # old gym: returns obs only
        return self._preprocess(obs), {}

    def step(self, action):
        total_reward = 0.0
        terminated   = False
        obs          = None
        info         = {}

        for _ in range(self.frame_skip):
            obs, reward, done, info = self._env.step(action)   # 4-tuple
            total_reward += reward
            if done:
                terminated = True
                break

        return self._preprocess(obs), total_reward, terminated, False, info

    def render(self):
        if self.render_mode == "rgb_array":
            return self._env.render(mode="rgb_array")

    def close(self):
        self._env.close()

    # ------------------------------------------------------------------

    def _preprocess(self, obs: np.ndarray) -> np.ndarray:
        gray    = cv2.cvtColor(obs, cv2.COLOR_RGB2GRAY)
        resized = cv2.resize(gray, (84, 84), interpolation=cv2.INTER_AREA)
        return resized[:, :, np.newaxis]   # (84, 84, 1)


__all__ = [ContraGymnasiumEnv.__name__]
