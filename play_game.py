import pygame
import numpy as np
from nes_py.nes_env import NESEnv
from nes_py.wrappers import JoypadSpace

from Contra.actions import COMPLEX_MOVEMENT

SCALE = 2
WIDTH, HEIGHT = 256 * SCALE, 240 * SCALE

# Khởi tạo pygame TRƯỚC khi tạo env để tránh xung đột display
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Contra | Mũi tên, J=bắn, K=nhảy, Enter=Start | Click vào cửa sổ này trước!")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

env = NESEnv("Contra/ROMs/contra.nes")
env = JoypadSpace(env, COMPLEX_MOVEMENT)

result = env.reset()
obs = result[0] if isinstance(result, tuple) else result

done = False
# Gửi START để bỏ qua màn hình title (attract mode)
start_frames = 0


def get_action(keys):
    right = keys[pygame.K_RIGHT]
    left  = keys[pygame.K_LEFT]
    up    = keys[pygame.K_UP]
    down  = keys[pygame.K_DOWN]
    fire  = keys[pygame.K_j]
    jump  = keys[pygame.K_k]

    if right and jump and fire and up: return 6
    if right and fire and up:          return 5
    if right and jump and up:          return 4
    if right and fire:                 return 3
    if right and jump:                 return 2
    if right:                          return 1
    if left and jump and fire and up:  return 15
    if left and fire and up:           return 14
    if left and jump and up:           return 13
    if left and fire:                  return 12
    if left and jump:                  return 11
    if left:                           return 10
    if down and jump and fire:         return 18
    if down and fire:                  return 17
    if down and jump:                  return 16
    if up and jump and fire:           return 20
    if up and jump:                    return 19
    if jump and fire:                  return 9
    if fire:                           return 8
    if jump:                           return 7
    return 0  # NOOP


# Action index của START trong COMPLEX_MOVEMENT không có, dùng NESEnv trực tiếp
# JoypadSpace nhận discrete action (index vào COMPLEX_MOVEMENT)
# Dùng env._frame_advance để skip title screen trước khi wrap

while not done:
    pressed_keys = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            pressed_keys.append(event.key)

    keys = pygame.key.get_pressed()

    # Nhấn Enter để start game (gửi thẳng vào NES controller)
    if keys[pygame.K_RETURN]:
        # START button = bit 4 trong NES joypad bitmask
        # Bypass JoypadSpace, tạm thời dùng action NOOP nhưng ghi trực tiếp RAM
        # Cách đơn giản: unwrap và step với START bitmask
        env.unwrapped._frame_advance(8)   # 8 = START button
        action = 0
    else:
        action = get_action(keys)

    result = env.step(action)
    if len(result) == 5:
        obs, reward, terminated, truncated, info = result
        episode_done = terminated or truncated
    else:
        obs, reward, episode_done, info = result

    # Vẽ frame game
    frame = np.transpose(obs, (1, 0, 2))
    surface = pygame.surfarray.make_surface(frame)
    surface = pygame.transform.scale(surface, (WIDTH, HEIGHT))
    screen.blit(surface, (0, 0))

    # HUD debug: hiện action đang nhấn
    action_name = COMPLEX_MOVEMENT[action] if action < len(COMPLEX_MOVEMENT) else ["START"]
    hud = font.render(f"Action: {action} {action_name}", True, (255, 255, 0))
    screen.blit(hud, (8, 8))
    pygame.display.flip()

    if episode_done:
        result = env.reset()
        obs = result[0] if isinstance(result, tuple) else result

    clock.tick(60)

env.close()
pygame.quit()
