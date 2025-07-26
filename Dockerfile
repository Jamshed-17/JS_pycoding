# Используем официальный образ Python
FROM python:3.11-slim

# Установим Node.js (для запуска JavaScript)
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /js-pybot_app

# Копируем файлы проекта в контейнер
COPY . .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Создадим папку data/DataBase если нет (или можно сделать это в коде)
RUN mkdir -p data


# Указываем команду запуска
CMD ["python3", "bot/main_bot.py"]
