"""Contra NES environment for reinforcement learning."""
import numpy as np
from nes_py import NESEnv
from Contra.ROMs.rom_path import rom_path

# ---------------------------------------------------------------------------
# Contra NES RAM map  (source: community-documented RAM map)
# ---------------------------------------------------------------------------
#
# Game state
_RAM_LEVEL           = 0x0030  # Current level 0x00-0x07 → levels 1-8; 0x09 = game-over seq
_RAM_P1_LIVES        = 0x0032  # P1 lives; 0x00 = last life (not zero lives)
_RAM_P1_GAME_OVER    = 0x0038  # P1 game-over status: 0x00 = playing, 0x01 = game over
_RAM_CONTINUES       = 0x003A  # Number of continues remaining
_RAM_BOSS_DEFEATED   = 0x003B  # Boss defeated flag: 0x00 = no, 0x01 = yes
_RAM_END_LEVEL_SEQ   = 0x002D  # End-level routine index; non-zero = in end-level sequence
#
# Score  (2-byte BCD stored without trailing zeros — multiply by 100 for display score)
# e.g. internal 0x0050 → display score 5,000
_RAM_SCORE_HI        = 0x07E2  # P1 score high byte  (most-significant 2 BCD digits)
_RAM_SCORE_LO        = 0x07E3  # P1 score low byte   (least-significant 2 BCD digits)
#
# Player position
# World X = (Level Screen Number × 256) + Horizontal Scroll pixel offset
_RAM_SCREEN_NUMBER   = 0x0064  # Level Screen Number — which screen of the level
_RAM_SCROLL_X        = 0x00FD  # Horizontal scroll pixel offset within current screen (0-255)
#
# Player state
_RAM_P1_STATE        = 0x0090  # P1 state: 0x00 falling-in, 0x01 normal, 0x02 dead, 0x03 frozen
_RAM_P1_DEATH_FLAG   = 0x00B4  # P1 death flag: bit 0 set when player has died this life
#
# Enemy type slots (10 concurrent enemies on screen)
_ENEMY_TYPE_ADDRS    = list(range(0x0528, 0x0532))   # 0x0528 – 0x0531
#
# Enemy type values observed during stage-cleared / end-level sequence
_STAGE_OVER_ENEMIES  = np.array([0x2D, 0x31])
# ---------------------------------------------------------------------------

# Konami logo plays for ~180 frames before title screen appears.
# We must wait it out before pressing START, otherwise START is ignored.
_LOGO_WAIT     = 300   # NOOP until title screen is visible
_START_HOLD    = 60    # hold START to begin 1-player game
_START_RELEASE = 90    # NOOP to let the game fully initialize


def _bcd2(byte: int) -> int:
    """Convert a single BCD byte (two packed decimal digits) to integer."""
    return (byte >> 4) * 10 + (byte & 0x0F)


class ContraEnv(NESEnv):
    """
    Contra NES reinforcement-learning environment.

    Subclasses NESEnv (nes_py) and overrides four hooks called inside step():
      _get_reward  — shaped reward from RAM deltas (called first)
      _get_done    — episode termination via game-over flag
      _get_info    — diagnostic dict returned to caller
      _did_step    — advance the RAM snapshot after reward is computed

    And one reset hook:
      _did_reset   — skip attract screen, then snapshot initial RAM state

    Typical usage:
        from nes_py.wrappers import JoypadSpace
        from Contra.actions import COMPLEX_MOVEMENT
        env = JoypadSpace(ContraEnv(), COMPLEX_MOVEMENT)
        obs = env.reset()
        obs, reward, done, info = env.step(action)
    """

    reward_range = (-float('inf'), float('inf'))

    def __init__(self):
        super().__init__(rom_path())
        # Previous-frame snapshots used by _get_reward to compute deltas.
        # Updated by _did_step (called after _get_reward each step).
        self._prev_score = 0
        self._prev_lives = 0
        self._prev_x     = 0
        self._prev_level = 0

    # ------------------------------------------------------------------
    # NESEnv hooks
    # ------------------------------------------------------------------

    def _did_reset(self):
        """Wait past Konami logo, press START on title screen, snapshot RAM."""
        for _ in range(_LOGO_WAIT):
            self._frame_advance(0)
        for _ in range(_START_HOLD):
            self._frame_advance(8)   # START bitmask
        for _ in range(_START_RELEASE):
            self._frame_advance(0)

        self._prev_score = self._read_score()
        self._prev_lives = int(self.ram[_RAM_P1_LIVES])
        self._prev_x     = self._read_x()
        self._prev_level = int(self.ram[_RAM_LEVEL])

    def _get_reward(self):
        """
        Shaped reward from four signals:

          +score delta    killing enemies / picking up items
          +x progress     moving right through the level (capped to avoid scroll glitches)
          -life lost      -50 per death
          +level cleared  +500 when level index increments (boss defeated + transition)
           +0.01          tiny survival bonus each frame
        """
        score_now = self._read_score()
        lives_now = int(self.ram[_RAM_P1_LIVES])
        x_now     = self._read_x()
        level_now = int(self.ram[_RAM_LEVEL])

        reward = 0.0

        score_delta = score_now - self._prev_score
        if score_delta > 0:
            reward += score_delta * 0.01

        x_delta = x_now - self._prev_x
        if 0 < x_delta < 200:          # cap filters out scroll-wrap glitches
            reward += x_delta * 0.5

        if lives_now < self._prev_lives:
            reward -= 50.0

        if level_now > self._prev_level:
            reward += 500.0

        reward += 0.01                  # survival bonus

        return reward

    def _get_done(self):
        """Episode ends when the game-over flag is set."""
        return bool(self.ram[_RAM_P1_GAME_OVER])

    def _get_info(self):
        return {
            'score':          self._read_score(),
            'lives':          int(self.ram[_RAM_P1_LIVES]),
            'level':          int(self.ram[_RAM_LEVEL]) + 1,  # 1-indexed for readability
            'x_pos':          self._read_x(),
            'player_state':   int(self.ram[_RAM_P1_STATE]),   # 0x02 = dead
            'boss_defeated':  bool(self.ram[_RAM_BOSS_DEFEATED]),
            'stage_over':     self._stage_is_over(),
            'game_over':      bool(self.ram[_RAM_P1_GAME_OVER]),
        }

    def _did_step(self, done):
        """Advance the RAM snapshot so the next _get_reward sees correct deltas."""
        self._prev_score = self._read_score()
        self._prev_lives = int(self.ram[_RAM_P1_LIVES])
        self._prev_x     = self._read_x()
        self._prev_level = int(self.ram[_RAM_LEVEL])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read_score(self) -> int:
        """
        Read 2-byte BCD score at 0x7E2-0x7E3.
        Internal value × 100 = displayed score (Contra omits trailing zeros).
        """
        return (_bcd2(self.ram[_RAM_SCORE_HI]) * 100
                + _bcd2(self.ram[_RAM_SCORE_LO])) * 100

    def _read_x(self) -> int:
        """
        Absolute world X position.
        Each 'screen' is 256 pixels wide; scroll offset is pixel position within it.
        """
        return int(self.ram[_RAM_SCREEN_NUMBER]) * 256 + int(self.ram[_RAM_SCROLL_X])

    def _stage_is_over(self) -> bool:
        """True when the end-level routine is running (non-zero index)."""
        return bool(self.ram[_RAM_END_LEVEL_SEQ])


__all__ = [ContraEnv.__name__]
