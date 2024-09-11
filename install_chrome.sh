#!/bin/bash

# Проверка наличия необходимых утилит
check_installed() {
    command -v "$1" &> /dev/null
}

# Функция для удаления установленного Google Chrome
remove_chrome() {
    if check_installed google-chrome; then
        echo "Удаление Google Chrome..."
        sudo apt remove --purge google-chrome-stable -y
    fi
}

# Функция для удаления установленного ChromeDriver
remove_chromedriver() {
    if check_installed chromedriver; then
        echo "Удаление ChromeDriver..."
        sudo rm /usr/bin/chromedriver
    fi
}

# Удаляем старые версии Google Chrome и ChromeDriver, если они есть
remove_chrome
remove_chromedriver

# Установка необходимых утилит
echo "Установка необходимых утилит..."
sudo apt update
sudo apt install -y wget curl unzip git python3 python3-pip  # Добавлены Python и pip

# Скачивание и установка ChromeDriver
CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.137/linux64/chromedriver-linux64.zip"
echo "Скачивание ChromeDriver..."
wget -O /tmp/chromedriver.zip $CHROMEDRIVER_URL

echo "Распаковка и установка ChromeDriver..."
unzip -o /tmp/chromedriver.zip -d /tmp/
sudo mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver
rm /tmp/chromedriver.zip

# Скачивание и установка Google Chrome
CHROME_URL="https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
echo "Скачивание Google Chrome..."
wget -O /tmp/google-chrome.deb $CHROME_URL

echo "Установка Google Chrome..."
sudo dpkg -i /tmp/google-chrome.deb
sudo apt --fix-broken install -y  # Для установки зависимостей, если они нужны

# Установка зависимостей через pip
if [ -f "requirements.txt" ]; then
    echo "Установка зависимостей из requirements.txt..."
    pip3 install -r requirements.txt
else
    echo "Файл requirements.txt не найден!"
fi

# Проверка установленных версий
echo "Проверка установленных версий..."
google-chrome --version
chromedriver --version

echo "Установка завершена!"
