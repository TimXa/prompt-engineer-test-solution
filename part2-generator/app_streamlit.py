"""
Streamlit веб-приложение для генератора задач ЕГЭ №5
Простое и быстрое прототипирование
"""

import streamlit as st
import sys
sys.path.append('src')
from generator import ProbabilityTaskGenerator

# Настройка страницы
st.set_page_config(
    page_title="Генератор задач ЕГЭ №5",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомные стили
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .task-card {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .answer-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1rem 0;
    }
    .solution-box {
        background: #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок
st.markdown('<h1 class="main-header">🎓 Генератор задач ЕГЭ №5</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #6c757d; font-size: 1.1rem;">Теория вероятностей | База 2026</p>', unsafe_allow_html=True)

st.markdown("---")

# Боковая панель с настройками
with st.sidebar:
    st.header("⚙️ Настройки генерации")

    # Количество задач
    count = st.slider(
        "Количество задач",
        min_value=1,
        max_value=20,
        value=3,
        help="Выберите сколько задач сгенерировать (от 1 до 20)"
    )

    # Сложность
    difficulty = st.select_slider(
        "Сложность",
        options=["easy", "medium", "hard"],
        value="medium",
        format_func=lambda x: {"easy": "🟢 Лёгкая", "medium": "🟡 Средняя", "hard": "🔴 Сложная"}[x],
        help="Выберите уровень сложности задач"
    )

    # Тип задачи
    task_type_options = {
        "Все типы (случайно)": None,
        "Экзаменационные билеты": "exam_tickets",
        "Телеканалы": "tv_channels",
        "Лотереи": "lottery",
        "Выбор объектов": "objects_selection",
        "Цветные шары": "colored_balls"
    }

    task_type_label = st.selectbox(
        "Тип задачи",
        options=list(task_type_options.keys()),
        help="Выберите тип задачи или оставьте случайный выбор"
    )
    task_type = task_type_options[task_type_label]

    st.markdown("---")

    # Кнопка генерации
    generate_button = st.button(
        "🎲 Сгенерировать задачи",
        type="primary",
        use_container_width=True
    )

    st.markdown("---")

    # Информация
    st.info("""
    **О генераторе:**

    - 5 типов задач
    - 3 уровня сложности
    - Алгоритмическая генерация
    - Пошаговые решения
    """)

# Инициализация генератора
@st.cache_resource
def get_generator():
    return ProbabilityTaskGenerator()

generator = get_generator()

# Основная область
if generate_button:
    with st.spinner('Генерируем задачи...'):
        # Генерация задач
        tasks = generator.generate_batch(count, task_type, difficulty)

        # Отображение задач
        st.success(f'✅ Сгенерировано задач: {len(tasks)}')

        for task in tasks:
            # Карточка задачи
            st.markdown(f'<div class="task-card">', unsafe_allow_html=True)

            # Заголовок задачи
            type_icons = {
                'exam_tickets': '📚',
                'tv_channels': '📺',
                'lottery': '🎰',
                'objects_selection': '🎴',
                'colored_balls': '⚽'
            }
            type_names = {
                'exam_tickets': 'Экзаменационные билеты',
                'tv_channels': 'Телеканалы',
                'lottery': 'Лотерея',
                'objects_selection': 'Выбор объектов',
                'colored_balls': 'Цветные шары'
            }

            icon = type_icons.get(task['type'], '📝')
            type_name = type_names.get(task['type'], 'Другое')

            st.markdown(f"### {icon} Задача №{task['id']} — {type_name}")

            # Сложность
            difficulty_badges = {
                'easy': '🟢 Лёгкая',
                'medium': '🟡 Средняя',
                'hard': '🔴 Сложная'
            }
            st.caption(difficulty_badges[task['difficulty']])

            # Условие
            st.markdown("**📋 Условие:**")
            st.markdown(task['condition'])

            # Ответ
            st.markdown(
                f'<div class="answer-box">✅ Ответ: {task["answer_fraction"]} ≈ {task["answer"]:.4f}</div>',
                unsafe_allow_html=True
            )

            # Решение (expandable)
            with st.expander("📖 Показать решение"):
                st.markdown('<div class="solution-box">', unsafe_allow_html=True)

                # Форматируем решение
                solution_lines = task['solution'].split('\n')
                for line in solution_lines:
                    if line.strip().startswith('**'):
                        # Заголовок шага
                        st.markdown(f"**{line.strip().replace('**', '')}**")
                    elif line.strip():
                        # Обычная строка
                        st.write(f"• {line.strip()}")

                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

else:
    # Placeholder когда задачи не сгенерированы
    st.info("👈 Выберите настройки в боковой панели и нажмите **'Сгенерировать задачи'**")

    # Пример задачи
    with st.expander("💡 Пример сгенерированной задачи"):
        example = generator.generate_task(difficulty="medium")

        st.markdown("**Условие:**")
        st.write(example['condition'])

        st.markdown(f"**Ответ:** {example['answer_fraction']} ≈ {example['answer']:.4f}")

        st.markdown("**Решение:**")
        st.code(example['solution'], language=None)

# Футер
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Технологии:**")
    st.caption("Python, Streamlit, Fractions")

with col2:
    st.markdown("**Автор:**")
    st.caption("[TimXa](https://github.com/TimXa)")

with col3:
    st.markdown("**Репозиторий:**")
    st.caption("[GitHub](https://github.com/TimXa/prompt-engineer-test-solution)")
