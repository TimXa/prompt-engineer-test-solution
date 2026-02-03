"""
Алгоритмический генератор задач ЕГЭ №5 (теория вероятностей)
Не использует нейросети в рантайме - только чистые алгоритмы
"""

import random
from typing import Dict, List, Tuple
from fractions import Fraction


class ProbabilityTaskGenerator:
    """Генератор задач по теории вероятностей для ЕГЭ (задание №5)"""

    def __init__(self, seed: int = None):
        """
        Инициализация генератора

        Args:
            seed: Seed для воспроизводимости результатов
        """
        if seed is not None:
            random.seed(seed)

        # Шаблоны задач разных типов
        self.task_templates = {
            "exam_tickets": self._generate_exam_tickets,
            "tv_channels": self._generate_tv_channels,
            "lottery": self._generate_lottery,
            "objects_selection": self._generate_objects_selection,
            "colored_balls": self._generate_colored_balls,
        }

        # Имена для разнообразия
        self.names = [
            "Андрей", "Маша", "Дима", "Катя", "Олег", "Аня", "Сергей", "Лена",
            "Максим", "Вика", "Артём", "Даша", "Никита", "Соня"
        ]

    def _generate_exam_tickets(self, difficulty: str = "medium") -> Dict:
        """Генерирует задачу про экзаменационные билеты"""

        if difficulty == "easy":
            total_tickets = random.choice([10, 12, 15, 20])
            unstudied = random.randint(1, min(3, total_tickets - 1))
        elif difficulty == "medium":
            total_tickets = random.choice([20, 24, 25, 30, 40])
            unstudied = random.randint(2, min(6, total_tickets - 2))
        else:  # hard
            total_tickets = random.choice([50, 60, 80, 100])
            unstudied = random.randint(5, min(15, total_tickets - 5))

        studied = total_tickets - unstudied
        name = random.choice(self.names)

        # Формируем условие
        condition = (
            f"На экзамене {total_tickets} вопросов. {name} не выучил(а) {unstudied} из них. "
            f"Найдите вероятность того, что ему достанется выученный вопрос."
        )

        # Решение пошагово
        solution_steps = [
            f"**Шаг 1:** Определяем общее количество возможных исходов",
            f"Всего вопросов: {total_tickets}",
            f"",
            f"**Шаг 2:** Определяем количество благоприятных исходов",
            f"Выученных вопросов: {total_tickets} - {unstudied} = {studied}",
            f"",
            f"**Шаг 3:** Вычисляем вероятность по формуле P = m/n",
            f"где m - число благоприятных исходов, n - число всех возможных исходов",
            f"",
            f"P = {studied}/{total_tickets}",
        ]

        # Упрощаем дробь
        fraction = Fraction(studied, total_tickets)
        answer = float(fraction)

        if fraction.denominator != 1 and fraction != Fraction(studied, total_tickets):
            solution_steps.append(f"P = {fraction.numerator}/{fraction.denominator}")

        if fraction.denominator != 1:
            solution_steps.append(f"P = {answer:.4f}")

        return {
            "condition": condition,
            "answer": answer,
            "answer_fraction": f"{fraction.numerator}/{fraction.denominator}",
            "solution": "\n".join(solution_steps),
            "type": "exam_tickets",
            "difficulty": difficulty
        }

    def _generate_tv_channels(self, difficulty: str = "medium") -> Dict:
        """Генерирует задачу про телевизионные каналы"""

        if difficulty == "easy":
            total_channels = random.choice([10, 12, 15, 20])
            thematic = random.randint(2, min(5, total_channels - 1))
        elif difficulty == "medium":
            total_channels = random.choice([30, 40, 45, 50])
            thematic = random.randint(5, min(15, total_channels - 5))
        else:  # hard
            total_channels = random.choice([60, 80, 100, 120])
            thematic = random.randint(10, min(30, total_channels - 10))

        name = random.choice(self.names)
        theme = random.choice([
            "новости", "спортивные программы", "детские передачи",
            "музыкальные каналы", "познавательные программы", "фильмы"
        ])

        event_type = random.choice(["попадёт", "не попадёт"])

        if event_type == "попадёт":
            favorable = thematic
            condition = (
                f"{name} включает телевизор на случайном канале. "
                f"Всего телевизор показывает {total_channels} каналов, из них {thematic} показывают {theme}. "
                f"Найдите вероятность того, что телевизор окажется настроен на канал, показывающий {theme}."
            )
        else:
            favorable = total_channels - thematic
            condition = (
                f"{name} включает телевизор на случайном канале. "
                f"Всего телевизор показывает {total_channels} каналов, из них {thematic} показывают {theme}. "
                f"Найдите вероятность того, что телевизор окажется настроен на канал, НЕ показывающий {theme}."
            )

        solution_steps = [
            f"**Шаг 1:** Определяем общее количество возможных исходов",
            f"Всего каналов: {total_channels}",
            f"",
            f"**Шаг 2:** Определяем количество благоприятных исходов",
        ]

        if event_type == "попадёт":
            solution_steps.append(f"Каналов с тематикой '{theme}': {thematic}")
            solution_steps.append(f"Благоприятных исходов: {favorable}")
        else:
            solution_steps.append(f"Каналов с тематикой '{theme}': {thematic}")
            solution_steps.append(f"Каналов БЕЗ этой тематики: {total_channels} - {thematic} = {favorable}")

        solution_steps.extend([
            f"",
            f"**Шаг 3:** Вычисляем вероятность по формуле P = m/n",
            f"P = {favorable}/{total_channels}",
        ])

        fraction = Fraction(favorable, total_channels)
        answer = float(fraction)

        if fraction.denominator != 1 and fraction != Fraction(favorable, total_channels):
            solution_steps.append(f"P = {fraction.numerator}/{fraction.denominator}")

        if fraction.denominator != 1:
            solution_steps.append(f"P = {answer:.4f}")

        return {
            "condition": condition,
            "answer": answer,
            "answer_fraction": f"{fraction.numerator}/{fraction.denominator}",
            "solution": "\n".join(solution_steps),
            "type": "tv_channels",
            "difficulty": difficulty
        }

    def _generate_lottery(self, difficulty: str = "medium") -> Dict:
        """Генерирует задачу про лотерею или розыгрыш"""

        if difficulty == "easy":
            total_tickets = random.choice([10, 15, 20, 25])
            winning = random.randint(1, min(5, total_tickets - 1))
        elif difficulty == "medium":
            total_tickets = random.choice([50, 100, 200, 250])
            winning = random.randint(5, min(30, total_tickets - 5))
        else:  # hard
            total_tickets = random.choice([500, 1000, 2000])
            winning = random.randint(10, min(100, total_tickets - 10))

        name = random.choice(self.names)
        prize = random.choice(["приз", "выигрышный билет", "подарок", "сертификат"])

        condition = (
            f"В лотерее {total_tickets} билетов, из них {winning} выигрышных. "
            f"{name} покупает один билет. Найдите вероятность того, что он окажется выигрышным."
        )

        solution_steps = [
            f"**Шаг 1:** Определяем общее количество возможных исходов",
            f"Всего билетов в лотерее: {total_tickets}",
            f"",
            f"**Шаг 2:** Определяем количество благоприятных исходов",
            f"Выигрышных билетов: {winning}",
            f"",
            f"**Шаг 3:** Вычисляем вероятность по формуле P = m/n",
            f"P = {winning}/{total_tickets}",
        ]

        fraction = Fraction(winning, total_tickets)
        answer = float(fraction)

        if fraction.denominator != 1 and fraction != Fraction(winning, total_tickets):
            solution_steps.append(f"P = {fraction.numerator}/{fraction.denominator}")

        if fraction.denominator != 1:
            solution_steps.append(f"P = {answer:.4f}")

        return {
            "condition": condition,
            "answer": answer,
            "answer_fraction": f"{fraction.numerator}/{fraction.denominator}",
            "solution": "\n".join(solution_steps),
            "type": "lottery",
            "difficulty": difficulty
        }

    def _generate_objects_selection(self, difficulty: str = "medium") -> Dict:
        """Генерирует задачу про выбор объектов (карты, номера и т.д.)"""

        objects = [
            ("карт", "колоде", "красная карта", 26, 52),
            ("карт", "колоде", "карта пиковой масти", 13, 52),
            ("дней", "году", "будний день", 250, 365),
            ("деталей", "партии", "бракованная деталь", None, None),
        ]

        obj_data = random.choice(objects)
        obj_name, location, favorable_name, fav_count_preset, total_preset = obj_data

        if total_preset is None:
            if difficulty == "easy":
                total = random.choice([20, 25, 30, 40])
                favorable_count = random.randint(2, min(8, total - 2))
            elif difficulty == "medium":
                total = random.choice([50, 80, 100, 150])
                favorable_count = random.randint(5, min(25, total - 5))
            else:
                total = random.choice([200, 300, 500])
                favorable_count = random.randint(10, min(50, total - 10))
        else:
            total = total_preset
            favorable_count = fav_count_preset

        condition = (
            f"В {location} {total} {obj_name}, из них {favorable_count} — {favorable_name}. "
            f"Случайным образом выбирается одна единица. Найдите вероятность того, что это будет {favorable_name}."
        )

        solution_steps = [
            f"**Шаг 1:** Определяем общее количество возможных исходов",
            f"Всего {obj_name}: {total}",
            f"",
            f"**Шаг 2:** Определяем количество благоприятных исходов",
            f"Количество '{favorable_name}': {favorable_count}",
            f"",
            f"**Шаг 3:** Вычисляем вероятность",
            f"P = {favorable_count}/{total}",
        ]

        fraction = Fraction(favorable_count, total)
        answer = float(fraction)

        if fraction.denominator != 1:
            solution_steps.append(f"P = {fraction.numerator}/{fraction.denominator}")
            solution_steps.append(f"P = {answer:.4f}")

        return {
            "condition": condition,
            "answer": answer,
            "answer_fraction": f"{fraction.numerator}/{fraction.denominator}",
            "solution": "\n".join(solution_steps),
            "type": "objects_selection",
            "difficulty": difficulty
        }

    def _generate_colored_balls(self, difficulty: str = "medium") -> Dict:
        """Генерирует задачу про цветные шары в коробке"""

        colors = ["красных", "синих", "зелёных", "жёлтых", "белых", "чёрных"]

        if difficulty == "easy":
            num_colors = 2
            total_balls = random.choice([10, 12, 15, 20])
        elif difficulty == "medium":
            num_colors = random.choice([2, 3])
            total_balls = random.choice([20, 24, 30, 40])
        else:
            num_colors = random.choice([3, 4])
            total_balls = random.choice([50, 60, 80, 100])

        selected_colors = random.sample(colors, num_colors)
        color_counts = []

        remaining = total_balls
        for i in range(num_colors - 1):
            count = random.randint(1, remaining - (num_colors - i - 1))
            color_counts.append(count)
            remaining -= count
        color_counts.append(remaining)

        target_color_idx = random.randint(0, num_colors - 1)
        target_color = selected_colors[target_color_idx]
        target_count = color_counts[target_color_idx]

        color_description = ", ".join(
            f"{count} {color}" for count, color in zip(color_counts, selected_colors)
        )

        condition = (
            f"В коробке лежат {total_balls} шаров: {color_description}. "
            f"Случайным образом достаётся один шар. Найдите вероятность того, что он будет {target_color[:-2]}им."
        )

        solution_steps = [
            f"**Шаг 1:** Определяем общее количество возможных исходов",
            f"Всего шаров: {total_balls}",
            f"",
            f"**Шаг 2:** Определяем количество благоприятных исходов",
            f"{target_color.capitalize()} шаров: {target_count}",
            f"",
            f"**Шаг 3:** Вычисляем вероятность",
            f"P = {target_count}/{total_balls}",
        ]

        fraction = Fraction(target_count, total_balls)
        answer = float(fraction)

        if fraction.denominator != 1:
            solution_steps.append(f"P = {fraction.numerator}/{fraction.denominator}")
            solution_steps.append(f"P = {answer:.4f}")

        return {
            "condition": condition,
            "answer": answer,
            "answer_fraction": f"{fraction.numerator}/{fraction.denominator}",
            "solution": "\n".join(solution_steps),
            "type": "colored_balls",
            "difficulty": difficulty
        }

    def generate_task(self, task_type: str = None, difficulty: str = "medium") -> Dict:
        """
        Генерирует одну задачу

        Args:
            task_type: Тип задачи (exam_tickets, tv_channels, lottery, objects_selection, colored_balls)
                      Если None - выбирается случайно
            difficulty: Сложность (easy, medium, hard)

        Returns:
            Dict с полями: condition, answer, answer_fraction, solution, type, difficulty
        """
        if task_type is None:
            task_type = random.choice(list(self.task_templates.keys()))

        if task_type not in self.task_templates:
            raise ValueError(f"Неизвестный тип задачи: {task_type}")

        return self.task_templates[task_type](difficulty)

    def generate_batch(self, count: int, task_type: str = None, difficulty: str = "medium") -> List[Dict]:
        """
        Генерирует пакет задач

        Args:
            count: Количество задач
            task_type: Тип задачи (если None - случайный микс)
            difficulty: Сложность

        Returns:
            Список задач
        """
        tasks = []
        for i in range(count):
            task = self.generate_task(task_type, difficulty)
            task["id"] = i + 1
            tasks.append(task)
        return tasks


# Пример использования
if __name__ == "__main__":
    import sys
    import io

    # Установка UTF-8 кодировки для вывода в консоль
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    generator = ProbabilityTaskGenerator(seed=42)

    print("=" * 80)
    print("ПРИМЕР СГЕНЕРИРОВАННЫХ ЗАДАЧ")
    print("=" * 80)

    for i in range(3):
        task = generator.generate_task(difficulty="medium")
        print(f"\nЗАДАЧА #{i + 1} (Тип: {task['type']})")
        print(f"\n{task['condition']}")
        print(f"\nОТВЕТ: {task['answer_fraction']} = {task['answer']:.4f}")
        print(f"\nРЕШЕНИЕ:\n{task['solution']}")
        print("\n" + "-" * 80)
