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
    DummyVecEnv, SubprocVecEnv, VecFrameStack, VecMonitor, VecTransposeImage,
)
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback
from stable_baselines3.common.utils import get_schedule_fn, set_random_seed

from Contra.wrappers import ContraGymnasiumEnv

# ── directories ────────────────────────────────────────────────────────────
LOG_DIR        = "./logs/"
CHECKPOINT_DIR = "./checkpoints/"
BEST_MODEL_DIR = "./best_model/"
DEFAULT_LR     = 5e-5
RESUME_LR      = 5e-5
os.makedirs(LOG_DIR,        exist_ok=True)
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
os.makedirs(BEST_MODEL_DIR, exist_ok=True)


def make_env(rank: int, seed: int = 0):
    """Factory: each worker gets its own env + deterministic seed."""
    def _init():
        import warnings
        warnings.filterwarnings("ignore")
        env = ContraGymnasiumEnv(frame_skip=4)
        env = TimeLimit(env, max_episode_steps=MAX_EPISODE_STEPS)
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


def build_eval_env(seed: int = 10_000):
    """Single deterministic eval env with the same observation stack as train."""
    vec_env = DummyVecEnv([make_env(0, seed)])
    vec_env = VecFrameStack(vec_env, n_stack=4)
    vec_env = VecTransposeImage(vec_env)
    return vec_env


def build_model(vec_env):
    lr              = DEFAULT_LR    # learning rate
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


def override_learning_rate(model: PPO, learning_rate: float) -> None:
    """Force a loaded checkpoint to continue training with a new LR."""
    model.learning_rate = learning_rate
    model.lr_schedule = get_schedule_fn(learning_rate)

    if hasattr(model, "policy") and hasattr(model.policy, "optimizer"):
        for param_group in model.policy.optimizer.param_groups:
            param_group["lr"] = learning_rate


class EvalBestCallback(BaseCallback):
    """
    Save best model from deterministic evaluation, not rollout mean.

    The score is ordered by (min_reward, mean_reward). This intentionally
    prefers robust policies over high-variance policies with one great episode
    and one early death.
    """

    def __init__(
        self,
        save_path: str,
        eval_freq: int,
        n_eval_episodes: int,
        seed: int,
        verbose: int = 1,
    ):
        super().__init__(verbose)
        self.save_path = save_path
        self.eval_freq = eval_freq
        self.n_eval_episodes = n_eval_episodes
        self.seed = seed
        self.best_score = (-np.inf, -np.inf)
        self.eval_env = None

    def _init_callback(self) -> None:
        os.makedirs(self.save_path, exist_ok=True)
        self.eval_env = build_eval_env(self.seed)

    def _evaluate(self):
        rewards = []
        for _ in range(self.n_eval_episodes):
            obs = self.eval_env.reset()
            done = False
            total_reward = 0.0
            while not done:
                action, _ = self.model.predict(obs, deterministic=True)
                obs, reward, dones, _ = self.eval_env.step(action)
                total_reward += float(reward[0])
                done = bool(dones[0])
            rewards.append(total_reward)
        return rewards

    def _on_step(self) -> bool:
        if self.n_calls % self.eval_freq != 0:
            return True

        rewards = self._evaluate()
        mean_reward = float(np.mean(rewards))
        min_reward = float(np.min(rewards))
        max_reward = float(np.max(rewards))
        score = (min_reward, mean_reward)

        if self.verbose:
            print(
                "[eval-best] "
                f"timesteps={self.num_timesteps:,} "
                f"mean={mean_reward:.2f} min={min_reward:.2f} "
                f"max={max_reward:.2f}"
            )

        if score > self.best_score:
            self.best_score = score
            self.model.save(os.path.join(self.save_path, "contra_ppo_best"))
            if self.verbose:
                print(
                    "[eval-best] New robust best "
                    f"(min={min_reward:.2f}, mean={mean_reward:.2f}) → saved"
                )
        return True

    def _on_training_end(self) -> None:
        if self.eval_env is not None:
            self.eval_env.close()


def build_callbacks(n_envs: int, eval_freq: int, eval_episodes: int, seed: int):
    checkpoint_cb = CheckpointCallback(
        save_freq   = max(100_000 // n_envs, 1),   # every ~100K total steps
        save_path   = CHECKPOINT_DIR,
        name_prefix = "contra_ppo",
        verbose     = 1,
    )
    best_cb = EvalBestCallback(
        save_path       = BEST_MODEL_DIR,
        eval_freq       = max(eval_freq // n_envs, 1),
        n_eval_episodes = eval_episodes,
        seed            = seed + 10_000,
        verbose         = 1,
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
    p.add_argument("--resume-lr", type=float, default=RESUME_LR,
                   help="Learning rate to use when resuming from a checkpoint")
    p.add_argument("--eval-freq", type=int, default=50_000,
                   help="Total timesteps between deterministic eval-best checks")
    p.add_argument("--eval-episodes", type=int, default=5,
                   help="Episodes per deterministic eval-best check")
    return p.parse_args()


def main():
    args = parse_args()
    print(f"[train] envs={args.envs}  total_steps={args.steps:,}  seed={args.seed}")

    train_env = build_vec_env(args.envs, args.seed)

    if args.resume:
        print(f"[train] Resuming from {args.resume}")
        model = PPO.load(
            args.resume,
            env=train_env,
            tensorboard_log=LOG_DIR,
            learning_rate=args.resume_lr,
            custom_objects={"learning_rate": args.resume_lr},
        )
        override_learning_rate(model, args.resume_lr)
        print(f"[train] Resume learning_rate={args.resume_lr:g}")
    else:
        model = build_model(train_env)

    callbacks = build_callbacks(
        args.envs,
        eval_freq=args.eval_freq,
        eval_episodes=args.eval_episodes,
        seed=args.seed,
    )

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
