#!/usr/bin/bash

EXT_PATH=nautilus-open-in-ptyxis.py

restart_nautilus() {
    read -p "Restart Nautilus(Files)? [Y/n]" ans

    if [[ $ans == 'y' || $ans == 'Y' || $ans == '' ]]; then
        nautilus -q
    fi
}

install_sudo() {
    path=$EXT_PATH
    target=/usr/share/nautilus-python/extensions/

    if [[ ! -d $target ]]; then
        sudo mkdir -v -p $target
    fi

    sudo cp -v $path $target

    restart_nautilus
}

if [[ $(id -u) != 0 ]]; then
    echo "This script must be run as root. Please use sudo."
    echo "Tip: sudo !!"
    exit 1
fi

install_sudo
