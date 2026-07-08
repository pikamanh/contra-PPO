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
NOOP_ACTION = 0

_RAM_P1_LIVES = 0x0032
_RAM_P1_STATE = 0x0090
_P1_STATE_NORMAL = 0x01


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

    def __init__(
        self,
        frame_skip: int = 4,
        render_mode: str | None = None,
        respawn_noop_frames: int = 90,
    ):
        super().__init__()
        self._env        = JoypadSpace(ContraEnv(), COMPLEX_MOVEMENT)
        self.frame_skip  = frame_skip
        self.render_mode = render_mode
        self.respawn_noop_frames = respawn_noop_frames
        self._respawn_noop_remaining = 0
        self._prev_lives = 0
        self._prev_player_state = _P1_STATE_NORMAL
        self._waiting_for_respawn_landing = False

        self.observation_space = gym.spaces.Box(
            low=0, high=255, shape=OBS_SHAPE, dtype=np.uint8
        )
        self.action_space = gym.spaces.Discrete(len(COMPLEX_MOVEMENT))

    # ------------------------------------------------------------------

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        obs = self._env.reset()          # old gym: returns obs only
        self._respawn_noop_remaining = 0
        self._prev_lives = int(self._ram[_RAM_P1_LIVES])
        self._prev_player_state = int(self._ram[_RAM_P1_STATE])
        self._waiting_for_respawn_landing = False
        return self._preprocess(obs), {}

    def step(self, action):
        total_reward = 0.0
        terminated   = False
        obs          = None
        info         = {}
        forced_noop  = False
        executed_action = action

        for _ in range(self.frame_skip):
            action_to_send = NOOP_ACTION if self._should_force_noop() else action
            forced_noop = forced_noop or (
                action_to_send == NOOP_ACTION and action != NOOP_ACTION
            )
            executed_action = action_to_send

            obs, reward, done, info = self._env.step(action_to_send)   # 4-tuple
            total_reward += reward
            self._update_respawn_guard()
            if done:
                terminated = True
                break

        info = dict(info)
        info["forced_respawn_noop"] = forced_noop
        info["respawn_noop_remaining"] = self._respawn_noop_remaining
        info["executed_action"] = int(executed_action)
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

    @property
    def _ram(self):
        return self._env.unwrapped.ram

    def _should_force_noop(self) -> bool:
        player_state = int(self._ram[_RAM_P1_STATE])
        return (
            player_state != _P1_STATE_NORMAL
            or self._respawn_noop_remaining > 0
        )

    def _update_respawn_guard(self) -> None:
        lives_now = int(self._ram[_RAM_P1_LIVES])
        player_state = int(self._ram[_RAM_P1_STATE])

        if lives_now < self._prev_lives:
            self._waiting_for_respawn_landing = True
            self._respawn_noop_remaining = 0
        elif (
            self._waiting_for_respawn_landing
            and self._prev_player_state != _P1_STATE_NORMAL
            and player_state == _P1_STATE_NORMAL
        ):
            self._waiting_for_respawn_landing = False
            self._respawn_noop_remaining = self.respawn_noop_frames
        elif self._respawn_noop_remaining > 0 and player_state == _P1_STATE_NORMAL:
            self._respawn_noop_remaining -= 1

        self._prev_lives = lives_now
        self._prev_player_state = player_state


__all__ = [ContraGymnasiumEnv.__name__]
