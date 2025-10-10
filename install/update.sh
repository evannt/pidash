#!/bin/bash

bold=$(tput bold)
normal=$(tput sgr0)
green=$(tput setaf 2)
red=$(tput setaf 1)

SOURCE=${BASH_SOURCE[0]}
while [ -h "$SOURCE" ]; do
  DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE
done
SCRIPT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

APPNAME="pidash"
SRC_PATH="$SCRIPT_DIR/../src"
INSTALL_PATH="/usr/local/$APPNAME"
VENV_PATH="$INSTALL_PATH/venv_$APPNAME"

APT_REQUIREMENTS_FILE="$SCRIPT_DIR/debian-requirements.txt"
PIP_REQUIREMENTS_FILE="$SCRIPT_DIR/pip-requirements.txt"

echo_success() {
  echo -e "$1 [\e[32m\xE2\x9C\x94\e[0m]"
}

echo_error() {
  echo -e "$1 [\e[31m\xE2\x9C\x98\e[0m]\n"
}

if [ "$EUID" -ne 0 ]; then
  echo_error "ERROR: This script requires root privileges. Please run it with sudo."
  exit 1
fi

echo "Stopping $APPNAME service."
systemctl stop $APPNAME.service
CONFIG_BASE_DIR="$SCRIPT_DIR/config_base"
CONFIG_DIR="$SRC_PATH/config"
echo "Copying config files to $CONFIG_DIR"

if ! mkdir -p "$CONFIG_DIR"; then
  echo_error "Failed to create config directory!"
  exit 1
fi

if ! cp "$CONFIG_BASE_DIR/device.json" "$CONFIG_DIR/"; then
  echo_error "Failed to copy device.json!"
  exit 1
fi
echo_success "\tCopying device.config to $CONFIG_DIR"

apt-get update -y > /dev/null &
if [ -f "$APT_REQUIREMENTS_FILE" ]; then
  echo "Installing system dependencies... "
  xargs -a "$APT_REQUIREMENTS_FILE" apt-get install -y > /dev/null && echo_success "Installed system dependencies."
else
  echo_error "ERROR: System dependencies file $APT_REQUIREMENTS_FILE not found!"
  exit 1
fi

if [ ! -d "$VENV_PATH" ]; then
  echo_error "ERROR: Virtual environment not found at $VENV_PATH. Run the installation script first."
  exit 1
fi

source "$VENV_PATH/bin/activate"

echo "Upgrading pip..."
$VENV_PATH/bin/python -m pip install --upgrade pip setuptools wheel > /dev/null && echo_success "Pip upgraded successfully."

if [ -f "$PIP_REQUIREMENTS_FILE" ]; then
  echo "Updating Python dependencies..."
  $VENV_PATH/bin/python -m pip install --upgrade -r "$PIP_REQUIREMENTS_FILE" -qq > /dev/null && echo_success "Dependencies updated successfully."
else
  echo_error "ERROR: Requirements file $PIP_REQUIREMENTS_FILE not found!"
  exit 1
fi

echo "Restarting $APPNAME service."
systemctl start $APPNAME.service

echo_success "Update completed."
