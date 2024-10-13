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
sudo apt install -y wget curl unzip git python3 python3-pip libgbm1 libatk1.0-0 libatk-bridge2.0-0 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libnss3 libxrandr2 libasound2 libpangocairo-1.0-0 libgtk-3-0

# Скачивание и установка ChromeDriver
CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/115.0.5763.0/linux64/chromedriver-linux64.zip"
echo "Скачивание ChromeDriver..."
wget -O /tmp/chromedriver.zip $CHROMEDRIVER_URL

echo "Распаковка и установка ChromeDriver..."
unzip -o /tmp/chromedriver.zip -d /tmp/
sudo mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver
rm /tmp/chromedriver.zip

# Скачивание и установка Google Chrome
CHROME_URL="https://storage.googleapis.com/chrome-for-testing-public/115.0.5763.0/linux64/chrome-linux64.zip"
echo "Скачивание Google Chrome..."
wget -O /tmp/google-chrome.zip $CHROME_URL

echo "Распаковка и установка Google Chrome..."
unzip -o /tmp/google-chrome.zip -d /tmp/
sudo mv /tmp/chrome-linux64 /opt/google-chrome
sudo ln -sf /opt/google-chrome/chrome /usr/bin/google-chrome
rm /tmp/google-chrome.zip

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
