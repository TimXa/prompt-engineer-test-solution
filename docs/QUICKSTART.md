
Быстрый старт для работы с проектом.

---

## За 5 минут

### Шаг 1: Установка

```bash
# Клонируйте репозиторий
git clone https://github.com/yourusername/prompt-engineer-test.git
cd prompt-engineer-test

# Создайте виртуальное окружение
python -m venv venv

# Активируйте (выберите вашу ОС)
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Шаг 2: Установите зависимости

```bash
# Для части 1 (Классификатор)
pip install anthropic python-dotenv pandas scikit-learn

# Для части 2 (Генератор)
pip install Flask gunicorn
```

### Шаг 3: Настройте API ключ (только для части 1)

```bash
# Создайте файл .env
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### Шаг 4: Запустите

#### Часть 1: Классификатор

```bash
cd part1-classifier
python classifier.py
```

#### Часть 2: Генератор

```bash
cd part2-generator
python app.py
# Откройте http://localhost:5000
```

---

## Примеры использования

### Классификация математических ошибок

```python
from part1_classifier.classifier import MathErrorClassifier

classifier = MathErrorClassifier()

result = classifier.classify(
    task_text="Найдите производную x²",
    dialogue_history="Ученик: Как решить?",
    ai_response="Производная x² равна 2x"
)

print(result['assessment'])  # 0 (правильно)
```

### Генерация задач ЕГЭ

```python
from part2_generator.src.generator import ProbabilityTaskGenerator

gen = ProbabilityTaskGenerator()
task = gen.generate_task(difficulty="medium")

print(task['condition'])
print(f"Ответ: {task['answer']}")
```

---

## Веб-интерфейс

Самый простой способ использовать генератор - через веб-интерфейс:

1. Запустите: `python part2-generator/app.py`
2. Откройте: `http://localhost:5000`
3. Выберите параметры и нажмите "Сгенерировать"

---

## Основные команды

```bash
# Активация окружения
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Запуск классификатора
python part1-classifier/classifier.py

# Запуск генератора
python part2-generator/app.py

# Деактивация окружения
deactivate
```

---

## Что дальше?

- 📖 [Полная документация](README.md)
- 🔧 [Подробная установка](docs/INSTALLATION.md)
- 🤔 [FAQ](docs/FAQ.md)
- 💡 [Примеры](docs/EXAMPLES.md)

---

## ❓ Проблемы?

**ModuleNotFoundError?**
```bash
pip install -r part1-classifier/requirements.txt
pip install -r part2-generator/requirements.txt
```

**Port 5000 занят?**
```bash
python app.py --port 5001
```

**Anthropic API key не работает?**
```bash
export ANTHROPIC_API_KEY="your-key"
```

---

**Готово!** 🎉 Теперь вы можете использовать проект.
