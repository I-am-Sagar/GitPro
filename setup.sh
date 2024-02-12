#!/bin/bash

# Script to set up gitpro globally

# Check if sudo is required
if [ "$EUID" -ne 0 ]; then
    echo "This script requires sudo privileges to create symbolic link. Please run with sudo."
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Copy gitpro.py to a global location
cp "${SCRIPT_DIR}/gitpro.py" /usr/local/bin/gitpro.py

# Check if gitpro already exists in /usr/local/bin
if [ -f "/usr/local/bin/gitpro" ]; then
    echo "Replacing existing gitpro script..."
    rm "/usr/local/bin/gitpro"
fi

# Create a symbolic link for the gitpro script in a global location
ln -s "/usr/local/bin/gitpro.py" /usr/local/bin/gitpro

# Make gitpro.py executable
chmod +x /usr/local/bin/gitpro.py

# Check the shell type and update the appropriate file to include /usr/local/bin in PATH
SHELL_TYPE="$(basename "$SHELL")"

if [[ "$SHELL_TYPE" == "bash" ]]; then
    # Update .bashrc file for bash shell
    echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
    echo "gitpro command is now available globally."
elif [[ "$SHELL_TYPE" == "zsh" ]]; then
    # Update .zshrc file for zsh shell
    echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
    source ~/.zshrc
    echo "gitpro command is now available globally."
else
    echo "Unsupported shell type. Please manually add /usr/local/bin to your PATH."
fi

echo "Setup complete. You can now use 'gitpro <command>' globally."
