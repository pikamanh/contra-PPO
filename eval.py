"""
Visual evaluation of a trained Contra PPO agent.

Loads a checkpoint and renders the agent playing in real time via pygame.

Usage:
    python eval.py --model checkpoints/contra_ppo_final.zip
    python eval.py --model best_model/contra_ppo_best.zip --episodes 5
    python eval.py --model checkpoints/contra_ppo_100000_steps.zip --slow
"""
import argparse
import time

import numpy as np
import pygame

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import VecFrameStack, VecTransposeImage, DummyVecEnv

from Contra.wrappers import ContraGymnasiumEnv
from Contra.actions import COMPLEX_MOVEMENT

# ── display ────────────────────────────────────────────────────────────────
SCALE   = 2
GAME_W  = 256 * SCALE   # 512
GAME_H  = 240 * SCALE   # 480
HUD_W   = 300
WIN_W   = GAME_W + HUD_W
WIN_H   = GAME_H


def make_eval_env():
    """Single env, no TimeLimit — let episode run to natural game over."""
    env = ContraGymnasiumEnv(frame_skip=4)
    return env


def load_model(model_path: str, env):
    print(f"[eval] Loading model from {model_path}")
    model = PPO.load(model_path, env=env)
    print("[eval] Model loaded.")
    return model


def build_env():
    """Build the same wrapper stack used in training."""
    vec_env = DummyVecEnv([make_eval_env])
    vec_env = VecFrameStack(vec_env, n_stack=4)
    vec_env = VecTransposeImage(vec_env)
    return vec_env


def get_nes_screen(vec_env) -> np.ndarray:
    """
    Read the raw RGB screen directly from the NES emulator buffer.

    Wrapper chain: VecTransposeImage → VecFrameStack → DummyVecEnv → ContraGymnasiumEnv
    We unwrap down to ContraGymnasiumEnv._env (JoypadSpace) then to NESEnv.screen.
    This bypasses render_mode checks and always returns the live frame.
    """
    gym_env = vec_env.venv.venv.envs[0]   # ContraGymnasiumEnv
    return gym_env._env.unwrapped.screen   # (240, 256, 3) RGB, updated every step


def run_episode(model, vec_env, screen, font, font_bold, clock, fps: int):
    """Run one episode and return total reward."""
    obs = vec_env.reset()
    done      = False
    total_rew = 0.0
    step      = 0

    while not done:
        # ── agent decides ──────────────────────────────────────────────
        action, _ = model.predict(obs, deterministic=True)

        obs, reward, terminated, info = vec_env.step(action)
        total_rew += float(reward[0])
        step      += 1
        done       = bool(terminated[0])

        # ── get raw NES frame directly from emulator buffer ────────────
        raw_frame = get_nes_screen(vec_env)            # (240, 256, 3)
        frame     = np.transpose(raw_frame, (1, 0, 2)) # (256, 240, 3) for pygame
        surface   = pygame.surfarray.make_surface(frame)
        surface   = pygame.transform.scale(surface, (GAME_W, GAME_H))

        # ── draw ───────────────────────────────────────────────────────
        screen.fill((20, 20, 20))
        screen.blit(surface, (0, 0))
        pygame.draw.line(screen, (60, 60, 60), (GAME_W, 0), (GAME_W, WIN_H), 2)
        pygame.draw.rect(screen, (18, 18, 18), (GAME_W + 2, 0, HUD_W, WIN_H))

        # info dict comes from the innermost env via VecEnv
        env_info = info[0] if info else {}
        action_name = COMPLEX_MOVEMENT[int(action[0])]

        # Read raw RAM for demo mode diagnosis
        _gym_env = vec_env.venv.venv.envs[0]
        _ram     = _gym_env._env.unwrapped.ram
        demo_flag = int(_ram[0x001C])   # 0x00=real game, 0x01=demo/attract mode

        demo_colour = (255, 60, 60) if demo_flag else (80, 255, 120)
        demo_label  = "DEMO MODE (attract)" if demo_flag else "real game"

        hud = [
            ("── Agent ──────────────",   None,              True),
            ("action",   str(action_name),                   (255, 255, 255)),
            ("step",     str(step),                          (200, 200, 200)),
            ("",         "",                                 None),
            ("── Episode ────────────",   None,              True),
            ("reward (step)", f"{float(reward[0]):+.3f}",    (255, 255,  80)),
            ("reward (total)",f"{total_rew:+.1f}",           (255, 220,  50)),
            ("",         "",                                 None),
            ("── Game state ─────────",   None,              True),
            ("0x1C demo_mode", f"{demo_flag}  {demo_label}", demo_colour),
            ("score",    f"{env_info.get('score', '?'):,}",  (255, 255,   0)),
            ("lives",    str(env_info.get('lives',   '?')),  ( 80, 255, 120)),
            ("level",    str(env_info.get('level',   '?')),  (100, 200, 255)),
            ("x_pos",    str(env_info.get('x_pos',   '?')),  (255, 180, 100)),
            ("game_over",str(env_info.get('game_over','?')), (255,  80,  80)),
            ("",         "",                                 None),
            ("── Controls ───────────",   None,              True),
            ("ESC / close",  "quit",                         (120, 120, 120)),
        ]

        y = 10
        for item in hud:
            if len(item) == 3:
                label, value, colour = item
            else:
                continue

            if colour is None:          # blank separator
                y += 8
                continue

            if value is None:           # section header
                txt = font_bold.render(label, True, (160, 160, 255))
                screen.blit(txt, (GAME_W + 8, y))
            else:
                left  = font.render(f"  {label}", True, (150, 150, 150))
                right = font.render(value,         True, colour)
                screen.blit(left,  (GAME_W + 8,   y))
                screen.blit(right, (GAME_W + 180,  y))
            y += 18

        pygame.display.flip()

        # ── quit check ─────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return total_rew, True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return total_rew, True

        clock.tick(fps)

    return total_rew, False


def parse_args():
    p = argparse.ArgumentParser(description="Evaluate a trained Contra PPO agent")
    p.add_argument("--model", "--model-path", dest="model", type=str, required=True,
                   help="Path to .zip model checkpoint")
    p.add_argument("--episodes", type=int, default=3,
                   help="Number of episodes to run (default: 3)")
    p.add_argument("--fps",      type=int, default=60,
                   help="Render FPS (default: 60). Use lower value to slow down.")
    p.add_argument("--slow",     action="store_true",
                   help="Slow down to 20 FPS for easier observation")
    return p.parse_args()


def main():
    args  = parse_args()
    fps   = 20 if args.slow else args.fps

    # ── build env + model ──────────────────────────────────────────────
    vec_env = build_env()
    model   = load_model(args.model, vec_env)

    # ── pygame setup ───────────────────────────────────────────────────
    pygame.init()
    screen    = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption(f"Contra PPO — {args.model}")
    clock     = pygame.time.Clock()
    font      = pygame.font.SysFont("monospace", 13)
    font_bold = pygame.font.SysFont("monospace", 13, bold=True)

    # ── run episodes ───────────────────────────────────────────────────
    all_rewards = []
    for ep in range(1, args.episodes + 1):
        print(f"[eval] Episode {ep}/{args.episodes} ...")
        reward, quit_requested = run_episode(
            model, vec_env, screen, font, font_bold, clock, fps
        )
        all_rewards.append(reward)
        print(f"[eval] Episode {ep} total reward: {reward:.1f}")

        if quit_requested:
            break

        if ep < args.episodes:
            time.sleep(1.0)   # brief pause between episodes

    # ── summary ────────────────────────────────────────────────────────
    if all_rewards:
        print(f"\n[eval] Results over {len(all_rewards)} episode(s):")
        print(f"       mean reward : {np.mean(all_rewards):.1f}")
        print(f"       max  reward : {np.max(all_rewards):.1f}")
        print(f"       min  reward : {np.min(all_rewards):.1f}")

    vec_env.close()
    pygame.quit()


if __name__ == "__main__":
    main()
