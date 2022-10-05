#!/usr/bin/env bash

if $1 -eq "uninstall"; then
    sudo systemctl stop wrb.timer
    sudo systemctl disable wrb.timer
    rm /etc/systemd/system/wrb.{timer,service}
fi

if [[ $(id -u) -ne 0 ]]; then
    echo "Please run this script as root"
fi
if [[ ! $(type pip3) ]]; then
    echo "Please install pip3"
    exit 1
fi

if [[ ! -d /opt/wrb ]]; then
    sudo mkdir -p /opt/wrb
fi
sudo cp wineReleaseBot.py /opt/wrb/


if [[ ! -d /etc/wrb ]]; then
    sudo mkdir -p /etc/wrb
fi
if [[ ! -d $HOME/.config/wrb ]]; then
    mkdir $HOME/.config/wrb
fi

if [[ -f auth.cred ]]; then
    sudo cp auth.cred /etc/wrb/
    ln -s /etc/wrb $HOME/.config/wrb
fi

/opt/wrb/wineReleaseBot.py -s
/opt/wrb/wineReleaseBot.py -d

sudo cp systemd/wrb.service /etc/systemd/system/
sudo cp systemd/wrb.timer /etc/systemd/system/
sudo systemctl enable wrb.timer
sudo systemctl start wrb.timer
