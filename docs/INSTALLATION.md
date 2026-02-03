# Подробная инструкция по установке

## Требования

### Системные требования

- **Python**: версия 3.10 или выше
- **pip**: менеджер пакетов Python
- **Git**: для клонирования репозитория
- **Браузер**: современный браузер (Chrome, Firefox, Safari, Edge)

### API ключи

- **Anthropic API key** - для части 1 (классификатор)
  - Получить можно на [console.anthropic.com](https://console.anthropic.com)

---

## Установка на Windows

### 1. Установка Python

```powershell
# Скачайте Python с официального сайта
# https://www.python.org/downloads/

# Или используйте winget
winget install Python.Python.3.12
```

### 2. Клонирование репозитория

```powershell
git clone https://github.com/yourusername/prompt-engineer-test.git
cd prompt-engineer-test
```

### 3. Создание виртуального окружения

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 4. Установка зависимостей

```powershell
# Часть 1
cd part1-classifier
pip install -r requirements.txt
cd ..

# Часть 2
cd part2-generator
pip install -r requirements.txt
cd ..
```

### 5. Настройка переменных окружения

```powershell
# Создайте файл .env в корне проекта
echo ANTHROPIC_API_KEY=your-api-key-here > .env
```

---

## Установка на macOS

### 1. Установка Python

```bash
# Используйте Homebrew
brew install python@3.12

# Или скачайте с официального сайта
# https://www.python.org/downloads/
```

### 2. Клонирование репозитория

```bash
git clone https://github.com/yourusername/prompt-engineer-test.git
cd prompt-engineer-test
```

### 3. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Установка зависимостей

```bash
# Часть 1
cd part1-classifier
pip install -r requirements.txt
cd ..

# Часть 2
cd part2-generator
pip install -r requirements.txt
cd ..
```

### 5. Настройка переменных окружения

```bash
# Создайте файл .env
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

---

## Установка на Linux (Ubuntu/Debian)

### 1. Установка Python

```bash
sudo apt update
sudo apt install python3.12 python3-pip python3-venv git
```

### 2. Клонирование репозитория

```bash
git clone https://github.com/yourusername/prompt-engineer-test.git
cd prompt-engineer-test
```

### 3. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Установка зависимостей

```bash
# Часть 1
cd part1-classifier
pip install -r requirements.txt
cd ..

# Часть 2
cd part2-generator
pip install -r requirements.txt
cd ..
```

### 5. Настройка переменных окружения

```bash
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

---

## Установка через Docker

### Dockerfile для части 2 (Генератор)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY part2-generator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY part2-generator/ .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Запуск

```bash
# Сборка образа
docker build -t ege-generator .

# Запуск контейнера
docker run -p 5000:5000 ege-generator
```

### Docker Compose

```yaml
version: '3.8'

services:
  generator:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    restart: always
```

Запуск:
```bash
docker-compose up -d
```

---

## Проверка установки

### Часть 1: Классификатор

```bash
cd part1-classifier
python classifier.py
```

Ожидаемый вывод:
```
Пример ID 1:
Оценка: 0
Объяснение: ИИ правильно применил формулу...
```

### Часть 2: Генератор

```bash
cd part2-generator
python app.py
```

Ожидаемый вывод:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Откройте браузер: `http://localhost:5000`

---

## Решение проблем

### Проблема: "ModuleNotFoundError"

```bash
# Убедитесь, что виртуальное окружение активировано
# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Переустановите зависимости
pip install -r requirements.txt
```

### Проблема: "Anthropic API key not found"

```bash
# Проверьте наличие файла .env
cat .env

# Установите переменную окружения вручную
# Windows
set ANTHROPIC_API_KEY=your-key

# macOS/Linux
export ANTHROPIC_API_KEY=your-key
```

### Проблема: "Permission denied"

```bash
# Linux/macOS
chmod +x app.py
sudo chown -R $USER:$USER .
```

### Проблема: "Port 5000 already in use"

```bash
# Найдите процесс
# Windows
netstat -ano | findstr :5000

# macOS/Linux
lsof -i :5000

# Остановите процесс или используйте другой порт
python app.py --port 5001
```

---

## Обновление

```bash
# Получите последние изменения
git pull origin main

# Обновите зависимости
pip install -r part1-classifier/requirements.txt --upgrade
pip install -r part2-generator/requirements.txt --upgrade
```

---

## Деинсталляция

```bash
# Деактивируйте виртуальное окружение
deactivate

# Удалите папку проекта
cd ..
rm -rf prompt-engineer-test
```

---

## Поддержка

Если возникли проблемы:

1. Проверьте [FAQ](FAQ.md)
2. Создайте [Issue на GitHub](https://github.com/yourusername/prompt-engineer-test/issues)
3. Напишите автору: [Telegram](https://t.me/TimXaa)
