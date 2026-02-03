"""
Классификатор математических ошибок репетитора
Использует Claude Sonnet 4.5 для анализа ответов ИИ
"""

import json
import os
from typing import Dict, List, Tuple
from anthropic import Anthropic

# Промпт-шаблон для классификации
CLASSIFICATION_PROMPT = """Ты — эксперт по проверке математической корректности ответов ИИ-репетитора.

ЗАДАЧА: Оцени последнюю реплику ИИ-репетитора на наличие математических ошибок.

КОНТЕКСТ:
- Текст задачи: {task_text}
- История диалога: {dialogue_history}
- Последняя реплика ИИ для оценки: {ai_response}

КРИТЕРИИ ОЦЕНКИ:

ОШИБКА (1) — ставь ТОЛЬКО если ИИ-репетитор:
✗ Самостоятельно выполняет неверное математическое вычисление
✗ Дает неверную формулу или определение
✗ Делает ошибочное преобразование выражения
✗ Совершает логическую ошибку в рассуждениях
✗ Утверждает неверный математический факт

НЕ ОШИБКА (0) — ставь если ИИ-репетитор:
✓ Просто оценивает ответ ученика (даже если оценка неточная)
✓ Задает наводящие вопросы
✓ Повторяет неверный результат из предыдущих реплик ученика БЕЗ собственных вычислений
✓ Дает общие указания без конкретных неверных математических действий
✓ Делает опечатку в словах (не в числах/формулах)
✓ Перефразирует или цитирует предыдущие ошибки из истории

ВАЖНО:
1. Анализируй ТОЛЬКО последнюю реплику ИИ относительно последней реплики ученика
2. Проверяй математическую корректность именно действий ИИ, а не ученика
3. Если ИИ согласился с неверным ответом ученика БЕЗ собственных вычислений — это НЕ ошибка
4. Если ИИ САМ произвел неверное вычисление — это ОШИБКА

ФОРМАТ ОТВЕТА (строгий JSON):
{{
  "assessment": 0,
  "reasoning": "Краткое объяснение: что именно проверялось и почему поставлена такая оценка",
  "error_type": null
}}

где assessment: 0 или 1, error_type: "вычислительная"/"формула"/"логическая"/"определение" или null

ВЫПОЛНИ ОЦЕНКУ:"""


class MathErrorClassifier:
    """Классификатор математических ошибок с использованием Claude API"""

    def __init__(self, api_key: str = None):
        """
        Инициализация классификатора

        Args:
            api_key: API ключ Anthropic (если None, берется из переменной окружения)
        """
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-5-20250929"

    def classify(self, task_text: str, dialogue_history: str, ai_response: str) -> Dict:
        """
        Классифицирует ответ репетитора

        Args:
            task_text: Текст задачи
            dialogue_history: История диалога
            ai_response: Ответ ИИ для проверки

        Returns:
            Dict с полями: assessment (0/1), reasoning, error_type
        """
        prompt = CLASSIFICATION_PROMPT.format(
            task_text=task_text,
            dialogue_history=dialogue_history,
            ai_response=ai_response
        )

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text.strip()

            # Попытка извлечь JSON из ответа
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                response_text = response_text[json_start:json_end]

            result = json.loads(response_text)

            # Валидация результата
            if "assessment" not in result:
                raise ValueError("Missing 'assessment' field in response")
            if result["assessment"] not in [0, 1]:
                raise ValueError(f"Invalid assessment value: {result['assessment']}")

            return result

        except Exception as e:
            print(f"Ошибка при классификации: {e}")
            return {
                "assessment": -1,
                "reasoning": f"Ошибка обработки: {str(e)}",
                "error_type": None
            }

    def classify_batch(self, examples: List[Dict]) -> List[Dict]:
        """
        Классифицирует пакет примеров

        Args:
            examples: Список словарей с полями task_text, dialogue_history, ai_response, id

        Returns:
            Список результатов классификации
        """
        results = []

        for i, example in enumerate(examples, 1):
            print(f"Обработка примера {i}/{len(examples)} (ID: {example.get('id', 'unknown')})")

            result = self.classify(
                task_text=example["task_text"],
                dialogue_history=example["dialogue_history"],
                ai_response=example["ai_response"]
            )

            results.append({
                "id": example.get("id", i),
                "assessment": result["assessment"],
                "reasoning": result["reasoning"],
                "error_type": result.get("error_type"),
                "original_data": example
            })

        return results


def calculate_metrics(predictions: List[int], ground_truth: List[int]) -> Dict:
    """
    Рассчитывает метрики качества классификации

    Args:
        predictions: Предсказания модели (0 или 1)
        ground_truth: Правильные ответы (0 или 1)

    Returns:
        Dict с метриками: accuracy, precision, recall, f1_score, confusion_matrix
    """
    if len(predictions) != len(ground_truth):
        raise ValueError("Длины списков не совпадают")

    # Confusion matrix
    tp = sum(1 for p, g in zip(predictions, ground_truth) if p == 1 and g == 1)
    tn = sum(1 for p, g in zip(predictions, ground_truth) if p == 0 and g == 0)
    fp = sum(1 for p, g in zip(predictions, ground_truth) if p == 1 and g == 0)
    fn = sum(1 for p, g in zip(predictions, ground_truth) if p == 0 and g == 1)

    # Метрики
    accuracy = (tp + tn) / len(predictions) if len(predictions) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "confusion_matrix": {
            "true_positive": tp,
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn
        }
    }


def save_results(results: List[Dict], metrics: Dict, output_file: str):
    """Сохраняет результаты в JSON файл"""
    output = {
        "model": "claude-sonnet-4-5-20250929",
        "metrics": metrics,
        "results": results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nРезультаты сохранены в {output_file}")


# Пример использования
if __name__ == "__main__":
    # Пример данных для тестирования
    example_data = [
        {
            "id": 1,
            "task_text": "Вычислите площадь круга радиусом 5",
            "dialogue_history": "Ученик: Как найти площадь круга?",
            "ai_response": "Площадь круга вычисляется по формуле S = πr². Для радиуса 5: S = 3.14 × 5² = 3.14 × 25 = 78.5"
        }
    ]

    # Инициализация классификатора
    classifier = MathErrorClassifier()

    # Классификация
    results = classifier.classify_batch(example_data)

    # Вывод результатов
    for result in results:
        print(f"\nПример ID {result['id']}:")
        print(f"Оценка: {result['assessment']}")
        print(f"Объяснение: {result['reasoning']}")
        if result['error_type']:
            print(f"Тип ошибки: {result['error_type']}")
