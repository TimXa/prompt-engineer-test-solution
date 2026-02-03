"""
Flask веб-приложение для генератора задач ЕГЭ
"""

from flask import Flask, render_template, request, jsonify
import sys
sys.path.append('src')
from generator import ProbabilityTaskGenerator

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Глобальный экземпляр генератора
generator = ProbabilityTaskGenerator()


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def generate_tasks():
    """API endpoint для генерации задач"""
    try:
        data = request.get_json()

        count = int(data.get('count', 1))
        difficulty = data.get('difficulty', 'medium')
        task_type = data.get('task_type', None)

        # Валидация
        if count < 1 or count > 20:
            return jsonify({'error': 'Количество задач должно быть от 1 до 20'}), 400

        if difficulty not in ['easy', 'medium', 'hard']:
            return jsonify({'error': 'Неверная сложность'}), 400

        # Генерация задач
        tasks = generator.generate_batch(count, task_type, difficulty)

        return jsonify({
            'success': True,
            'tasks': tasks,
            'count': len(tasks)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/task-types', methods=['GET'])
def get_task_types():
    """Возвращает список доступных типов задач"""
    task_types = {
        'all': 'Все типы (случайный выбор)',
        'exam_tickets': 'Экзаменационные билеты',
        'tv_channels': 'Телевизионные каналы',
        'lottery': 'Лотереи и розыгрыши',
        'objects_selection': 'Выбор объектов',
        'colored_balls': 'Цветные шары'
    }

    return jsonify({
        'success': True,
        'task_types': task_types
    })


if __name__ == '__main__':
    # В продакшене использовать gunicorn или другой WSGI сервер
    app.run(debug=True, host='0.0.0.0', port=5000)
