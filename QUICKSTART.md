# Быстрый старт

## Часть 1: Промпт-классификатор математических ошибок

### Запуск классификации

```bash
cd part1-classifier
pip install -r requirements.txt
python classifier.py
```

### Автоматическая разметка 45 примеров

```bash
python run_annotation.py
```

Результаты сохраняются в:
- `results_deepseek.json` - полные результаты в JSON
- `results_table_deepseek.md` - таблица с результатами

### Использование универсального классификатора

```python
from universal_classifier import UniversalMathErrorClassifier

# С Deepseek через Artemox прокси
classifier = UniversalMathErrorClassifier(
    provider='deepseek',
    api_key='YOUR_KEY',
    base_url='https://api.artemox.com/v1'
)

# Или с Claude
classifier = UniversalMathErrorClassifier(
    provider='claude',
    api_key='YOUR_CLAUDE_KEY'
)

# Классификация
result = classifier.classify(
    task_text="Найдите производную f(x) = x^2",
    dialogue_history="",
    ai_response="Производная равна 2x"
)

print(f"Оценка: {result['assessment']}")  # 0 или 1
print(f"Обоснование: {result['reasoning']}")
```

## Часть 2: Генератор задач ЕГЭ №5

### Запуск Streamlit приложения (рекомендуется)

```bash
cd part2-generator
pip install -r requirements.txt
streamlit run app_streamlit.py
```

Откроется веб-интерфейс в браузере.

### Запуск Flask приложения

```bash
python app.py
```

Откройте `http://localhost:5000` в браузере.

### Использование генератора в коде

```python
from src.generator import ProbabilityTaskGenerator

gen = ProbabilityTaskGenerator()

# Генерация одной задачи
task = gen.generate_task('exam_tickets', 'medium')
print(task['condition'])
print(task['answer'])

# Пакетная генерация
tasks = gen.generate_batch(count=10, task_type='lottery', difficulty='easy')
```

## Доступные типы задач

1. `exam_tickets` - Экзаменационные билеты
2. `tv_channels` - Телеканалы и передачи
3. `lottery` - Лотереи и розыгрыши
4. `objects_selection` - Выбор объектов
5. `colored_balls` - Цветные шары

## Уровни сложности

- `easy` - Простые (небольшие числа)
- `medium` - Средние
- `hard` - Сложные (большие числа, дроби)

## Метрики классификатора

После разметки автоматически рассчитываются:
- **Accuracy** - общая точность
- **Precision** - точность определения ошибок
- **Recall** - полнота определения ошибок
- **F1-Score** - гармоническое среднее
- **Confusion Matrix** - матрица ошибок

## Требования

- Python 3.8+
- API ключ Deepseek/Claude/OpenAI
- Все зависимости в `requirements.txt`
