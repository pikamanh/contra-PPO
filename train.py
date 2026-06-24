"""
PPO training script for Contra NES.

Architecture:
  ContraEnv (NESEnv subclass)
      └── JoypadSpace            (21 discrete actions)
              └── ContraGymnasiumEnv     (frame-skip=4, grayscale 84×84)
                      └── SubprocVecEnv × N_ENVS   (parallel workers)
                              └── VecFrameStack × 4  (84,84,4)
                                      └── VecMonitor
                                              └── VecTransposeImage  (4,84,84) for PyTorch
                                                      └── PPO (CnnPolicy)

Run:
    python train.py
    python train.py --envs 4 --steps 5_000_000
    python train.py --resume checkpoints/contra_ppo_500000_steps.zip
"""
import argparse
import os
import warnings

# Suppress noisy deprecation warnings from nes_py using old gym
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*Gym has been unmaintained.*")

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import (
    SubprocVecEnv, VecFrameStack, VecMonitor, VecTransposeImage,
)
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.utils import set_random_seed

from Contra.wrappers import ContraGymnasiumEnv

# ── directories ────────────────────────────────────────────────────────────
LOG_DIR        = "./logs/"
CHECKPOINT_DIR = "./checkpoints/"
BEST_MODEL_DIR = "./best_model/"
os.makedirs(LOG_DIR,        exist_ok=True)
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
os.makedirs(BEST_MODEL_DIR, exist_ok=True)


def make_env(rank: int, seed: int = 0):
    """Factory: each worker gets its own env + deterministic seed."""
    def _init():
        env = ContraGymnasiumEnv(frame_skip=4)
        env.reset(seed=seed + rank)
        return env
    set_random_seed(seed)
    return _init


def build_vec_env(n_envs: int, seed: int = 0):
    vec_env = SubprocVecEnv([make_env(i, seed) for i in range(n_envs)])
    vec_env = VecFrameStack(vec_env, n_stack=4)    # obs shape: (84, 84, 4)
    vec_env = VecMonitor(vec_env, LOG_DIR)
    vec_env = VecTransposeImage(vec_env)            # (H,W,C) → (C,H,W) for PyTorch CNN
    return vec_env


def build_model(vec_env):
    return PPO(
        policy          = "CnnPolicy",
        env             = vec_env,
        # ── core PPO ──────────────────────────────────────────────────
        learning_rate   = 2.5e-4,
        n_steps         = 128,      # steps collected per env per update
        batch_size      = 256,      # minibatch size for gradient update
        n_epochs        = 4,        # passes over the rollout buffer
        gamma           = 0.99,     # discount factor
        gae_lambda      = 0.95,     # GAE smoothing
        clip_range      = 0.1,      # PPO clip epsilon
        # ── regularisation ────────────────────────────────────────────
        ent_coef        = 0.01,     # entropy bonus → encourages exploration
        vf_coef         = 0.5,      # value-function loss weight
        max_grad_norm   = 0.5,      # gradient clipping
        # ── logging ───────────────────────────────────────────────────
        tensorboard_log = LOG_DIR,
        verbose         = 1,
    )


def build_callbacks(n_envs: int, eval_env):
    checkpoint_cb = CheckpointCallback(
        save_freq   = max(100_000 // n_envs, 1),   # every ~100K total steps
        save_path   = CHECKPOINT_DIR,
        name_prefix = "contra_ppo",
        verbose     = 1,
    )
    eval_cb = EvalCallback(
        eval_env,
        best_model_save_path = BEST_MODEL_DIR,
        log_path             = LOG_DIR,
        eval_freq            = max(50_000 // n_envs, 1),
        n_eval_episodes      = 3,
        deterministic        = True,
        verbose              = 1,
    )
    return [checkpoint_cb, eval_cb]


# ── CLI ────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="Train PPO on Contra NES")
    p.add_argument("--envs",   type=int, default=8,
                   help="Number of parallel environments (default: 8)")
    p.add_argument("--steps",  type=int, default=10_000_000,
                   help="Total timesteps to train (default: 10M)")
    p.add_argument("--seed",   type=int, default=42)
    p.add_argument("--resume", type=str, default=None,
                   help="Path to .zip checkpoint to resume training")
    return p.parse_args()


def main():
    args = parse_args()
    print(f"[train] envs={args.envs}  total_steps={args.steps:,}  seed={args.seed}")

    train_env = build_vec_env(args.envs, args.seed)
    eval_env  = build_vec_env(1, args.seed + 1000)

    if args.resume:
        print(f"[train] Resuming from {args.resume}")
        model = PPO.load(args.resume, env=train_env, tensorboard_log=LOG_DIR)
    else:
        model = build_model(train_env)

    callbacks = build_callbacks(args.envs, eval_env)

    model.learn(
        total_timesteps     = args.steps,
        callback            = callbacks,
        tb_log_name         = "PPO_contra",
        reset_num_timesteps = args.resume is None,
        progress_bar        = True,
    )

    model.save(os.path.join(CHECKPOINT_DIR, "contra_ppo_final"))
    print("[train] Done — model saved to checkpoints/contra_ppo_final.zip")

    train_env.close()
    eval_env.close()


if __name__ == "__main__":
    main()
