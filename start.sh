#!/bin/bash

echo "🔄 Updating system..."
apt update && apt upgrade -y

echo "🐍 Installing Python..."
apt install python3 python3-pip git -y

echo "📥 Cloning your repo..."
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git

cd YOUR_REPO

echo "📦 Installing requirements..."
pip3 install -r requirements.txt

echo "🚀 Starting bot..."
python3 bot.py
