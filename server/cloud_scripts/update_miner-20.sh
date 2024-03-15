#!/bin/bash

REPO_URL="https://github.com/RogueTensor/bitagent_subnet.git"
DIR="bitagent_subnet"

install_dependencies() {
    pip install -r requirements.txt && pip install -e . && pip uninstall uvloop -y
    echo "Dependencies installed."
}

strip_quotes() {
    local input="$1"

    # Remove leading and trailing quotes using parameter expansion
    local stripped="${input#\"}"
    stripped="${stripped%\"}"

    echo "$stripped"
}

get_version() {
  # Extract the version while removing possible carriage returns/spaces
  version=$(awk -F '"' '/__version__/ {print $2}' bitagent/validator/__init__.py | tr -d ' ')
  strip_quotes $version
}

if [ -d "$DIR" ]; then
    echo "'$DIR' directory exists."
    cd "$DIR"
    if git rev-parse --git-dir > /dev/null 2>&1; then
        echo "'$DIR' is a git repository."
        # Fetch latest changes from remote without merging
        git fetch origin main
        # Get local version
        local_version=$(get_version)
        # Get remote version without changing the working directory, trimming invisible characters
        remote_version=$(git show origin/main:bitagent/validator/__init__.py | awk -F '"' '/__version__/ {print $2}' | tr -d ' ')
        remote_version_cleared="$(strip_quotes $remote_version)"
        if [ "$local_version" != "$remote_version_cleared" ]; then
            echo "Version mismatch detected. Local version: $local_version, Remote version: $remote_version_cleared. Updating now..."
            git pull origin main
            install_dependencies
        else
            echo "Version is up-to-date. No update required."
        fi
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
