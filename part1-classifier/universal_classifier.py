"""
Универсальный классификатор математических ошибок
Поддерживает: Claude, Deepseek, OpenAI GPT, и любые OpenAI-compatible API
"""

import json
import os
from typing import Dict, List
from enum import Enum


class LLMProvider(Enum):
    """Поддерживаемые LLM провайдеры"""
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    CUSTOM = "custom"


# Промпт-шаблон для классификации (универсальный для всех моделей)
CLASSIFICATION_PROMPT = """Ты — эксперт по проверке математической корректности ответов ИИ-репетитора.

ЗАДАЧА: Оцени последнюю реплику ИИ-репетитора на наличие математических ошибок.

КОНТЕКСТ:
- Текст задачи: {task_text}
- История диалога: {dialogue_history}
- Последняя реплика ИИ для оценки: {ai_response}

КРИТЕРИИ ОЦЕНКИ:

ОШИБКА (1) — ставь ТОЛЬКО если ИИ-репетитор:
[X] Самостоятельно выполняет неверное математическое вычисление
[X] Дает неверную формулу или определение
[X] Делает ошибочное преобразование выражения
[X] Совершает логическую ошибку в рассуждениях
[X] Утверждает неверный математический факт

НЕ ОШИБКА (0) — ставь если ИИ-репетитор:
[OK] Просто оценивает ответ ученика (даже если оценка неточная)
[OK] Задает наводящие вопросы
[OK] Повторяет неверный результат из предыдущих реплик ученика БЕЗ собственных вычислений
[OK] Дает общие указания без конкретных неверных математических действий
[OK] Делает опечатку в словах (не в числах/формулах)
[OK] Перефразирует или цитирует предыдущие ошибки из истории

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


class UniversalMathErrorClassifier:
    """Универсальный классификатор для разных LLM провайдеров"""

    def __init__(self, provider: str = "deepseek", api_key: str = None, model: str = None, base_url: str = None):
        """
        Инициализация классификатора

        Args:
            provider: Провайдер LLM (claude, deepseek, openai, custom)
            api_key: API ключ (если None, берется из переменной окружения)
            model: Название модели (если None, используется default для провайдера)
            base_url: Custom base URL для API (для прокси или альтернативных endpoints)
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = None

        self._init_client()

    def _init_client(self):
        """Инициализация клиента в зависимости от провайдера"""

        if self.provider == "claude":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key or os.environ.get("ANTHROPIC_API_KEY"))
            self.model = self.model or "claude-sonnet-4-5-20250929"
            self.provider_type = LLMProvider.CLAUDE

        elif self.provider == "deepseek":
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key or os.environ.get("DEEPSEEK_API_KEY"),
                base_url=self.base_url or "https://api.deepseek.com"
            )
            self.model = self.model or "deepseek-chat"
            self.provider_type = LLMProvider.DEEPSEEK

        elif self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key or os.environ.get("OPENAI_API_KEY"))
            self.model = self.model or "gpt-4o"
            self.provider_type = LLMProvider.OPENAI

        else:
            raise ValueError(f"Неизвестный провайдер: {self.provider}. "
                           f"Поддерживаются: claude, deepseek, openai")

        print(f"[OK] Инициализирован {self.provider.upper()} с моделью {self.model}")

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
            if self.provider_type == LLMProvider.CLAUDE:
                response = self._classify_claude(prompt)
            else:
                response = self._classify_openai_compatible(prompt)

            # Парсинг JSON ответа
            result = self._parse_response(response)
            return result

        except Exception as e:
            print(f"Ошибка при классификации: {e}")
            return {
                "assessment": -1,
                "reasoning": f"Ошибка обработки: {str(e)}",
                "error_type": None
            }

    def _classify_claude(self, prompt: str) -> str:
        """Классификация через Claude API"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()

    def _classify_openai_compatible(self, prompt: str) -> str:
        """Классификация через OpenAI-compatible API (Deepseek, OpenAI, и т.д.)"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    def _parse_response(self, response_text: str) -> Dict:
        """Парсинг JSON ответа от модели"""
        # Попытка извлечь JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "{" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            response_text = response_text[json_start:json_end]

        result = json.loads(response_text)

        # Валидация
        if "assessment" not in result:
            raise ValueError("Missing 'assessment' field in response")
        if result["assessment"] not in [0, 1]:
            raise ValueError(f"Invalid assessment value: {result['assessment']}")

        return result

    def classify_batch(self, examples: List[Dict], verbose: bool = True) -> List[Dict]:
        """
        Классифицирует пакет примеров

        Args:
            examples: Список словарей с полями task_text, dialogue_history, ai_response, id
            verbose: Выводить прогресс

        Returns:
            Список результатов классификации
        """
        results = []

        for i, example in enumerate(examples, 1):
            if verbose:
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


# Пример использования
if __name__ == "__main__":
    print("=" * 80)
    print("УНИВЕРСАЛЬНЫЙ КЛАССИФИКАТОР МАТЕМАТИЧЕСКИХ ОШИБОК")
    print("=" * 80)
    print("\nПоддерживаемые провайдеры:")
    print("- Claude (claude-sonnet-4-5)")
    print("- Deepseek (deepseek-chat)")
    print("- OpenAI (gpt-4o)")
    print("=" * 80)

    # Пример с Deepseek
    example_data = {
        "task_text": "Вычислите площадь круга радиусом 5",
        "dialogue_history": "Ученик: Как найти площадь круга?",
        "ai_response": "Площадь круга вычисляется по формуле S = πr². Для радиуса 5: S = 3.14 × 5² = 3.14 × 25 = 78.5"
    }

    # Используем Deepseek (по умолчанию)
    classifier = UniversalMathErrorClassifier(
        provider="deepseek",
        api_key=os.environ.get("DEEPSEEK_API_KEY")  # Из переменной окружения
    )

    print("\n Тестовый пример:")
    print(f"Условие: {example_data['task_text']}")
    print(f"Ответ ИИ: {example_data['ai_response'][:100]}...")

    result = classifier.classify(**example_data)

    print(f"\n[DONE] Результат классификации:")
    print(f"Оценка: {result['assessment']}")
    print(f"Объяснение: {result['reasoning']}")
    if result['error_type']:
        print(f"Тип ошибки: {result['error_type']}")
