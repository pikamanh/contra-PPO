"""
Manual play + RAM debug display for ContraEnv.

Layout:  [game 512×480] | [HUD panel 420×480]
Total window: 932 × 480

Keyboard:
  Arrow keys  — move
  J           — fire (B)
  K           — jump (A)
  Enter       — START (sent directly to emulator, bypasses JoypadSpace)
  ESC / close — quit
"""
import pygame
import numpy as np
from nes_py.wrappers import JoypadSpace

from Contra.contra_env import (
    ContraEnv,
    _RAM_LEVEL, _RAM_P1_LIVES, _RAM_P1_GAME_OVER,
    _RAM_SCORE_HI, _RAM_SCORE_LO,
    _RAM_SCREEN_NUMBER, _RAM_SCROLL_X,
    _RAM_P1_STATE, _RAM_END_LEVEL_SEQ,
)
from Contra.actions import COMPLEX_MOVEMENT

# ── display layout ─────────────────────────────────────────────────────────
SCALE      = 2
GAME_W     = 256 * SCALE   # 512
GAME_H     = 240 * SCALE   # 480
HUD_W      = 420
WIN_W      = GAME_W + HUD_W
WIN_H      = GAME_H
HUD_BG     = (18, 18, 18)
DIVIDER    = (60, 60, 60)

pygame.init()
screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Contra – RAM Debug  |  J=fire  K=jump  Enter=START  ESC=quit")
clock  = pygame.time.Clock()
font   = pygame.font.SysFont("monospace", 14)
font_h = pygame.font.SysFont("monospace", 14, bold=True)  # section headers

# ── environment ────────────────────────────────────────────────────────────
_base = ContraEnv()
env   = JoypadSpace(_base, COMPLEX_MOVEMENT)

obs  = env.reset()
done = False


# ── action mapping ─────────────────────────────────────────────────────────
def get_action(keys):
    r, l = keys[pygame.K_RIGHT], keys[pygame.K_LEFT]
    u, d = keys[pygame.K_UP],    keys[pygame.K_DOWN]
    fire  = keys[pygame.K_j]
    jump  = keys[pygame.K_k]

    if r and jump and fire and u: return 6
    if r and fire and u:          return 5
    if r and jump and u:          return 4
    if r and fire:                return 3
    if r and jump:                return 2
    if r:                         return 1
    if l and jump and fire and u: return 15
    if l and fire and u:          return 14
    if l and jump and u:          return 13
    if l and fire:                return 12
    if l and jump:                return 11
    if l:                         return 10
    if d and jump and fire:       return 18
    if d and fire:                return 17
    if d and jump:                return 16
    if u and jump and fire:       return 20
    if u and jump:                return 19
    if jump and fire:             return 9
    if fire:                      return 8
    if jump:                      return 7
    return 0


# ── HUD content ────────────────────────────────────────────────────────────
def build_hud(ram, info, step_reward, total_reward, action):
    """
    Return list of (text, colour, is_header) rows for the right-side panel.
    Colour = None on separator lines.
    """
    state_label = {0: "falling-in", 1: "normal", 2: "DEAD", 3: "frozen"}

    def row(label, value, colour):
        return (f"  {label:<24} {value}", colour, False)

    def header(title):
        return (f" {title}", (180, 180, 255), True)

    def sep():
        return ("", None, False)

    return [
        header("── Step ────────────────────"),
        row("action index",     str(action),                         (255, 255, 255)),
        row("action buttons",   str(COMPLEX_MOVEMENT[action]),       (255, 255, 255)),
        row("reward (step)",    f"{step_reward:+.4f}",               (255, 255,  80)),
        row("reward (total)",   f"{total_reward:+.1f}",              (255, 220,  50)),
        sep(),
        header("── ContraEnv  info{} ────────"),
        row("score",            f"{info['score']:,}",                (255, 255,   0)),
        row("lives",            f"{info['lives']}",                  ( 80, 255, 120)),
        row("level",            f"{info['level']}",                  (100, 200, 255)),
        row("x_pos",            f"{info['x_pos']}",                  (255, 180, 100)),
        row("player_state",     f"{info['player_state']}  "
                                f"({state_label.get(info['player_state'],'?')})",
                                                                     (255, 140, 140)),
        row("boss_defeated",    f"{info['boss_defeated']}",          (255, 120, 255)),
        row("stage_over",       f"{info['stage_over']}",             (120, 255, 180)),
        row("game_over",        f"{info['game_over']}",              (255,  70,  70)),
        sep(),
        header("── Raw RAM bytes ────────────"),
        row("0x0030  level",      f"{ram[_RAM_LEVEL]:#04x}  "
                                  f"= {ram[_RAM_LEVEL]}",            (160, 160, 160)),
        row("0x0032  p1_lives",   f"{ram[_RAM_P1_LIVES]:#04x}  "
                                  f"= {ram[_RAM_P1_LIVES]}",         (160, 160, 160)),
        row("0x0038  game_over",  f"{ram[_RAM_P1_GAME_OVER]:#04x}  "
                                  f"= {ram[_RAM_P1_GAME_OVER]}",     (160, 160, 160)),
        row("0x7E2   score_hi",   f"{ram[_RAM_SCORE_HI]:#04x}  "
                                  f"= {ram[_RAM_SCORE_HI]}",         (160, 160, 160)),
        row("0x7E3   score_lo",   f"{ram[_RAM_SCORE_LO]:#04x}  "
                                  f"= {ram[_RAM_SCORE_LO]}",         (160, 160, 160)),
        row("0x0064  screen_num", f"{ram[_RAM_SCREEN_NUMBER]:#04x}  "
                                  f"= {ram[_RAM_SCREEN_NUMBER]}",    (160, 160, 160)),
        row("0x00FD  scroll_x",   f"{ram[_RAM_SCROLL_X]:#04x}  "
                                  f"= {ram[_RAM_SCROLL_X]}",         (160, 160, 160)),
        row("0x0090  p1_state",   f"{ram[_RAM_P1_STATE]:#04x}  "
                                  f"= {ram[_RAM_P1_STATE]}",         (160, 160, 160)),
        row("0x002D  end_level",  f"{ram[_RAM_END_LEVEL_SEQ]:#04x}  "
                                  f"= {ram[_RAM_END_LEVEL_SEQ]}",    (160, 160, 160)),
        sep(),
        header("── Controls ─────────────────"),
        ("  Arrows=move  J=fire  K=jump", (120, 120, 120), False),
        ("  Enter=START  ESC=quit",        (120, 120, 120), False),
    ]


# ── main loop ──────────────────────────────────────────────────────────────
total_reward = 0.0
last_reward  = 0.0
action       = 0

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            done = True
    if done:
        break

    keys = pygame.key.get_pressed()

    if keys[pygame.K_RETURN]:
        _base._frame_advance(8)   # START bitmask, bypass JoypadSpace
        action = 0
    else:
        action = get_action(keys)

    result = env.step(action)
    if len(result) == 5:
        obs, reward, terminated, truncated, info = result
        episode_done = terminated or truncated
    else:
        obs, reward, episode_done, info = result

    last_reward   = reward
    total_reward += reward

    # ── draw game ──────────────────────────────────────────────────────
    screen.fill((0, 0, 0))
    frame   = np.transpose(obs, (1, 0, 2))
    surface = pygame.surfarray.make_surface(frame)
    surface = pygame.transform.scale(surface, (GAME_W, GAME_H))
    screen.blit(surface, (0, 0))

    # vertical divider
    pygame.draw.line(screen, DIVIDER, (GAME_W, 0), (GAME_W, WIN_H), 2)

    # ── draw HUD panel ─────────────────────────────────────────────────
    pygame.draw.rect(screen, HUD_BG, (GAME_W + 2, 0, HUD_W, WIN_H))

    rows    = build_hud(_base.ram, info, last_reward, total_reward, action)
    row_h   = 17
    y       = 8

    for text, colour, is_header in rows:
        if colour is None:          # separator → blank gap
            y += row_h // 2
            continue
        f   = font_h if is_header else font
        txt = f.render(text, True, colour)
        screen.blit(txt, (GAME_W + 4, y))
        y += row_h

    pygame.display.flip()

    if episode_done:
        obs          = env.reset()
        total_reward = 0.0

    clock.tick(60)

env.close()
pygame.quit()
