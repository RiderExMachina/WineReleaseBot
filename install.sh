#!/usr/bin/env bash

if [[ $(id -u) -eq 0 ]]; then
    echo "Please do not run this script as root!"
fi
if [[ ! type pip3 ]]; then
    echo "Please install pip3"
    exit 1
fi

if [[ ! -d /opt/wrb ]]; then
    mkdir -p /opt/wrb
fi

cp wineReleaseBot.py /opt/wrb/
cp systemd/wrb.service /etc/systemd/system/
cp systemd/wrb.timer /etc/systemd/system/

if [[ -f auth.cred ]]; then
    if [[ ! -d /etc/wrb ]]; then
        mkdir -p /etc/wrb
    fi
    if [[ ! -d $HOME/.config/wrb ]]; then
        mkdir $HOME/.config/wrb
    fi
    sudo cp auth.cred /etc/wrb/
    ln -s /etc/wrb $HOME/.config/wrb
fi

/opt/wrb/wineReleaseBot.py -s
/opt/wrb/wineReleaseBot.py -d

sudo systemctl enable wrb.timer
sudo systemctl start wrb.service

if [[!$ -ne 0]]; then
	echo "Something went wrong. Please create a pull request with the information from 'systemctl status aacs-update'"
fi