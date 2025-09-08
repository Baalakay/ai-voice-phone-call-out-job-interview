#!/bin/zsh

PROJECT_ROOT="$(pwd)"
ACTIVE_PROJECT="$(basename "$PROJECT_ROOT")"
ENV_FILE=".devcontainer/.env"

# Ensure .devcontainer exists
if [ ! -d ".devcontainer" ]; then
  echo "Error: .devcontainer directory not found in project root."
  exit 1
fi

# Create .env if it doesn't exist
touch "$ENV_FILE"

# Update or add PROJECT_ROOT
if grep -q "^PROJECT_ROOT=" "$ENV_FILE"; then
  sed -i.bak "s|^PROJECT_ROOT=.*$|PROJECT_ROOT=$PROJECT_ROOT|" "$ENV_FILE"
else
  echo "PROJECT_ROOT=$PROJECT_ROOT" >> "$ENV_FILE"
fi

# Update or add ACTIVE_PROJECT
if grep -q "^ACTIVE_PROJECT=" "$ENV_FILE"; then
  sed -i.bak "s|^ACTIVE_PROJECT=.*$|ACTIVE_PROJECT=$ACTIVE_PROJECT|" "$ENV_FILE"
else
  echo "ACTIVE_PROJECT=$ACTIVE_PROJECT" >> "$ENV_FILE"
fi

# Clean up backup file created by sed (macOS/BSD)
rm -f "$ENV_FILE.bak"

echo "Set PROJECT_ROOT=$PROJECT_ROOT and ACTIVE_PROJECT=$ACTIVE_PROJECT in $ENV_FILE
"
