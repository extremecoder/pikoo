#!/bin/bash
set -e

# Set up pyenv environment variables
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# Install Python version if not already installed
pyenv install --skip-existing 3.10.13

# Set local Python version
pyenv local 3.10.13

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip and install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt