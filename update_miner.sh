#!/bin/bash

REPO_URL="https://github.com/bit-current/DistributedTraining.git"
DIR="DistributedTraining"

install_dependencies() {
  pip install -e . && python post_install.py
}


if [ -d "$DIR" ]; then
    echo "'$DIR' directory exists."
    cd "$DIR"
    if git rev-parse --git-dir > /dev/null 2>&1; then
        echo "'$DIR' is a git repository. Updating it now..."
        git pull origin main
        install_dependencies
    else
        echo "'$DIR' is not a git repository. Removing and cloning anew..."
        cd ..
        rm -rf "$DIR"
        git clone "$REPO_URL"
        cd "$DIR"
        install_dependencies
    fi
else
    echo "'$DIR' directory does not exist. Cloning the repository..."
    git clone "$REPO_URL"
    cd "$DIR"
    install_dependencies
fi

echo "Update complete."
