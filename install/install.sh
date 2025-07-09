#!/bin/bash

# =============================================================================
# Script Name: install.sh
# Description: This script automates the installatin of PiDash and creation of
#              the PiDash service.
#
# Usage: ./install.sh 
# =============================================================================

bold=$(tput bold)
normal=$(tput sgr0)
red=$(tput setaf 1)
green=$(tput setaf 2)

SOURCE=${BASH_SOURCE[0]}
while [ -h "$SOURCE" ]; do
  DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE
done
SCRIPT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

APPNAME="pidash"
INSTALL_PATH="/usr/local/$APPNAME"
SRC_PATH="$SCRIPT_DIR/../src"
BINPATH="/usr/local/bin"
VENV_PATH="$INSTALL_PATH/venv_$APPNAME"

SERVICE_FILE="$APPNAME.service"
SERVICE_FILE_SOURCE="$SCRIPT_DIR/$SERVICE_FILE"
SERVICE_FILE_TARGET="/etc/systemd/system/$SERVICE_FILE"

APT_REQUIREMENTS_FILE="$SCRIPT_DIR/debian-requirements.txt"
PIP_REQUIREMENTS_FILE="$SCRIPT_DIR/pip-requirements.txt"

check_permissions () {
  if [ "$EUID" -ne 0 ]; then
    echo_error "ERROR: Installation requires root privileges. Please run it with sudo."
    exit 1
  fi
}

enable_interfaces () {
  echo "Enabling interfaces required for $APPNAME"
  sed -i 's/^dtparam=spi=.*/dtparam=spi=on/' /boot/config.txt
  sed -i 's/^#dtparam=spi=.*/dtparam=spi=on/' /boot/config.txt
  raspi-config nonint do_spi 0
  echo_success "\tSPI Interface has been enabled."
  sed -i 's/^dtparam=i2c_arm=.*/dtparam=i2c_arm=on/' /boot/config.txt
  sed -i 's/^#dtparam=i2c_arm=.*/dtparam=i2c_arm=on/' /boot/config.txt
  raspi-config nonint do_i2c 0
  echo_success "\tI2C Interface has been enabled."

  echo "Enabling single CS line for SPI interface in config.txt"
  if ! grep -E -q '^[[:space:]]*dtoverlay=spi0-0cs' /boot/firmware/config.txt; then
    sed -i '/^dtparam=spi=on/a dtoverlay=spi0-0cs' /boot/firmware/config.txt
  else
    echo "dtoverlay for spi0-0cs already specified"
  fi
}

show_loader () {
  local pid=$!
  local delay=0.1
  local spinstr='|/-\'
  printf "$1 [${spinstr:0:1}] "
  while ps a | awk '{print $1}' | grep -q "${pid}"; do
    local temp=${spinstr#?}
    printf "\r$1 [${temp:0:1}] "
    spinstr=${temp}${spinstr%"${temp}"}
    sleep ${delay}
  done
  if [[ $? -eq 0 ]]; then
    printf "\r$1 [\e[32m\xE2\x9C\x94\e[0m]\n"
  else
    printf "\r$1 [\e[31m\xE2\x9C\x98\e[0m]\n"
  fi
}

echo_success () {
  echo -e "$1 [\e[32m\xE2\x9C\x94\e[0m]"
}

echo_override () {
  echo -e "\r$1"
}

echo_header () {
  echo -e "${bold}$1${normal}"
}

echo_error () {
  echo -e "${red}$1${normal} [\e[31m\xE2\x9C\x98\e[0m]\n"
}

echo_blue () {
  echo -e "\e[38;2;65;105;225m$1\e[0m"
}


install_debian_dependencies () {
  if [ -f "$APT_REQUIREMENTS_FILE" ]; then
    if xargs -a "$APT_REQUIREMENTS_FILE" apt-get install -y > /dev/null; then
      echo_success "Installing system dependencies."
    else
      echo_error "Failed to install system dependencies."
      exit 1
    fi
  else
    echo "ERROR: System dependencies file $APT_REQUIREMENTS_FILE not found!"
    exit 1
  fi
}

create_venv () {
  echo "Creating python virtual environment. "
  if ! python3 -m venv "$VENV_PATH"; then
    echo_error "Failed to create virtual environment!"
    exit 1
  fi
  
  echo "Upgrading pip..."
  if ! "$VENV_PATH/bin/python" -m pip install --upgrade pip setuptools wheel > /dev/null; then
    echo_error "Failed to upgrade pip!"
    exit 1
  fi
  echo_success "Pip upgraded."
  
  echo "Installing python dependencies..."
  if ! "$VENV_PATH/bin/python" -m pip install -r "$PIP_REQUIREMENTS_FILE" -qq > /dev/null; then
    echo_error "Failed to install Python dependencies!"
    exit 1
  fi
  echo_success "\tInstalling python dependencies. "
}

install_app_service () {
  echo "Installing $APPNAME systemd service."
  if [ -f "$SERVICE_FILE_SOURCE" ]; then
    if ! cp "$SERVICE_FILE_SOURCE" "$SERVICE_FILE_TARGET"; then
      echo_error "Failed to copy service file!"
      exit 1/
    fi
    systemctl daemon-reload
    if ! systemctl enable "$SERVICE_FILE"; then
      echo_error "Failed to enable service!"
      exit 1
    fi
    echo_success "\tService installed and enabled."
  else
    echo_error "ERROR: Service file $SERVICE_FILE_SOURCE not found!"
    exit 1
  fi
}

install_executable () {
  echo "Adding executable to ${BINPATH}/$APPNAME"
  if ! cp "$SCRIPT_DIR/pidash" "$BINPATH/"; then
    echo_error "Failed to copy executable!"
    exit 1
  fi
  if ! chmod +x "$BINPATH/$APPNAME"; then
    echo_error "Failed to make executable!"
    exit 1
  fi
  echo_success "\tExecutable installed."
}

install_config() {
  CONFIG_BASE_DIR="$SCRIPT_DIR/config_base"
  CONFIG_DIR="$SRC_PATH/config"
  echo "Copying config files to $CONFIG_DIR"

  # Check and copy device.config if it doesn't exist
  if [ ! -f "$CONFIG_DIR/device.json" ]; then
    if ! cp "$CONFIG_BASE_DIR/device.json" "$CONFIG_DIR/"; then
      echo_error "Failed to copy device.json!"
      exit 1
    fi
    echo_success "\tCopying device.config to $CONFIG_DIR"
  else
    echo_success "\tdevice.json already exists in $CONFIG_DIR"
  fi
}

stop_service () {
    echo "Checking if $SERVICE_FILE is running"
    if systemctl is-active --quiet "$SERVICE_FILE"; then
      if systemctl stop "$SERVICE_FILE"; then
        echo_success "Stopped $APPNAME service"
      else
        echo_error "Failed to stop $APPNAME service!"
      fi
    else  
      echo_success "\t$SERVICE_FILE not running"
    fi
}

start_service () {
  echo "Starting $APPNAME service."
  if systemctl start "$SERVICE_FILE"; then
    echo_success "Started $APPNAME service."
  else
    echo_error "Failed to start $APPNAME service!"
    exit 1
  fi
}

copy_project () {
  echo "Installing $APPNAME to $INSTALL_PATH"
  if [[ -d $INSTALL_PATH ]]; then
    if ! rm -rf "$INSTALL_PATH"; then
      echo_error "Failed to remove existing installation!"
      exit 1
    fi
    echo_success "Removed existing installation found at $INSTALL_PATH"
  fi

  if ! mkdir -p "$INSTALL_PATH"; then
    echo_error "Failed to create installation directory!"
    exit 1
  fi

  if ! ln -sf "$SRC_PATH" "$INSTALL_PATH/src"; then
    echo_error "Failed to create symlink!"
    exit 1
  fi
  echo_success "Created symlink from $SRC_PATH to $INSTALL_PATH/src"
}

get_hostname () {
  echo "$(hostname)"
}

get_ip_address () {
  ip_address=$(hostname -I | awk '{print $1}')
  echo "$ip_address"
}

ask_for_reboot () {
  hostname=$(get_hostname)
  ip_address=$(get_ip_address)
  echo_header "$(echo_success "${APPNAME^^} Installation Complete!")"
  echo_header "[•] A reboot of your Raspberry Pi is required for the changes to take effect"
  echo_header "[•] After your Pi is rebooted, you can access the web UI by going to $(echo_blue "'$hostname.local'") or $(echo_blue "'$ip_address'") in your browser."

  read -p "Would you like to restart your Raspberry Pi now? [Y/N] " userInput
  userInput="${userInput,,}"

  if [[ "${userInput}" == "y" ]]; then
    echo_success "You entered 'Y', rebooting now..."
    sleep 2
    reboot now
  elif [[ "${userInput}" == "n" ]]; then
    echo "Please restart your Raspberry Pi later to apply changes by running 'reboot now'."
    exit
  else
    echo "Unknown input, please restart your Raspberry Pi later to apply changes by running 'reboot now'."
    sleep 1
  fi
}

check_permissions
stop_service
enable_interfaces
install_debian_dependencies
copy_project
create_venv
install_executable
install_config
install_app_service
ask_for_reboot
