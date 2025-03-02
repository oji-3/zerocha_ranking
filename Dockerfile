FROM python:3.11.9-slim

WORKDIR /app

# 必要なパッケージのインストール（Chromium と ChromeDriver）
RUN apt-get update && \
    apt-get install -y chromium chromium-driver && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
