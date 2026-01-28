## ✨ TwoD: Open-Source 2D Game Engine

TwoD is a robust, open-source 2D game engine designed to empower developers to create a wide variety of games, including classic RPGs and dynamic 2D Platformers.

Inspired by the accessibility and workflow of engines like RPG Maker, TwoD offers a flexible and powerful toolkit for non-programmers and seasoned developers alike. Its open-source nature fosters community collaboration, ensuring continuous improvement and a rich library of user-created assets and tools.



## 📜 Credits & Acknowledgments

Here:

https://github.com/Stormwindsky/TwoD/blob/main/NOTICE.md

## Setup

### ⚠️ PLEASE NOTE THAT THESE INSTRUCTIONS MAY BE THEORETICALLY SIMILAR TO THOSE FOR WINDOWS, BUT SINCE I DO NOT HAVE WINDOWS AND ONLY LINUX, I CANNOT CONFIRM THAT THE COMMANDS TYPED IN WINDOWS ARE 100% THE SAME. ⚠️

# 🛠️ Installation & Setup Guide

This guide will help you set up the development environment for the **TwoD Engine** on Linux (Ubuntu/Mint).

## Prerequisites

Before starting, ensure your system is up to date and you have Python installed.

sudo apt update
sudo apt install python3 python3-venv python3-pip

# 🚀 Getting Started

Follow these steps to clone the repository and set up the virtual environment.
1. Clone the repository

git clone [https://github.com/Stormwindsky/TwoD.git](https://github.com/Stormwindsky/TwoD.git)
cd TwoD

2. Create a Virtual Environment

It is highly recommended to use a virtual environment to keep dependencies organized and avoid conflicts with system packages.

python3 -m venv .venv

3. Activate the Environment

You must activate the virtual environment every time you open a new terminal to work on this project.

# On Linux / macOS
source .venv/bin/activate

Note: Once activated, your terminal prompt should start with (.venv).
4. Install Dependencies

Install Pygame and any other required libraries using pip:

pip install --upgrade pip
pip install pygame

# 🎮 Running the Engine

To launch the project, simply run the main script:

python3 twod_engine.py

# 📦 Troubleshooting
"ModuleNotFoundError: No module named 'pygame'"

This usually happens if:

    1. You forgot to activate the virtual environment (source .venv/bin/activate).

    2. You installed pygame before activating the environment.

"python3-venv is not installed"

If you get an error while creating the venv, run: sudo apt install python3-venv

