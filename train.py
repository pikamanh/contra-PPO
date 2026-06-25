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
import numpy as np
from gymnasium.wrappers import TimeLimit

from stable_baselines3 import PPO

# 4500 agent-steps × frame_skip(4) / 60fps ≈ 5 phút game time tối đa/episode
MAX_EPISODE_STEPS = 4500
from stable_baselines3.common.vec_env import (
    SubprocVecEnv, VecFrameStack, VecMonitor, VecTransposeImage,
)
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
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
        import warnings
        warnings.filterwarnings("ignore")
        env = ContraGymnasiumEnv(frame_skip=4)
        # env = TimeLimit(env, max_episode_steps=MAX_EPISODE_STEPS)
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
    lr              = 1e-4    # learning rate
    gamma           = 0.9     # discount factor
    tau             = 1.0     # GAE lambda
    beta            = 0.02    # entropy coefficient
    epsilon         = 0.2     # PPO clip range
    batch_size      = 128     # minibatch size
    num_epochs      = 10      # passes over rollout buffer
    num_local_steps = 512     # rollout steps per env

    return PPO(
        policy          = "CnnPolicy",
        env             = vec_env,
        learning_rate   = lr,
        n_steps         = num_local_steps,
        batch_size      = batch_size,
        n_epochs        = num_epochs,
        gamma           = gamma,
        gae_lambda      = tau,
        clip_range      = epsilon,
        ent_coef        = beta,
        vf_coef         = 0.5,
        max_grad_norm   = 0.5,
        tensorboard_log = LOG_DIR,
        verbose         = 1,
    )


class SaveBestCallback(BaseCallback):
    """
    Save best model based on mean episode reward from the training buffer.

    SB3 keeps a rolling buffer (ep_info_buffer) of the last 100 completed
    episodes across all envs. We read it every `check_freq` steps and save
    when the mean reward improves — no separate eval env needed.

    Metric: mean of ep_info_buffer["r"]  (same as rollout/ep_rew_mean in TB)
    """

    def __init__(self, save_path: str, check_freq: int, verbose: int = 1):
        super().__init__(verbose)
        self.save_path       = save_path
        self.check_freq      = check_freq
        self.best_mean_reward = -np.inf

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq != 0:
            return True
        if len(self.model.ep_info_buffer) == 0:
            return True

        mean_reward = np.mean([ep["r"] for ep in self.model.ep_info_buffer])
        if mean_reward > self.best_mean_reward:
            self.best_mean_reward = mean_reward
            self.model.save(os.path.join(self.save_path, "contra_ppo_best"))
            if self.verbose:
                print(f"[best] New best mean reward: {mean_reward:.2f} → saved")
        return True


def build_callbacks(n_envs: int):
    checkpoint_cb = CheckpointCallback(
        save_freq   = max(100_000 // n_envs, 1),   # every ~100K total steps
        save_path   = CHECKPOINT_DIR,
        name_prefix = "contra_ppo",
        verbose     = 1,
    )
    best_cb = SaveBestCallback(
        save_path  = BEST_MODEL_DIR,
        check_freq = max(50_000 // n_envs, 1),     # check every ~50K total steps
        verbose    = 1,
    )
    return [checkpoint_cb, best_cb]


# ── CLI ────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="Train PPO on Contra NES")
    p.add_argument("--envs",   type=int, default=32,
                   help="Number of parallel environments / num_processes (default: 32)")
    p.add_argument("--steps",  type=int, default=1_000_000,
                   help="Total timesteps to train (default: 10M)")
    p.add_argument("--seed",   type=int, default=42)
    p.add_argument("--resume", type=str, default=None,
                   help="Path to .zip checkpoint to resume training")
    return p.parse_args()


def main():
    args = parse_args()
    print(f"[train] envs={args.envs}  total_steps={args.steps:,}  seed={args.seed}")

    train_env = build_vec_env(args.envs, args.seed)

    if args.resume:
        print(f"[train] Resuming from {args.resume}")
        model = PPO.load(args.resume, env=train_env, tensorboard_log=LOG_DIR)
    else:
        model = build_model(train_env)

    callbacks = build_callbacks(args.envs)

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


if __name__ == "__main__":
    main()
