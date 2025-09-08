#!/bin/bash
set -e

echo "Setting up development environment..."

# 1. Setup ZSH plugins
echo "Setting up ZSH plugins..."
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-completions ${ZSH_CUSTOM:-${ZSH:-~/.oh-my-zsh}/custom}/plugins/zsh-completions
git clone https://github.com/zsh-users/zsh-history-substring-search ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-history-substring-search
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
git clone https://github.com/matthiasha/zsh-uv-env ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-uv-env

# 2. Setup dotfiles
echo "Setting up dotfiles..."
git clone https://github.com/Baalakay/.dotfiles.git ~/.dotfiles
cd ~/.dotfiles
stow --adopt .
git reset --hard
cd $LOCAL_WORKSPACE_FOLDER

# 3. Ensure .zshrc exists and set aliases
touch ~/.zshrc
if grep -q '^alias cat=' ~/.zshrc; then
  sed -i 's|^alias cat=.*|alias cat=batcat|' ~/.zshrc
else
  echo 'alias cat=batcat' >> ~/.zshrc
fi
if ! grep -q '^alias bat=batcat' ~/.zshrc; then
  echo 'alias bat=batcat' >> ~/.zshrc
fi

# 4. Setup AWS CLI completion for zsh
echo "Setting up AWS CLI completion..."
if ! grep -q '^# For AWS CLI auto completions' ~/.zshrc; then
  echo '' >> ~/.zshrc
  echo '# For AWS CLI auto completions' >> ~/.zshrc
  echo 'autoload bashcompinit && bashcompinit' >> ~/.zshrc
  echo 'autoload -Uz compinit && compinit' >> ~/.zshrc
  echo 'complete -C '\''/usr/local/bin/aws_completer'\'' aws' >> ~/.zshrc
fi

# 5. Fix AWS CLI output issues permanently
echo "Fixing AWS CLI output issues..."
if ! grep -q '^unset FZF_DEFAULT_COMMAND' ~/.zshrc; then
  echo '' >> ~/.zshrc
  echo '# Permanently disable FZF_DEFAULT_COMMAND to prevent AWS CLI issues' >> ~/.zshrc
  echo 'unset FZF_DEFAULT_COMMAND' >> ~/.zshrc
fi
if ! grep -q '^export AWS_PAGER=""' ~/.zshrc; then
  echo 'export AWS_PAGER=""' >> ~/.zshrc
fi

# 6. npm global install (if needed)
npm install -g npm@11.4.1

uv sync

# 7. Install python packages
if [ -f "requirements.txt" ]; then
    uv pip install -r requirements.txt
    uv pip install -r requirements-dev.txt
fi

echo "Development environment setup complete! Launch a new terminal session to begin in your devcontainer."