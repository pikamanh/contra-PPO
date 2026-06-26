"""Contra NES environment for reinforcement learning."""
import numpy as np
from nes_py import NESEnv
from Contra.ROMs.rom_path import rom_path

# ---------------------------------------------------------------------------
# Contra NES RAM map
# ---------------------------------------------------------------------------
_RAM_LEVEL        = 0x0030  # Current level 0x00-0x07 → levels 1-8; 0x09 = game-over seq
_RAM_P1_LIVES     = 0x0032  # P1 lives; 0x00 = last life
_RAM_P1_GAME_OVER = 0x0038  # 0x00 playing, 0x01 game over
_RAM_BOSS_DEFEATED = 0x003B  # 0x00 = no, 0x01 = yes
_RAM_END_LEVEL_SEQ = 0x002D  # non-zero = in end-level sequence

_RAM_SCORE_HI     = 0x07E2  # P1 score high byte (BCD)
_RAM_SCORE_LO     = 0x07E3  # P1 score low byte  (BCD)

_RAM_SCREEN_NUMBER = 0x0064  # Level Screen Number
_RAM_SCROLL_X      = 0x00FD  # Horizontal scroll pixel offset (0-255)

_RAM_P1_STATE     = 0x0090  # 0x00 falling-in, 0x01 normal, 0x02 dead, 0x03 frozen

_ENEMY_TYPE_BASE  = 0x0528  # Enemy Type array, 16 slots
_ENEMY_SLOT_COUNT = 16
# ---------------------------------------------------------------------------

_LOGO_WAIT     = 300
_START_HOLD    = 60
_START_RELEASE = 90


def _bcd2(byte: int) -> int:
    """Convert a single BCD byte to integer."""
    return (byte >> 4) * 10 + (byte & 0x0F)


class ContraEnv(NESEnv):
    """
    Contra NES reinforcement-learning environment.

    Reward components (all divided by 10 before returning):
      ProgressReward  = clip(x_delta - 0.5, -3, 3)   moving right; -0.5 bias penalises idling
      ScoreReward     = clip(score_delta, 0, 2)        kills / pickups
      LifePenalty     = -15 on death, else 0
      DodgeReward     = +0.5 per step alive in normal state with enemies on screen
      TerminalReward  = +50 level clear | -35 game over | 0 otherwise

    The progress bias (-0.5) and dodge reward (+0.5) are balanced so that
    standing still near enemies nets 0 while advancing nets ≥1, preventing
    the agent from learning to idle purely for the dodge bonus.
    """

    reward_range = (-float('inf'), float('inf'))

    def __init__(self):
        super().__init__(rom_path())
        self._prev_score = 0
        self._prev_lives = 0
        self._prev_x     = 0
        self._prev_level = 0

    # ------------------------------------------------------------------
    # NESEnv hooks
    # ------------------------------------------------------------------

    def _did_reset(self):
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
        score_now = self._read_score()
        lives_now = int(self.ram[_RAM_P1_LIVES])
        x_now     = self._read_x()
        level_now = int(self.ram[_RAM_LEVEL])

        # -0.5 bias: standing still costs -0.05 after /10, forcing forward movement
        progress_reward = float(np.clip(x_now - self._prev_x - 0.5, -3, 3))

        score_reward = float(np.clip(score_now - self._prev_score, 0, 2))

        just_died    = lives_now < self._prev_lives
        life_penalty = -15.0 if just_died else 0.0

        # Dodge reward: +0.5 each frame the player is alive (normal state) while
        # enemies are present. Cancels the standing-still cost exactly, so the
        # agent must still progress to earn positive reward.
        if not just_died and int(self.ram[_RAM_P1_STATE]) == 0x01:
            active_enemies = sum(
                1 for i in range(_ENEMY_SLOT_COUNT)
                if self.ram[_ENEMY_TYPE_BASE + i] != 0
            )
            dodge_reward = 0.5 if active_enemies > 0 else 0.0
        else:
            dodge_reward = 0.0

        if level_now > self._prev_level:
            terminal_reward = 50.0
        elif bool(self.ram[_RAM_P1_GAME_OVER]):
            terminal_reward = -35.0
        else:
            terminal_reward = 0.0

        return (progress_reward + score_reward + life_penalty + dodge_reward + terminal_reward) / 10

    def _get_done(self):
        return bool(self.ram[_RAM_P1_GAME_OVER])

    def _get_info(self):
        return {
            'score':         self._read_score(),
            'lives':         int(self.ram[_RAM_P1_LIVES]),
            'level':         int(self.ram[_RAM_LEVEL]) + 1,
            'x_pos':         self._read_x(),
            'player_state':  int(self.ram[_RAM_P1_STATE]),
            'boss_defeated': bool(self.ram[_RAM_BOSS_DEFEATED]),
            'stage_over':    self._stage_is_over(),
            'game_over':     bool(self.ram[_RAM_P1_GAME_OVER]),
        }

    def _did_step(self, done):  # noqa: ARG002
        self._prev_score = self._read_score()
        self._prev_lives = int(self.ram[_RAM_P1_LIVES])
        self._prev_x     = self._read_x()
        self._prev_level = int(self.ram[_RAM_LEVEL])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read_score(self) -> int:
        return (_bcd2(self.ram[_RAM_SCORE_HI]) * 100
                + _bcd2(self.ram[_RAM_SCORE_LO])) * 100

    def _read_x(self) -> int:
        return int(self.ram[_RAM_SCREEN_NUMBER]) * 256 + int(self.ram[_RAM_SCROLL_X])

    def _stage_is_over(self) -> bool:
        return bool(self.ram[_RAM_END_LEVEL_SEQ])


__all__ = [ContraEnv.__name__]
