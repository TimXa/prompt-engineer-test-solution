// Основной JavaScript для генератора задач ЕГЭ

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('generatorForm');
    const placeholder = document.getElementById('placeholder');
    const loader = document.getElementById('loader');
    const tasksContainer = document.getElementById('tasksContainer');
    const statsText = document.getElementById('statsText');

    // Обработка формы
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Получаем значения
        const count = parseInt(document.getElementById('taskCount').value);
        const difficulty = document.querySelector('input[name="difficulty"]:checked').value;
        const taskType = document.getElementById('taskType').value;

        // Валидация
        if (count < 1 || count > 20) {
            showAlert('Количество задач должно быть от 1 до 20', 'danger');
            return;
        }

        // Показываем loader
        placeholder.classList.add('d-none');
        loader.classList.remove('d-none');
        tasksContainer.innerHTML = '';

        try {
            // Отправляем запрос
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    count: count,
                    difficulty: difficulty,
                    task_type: taskType === 'all' ? null : taskType
                })
            });

            if (!response.ok) {
                throw new Error('Ошибка при генерации задач');
            }

            const data = await response.json();

            // Скрываем loader
            loader.classList.add('d-none');

            // Отображаем задачи
            displayTasks(data.tasks);

            // Обновляем статистику
            statsText.textContent = `Сгенерировано: ${data.count} задач`;

            // Добавляем кнопку печати
            addPrintButton();

        } catch (error) {
            loader.classList.add('d-none');
            showAlert('Произошла ошибка: ' + error.message, 'danger');
            console.error('Error:', error);
        }
    });

    // Отображение задач
    function displayTasks(tasks) {
        tasksContainer.innerHTML = '';

        tasks.forEach((task, index) => {
            const taskCard = createTaskCard(task, index);
            tasksContainer.appendChild(taskCard);
        });

        // Плавное появление
        setTimeout(() => {
            document.querySelectorAll('.task-card').forEach((card, index) => {
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateX(0)';
                }, index * 100);
            });
        }, 10);
    }

    // Создание карточки задачи
    function createTaskCard(task, index) {
        const card = document.createElement('div');
        card.className = `card task-card type-${task.type} shadow-sm mb-4`;
        card.style.opacity = '0';
        card.style.transform = 'translateX(-30px)';
        card.style.transition = 'all 0.5s ease';

        // Иконки для типов задач
        const typeIcons = {
            'exam_tickets': 'bi-journal-text',
            'tv_channels': 'bi-tv',
            'lottery': 'bi-ticket-perforated',
            'objects_selection': 'bi-boxes',
            'colored_balls': 'bi-circle-fill'
        };

        const icon = typeIcons[task.type] || 'bi-question-circle';

        // Названия типов
        const typeNames = {
            'exam_tickets': 'Экзаменационные билеты',
            'tv_channels': 'Телеканалы',
            'lottery': 'Лотерея',
            'objects_selection': 'Выбор объектов',
            'colored_balls': 'Цветные шары'
        };

        const typeName = typeNames[task.type] || 'Другое';

        // Сложность
        const difficultyBadges = {
            'easy': '<span class="badge bg-success">Лёгкая</span>',
            'medium': '<span class="badge bg-warning text-dark">Средняя</span>',
            'hard': '<span class="badge bg-danger">Сложная</span>'
        };

        card.innerHTML = `
            <div class="task-header">
                <div class="d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">
                        <i class="bi ${icon} me-2"></i>
                        Задача №${task.id}
                    </h5>
                    <div>
                        ${difficultyBadges[task.difficulty]}
                        <span class="badge bg-info ms-2">${typeName}</span>
                    </div>
                </div>
            </div>
            <div class="task-body">
                <!-- Условие -->
                <div class="mb-4">
                    <h6 class="text-muted mb-2">
                        <i class="bi bi-clipboard-check text-primary"></i> Условие:
                    </h6>
                    <p class="lead">${task.condition}</p>
                </div>

                <!-- Ответ -->
                <div class="answer-highlight mb-4">
                    <i class="bi bi-check-circle me-2"></i>
                    Ответ: ${task.answer_fraction} ≈ ${task.answer.toFixed(4)}
                </div>

                <!-- Решение (Accordion) -->
                <div class="accordion" id="accordion${task.id}">
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button"
                                    data-bs-toggle="collapse" data-bs-target="#solution${task.id}">
                                <i class="bi bi-book me-2"></i>
                                Показать решение
                            </button>
                        </h2>
                        <div id="solution${task.id}" class="accordion-collapse collapse"
                             data-bs-parent="#accordion${task.id}">
                            <div class="accordion-body">
                                <div class="solution-box">
                                    ${formatSolution(task.solution)}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        return card;
    }

    // Форматирование решения
    function formatSolution(solution) {
        // Разбиваем на строки и форматируем
        const lines = solution.split('\n');
        let formatted = '';

        lines.forEach(line => {
            if (line.trim().startsWith('**')) {
                // Заголовки шагов
                formatted += `<div class="fw-bold text-primary mt-3 mb-2">${line.replace(/\*\*/g, '')}</div>`;
            } else if (line.trim() !== '') {
                // Обычные строки
                formatted += `<div class="solution-step">${line}</div>`;
            } else {
                // Пустые строки
                formatted += '<div class="mb-2"></div>';
            }
        });

        return formatted;
    }

    // Добавление кнопки печати
    function addPrintButton() {
        // Удаляем старую кнопку если есть
        const oldBtn = document.querySelector('.print-btn');
        if (oldBtn) oldBtn.remove();

        const printBtn = document.createElement('button');
        printBtn.className = 'print-btn';
        printBtn.innerHTML = '<i class="bi bi-printer"></i>';
        printBtn.title = 'Распечатать задачи';
        printBtn.addEventListener('click', () => window.print());

        document.body.appendChild(printBtn);
    }

    // Показать alert
    function showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    // Плавная прокрутка к якорям
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Анимация при прокрутке
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
            }
        });
    }, observerOptions);

    // Наблюдаем за карточками в секции "О проекте"
    document.querySelectorAll('#about .card').forEach(card => {
        observer.observe(card);
    });
});
