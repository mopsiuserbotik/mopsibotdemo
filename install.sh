#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
RESET='\033[0m'

echo -e "${GREEN}\nустановка зависимостей...\n${RESET}"

pkg update && pkg upgrade -y

pkg install git -y
pkg install python -y
pkg install zbar -y
pkg install libjpeg-turbo zlib libpng freetype -y
pkg install ffmpeg -y

pip install --upgrade pip setuptools wheel

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo -e "${RED}Файл requirements.txt не найден. Установка прервана.${RESET}"
    exit 1
fi

echo -e "${GREEN}\nзависимости установлены, запуск main.py...\n${RESET}"

python main.py