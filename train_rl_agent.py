import cv2
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecTransposeImage, DummyVecEnv
from env.aoe_env import AOEEnv

# 🧠 Step 1: Wrap in DummyVecEnv manually
env = DummyVecEnv([lambda: AOEEnv()])

# 🧠 Step 2: THEN apply VecTransposeImage
env = VecTransposeImage(env)

# 🚀 Step 3: Train the model
model = PPO(
    "CnnPolicy",
    env,
    verbose=1,
    tensorboard_log="./logs",
    learning_rate=2.5e-4,
    n_steps=128,
    batch_size=64,
    n_epochs=4,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2
)

model.learn(total_timesteps=100_000)
model.save("models/rl_aoe_agent")
