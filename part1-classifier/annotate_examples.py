"""
Скрипт для автоматической разметки примеров 1-45
Читает данные из Excel, запускает классификатор и сохраняет результаты
"""

import pandas as pd
import sys
import os
from classifier import MathErrorClassifier, calculate_metrics
import json

def load_data(excel_path):
    """Загружает данные из Excel файла"""
    print(f"Загрузка данных из {excel_path}...")

    # Читаем лист "Рабочий лист 1"
    df = pd.read_excel(excel_path, sheet_name='Рабочий лист 1')

    print(f"Загружено строк: {len(df)}")
    print(f"Столбцы: {df.columns.tolist()}")

    return df

def prepare_examples(df):
    """Подготавливает примеры для классификации"""
    examples = []

    for idx, row in df.iterrows():
        # Пропускаем пустые строки
        if pd.isna(row.get('problem_statement')) or pd.isna(row.get('R1_REPLICA_OUT')):
            continue

        example = {
            'id': int(row.get('id', idx + 1)) if not pd.isna(row.get('id')) else idx + 1,
            'task_text': str(row.get('problem_statement', '')),
            'dialogue_history': str(row.get('full_dialog_student', '')),
            'ai_response': str(row.get('R1_REPLICA_OUT', '')),
            'ground_truth': row.get('Ground truth') if 'Ground truth' in row and not pd.isna(row.get('Ground truth')) else None
        }

        examples.append(example)

    print(f"Подготовлено примеров для классификации: {len(examples)}")
    return examples

def annotate_examples(examples, classifier):
    """Размечает примеры с помощью классификатора"""
    print("\nНачинаем разметку примеров...")
    print("=" * 80)

    results = []

    for i, example in enumerate(examples, 1):
        print(f"\n[{i}/{len(examples)}] Обработка примера ID {example['id']}...")

        # Классификация
        result = classifier.classify(
            task_text=example['task_text'],
            dialogue_history=example['dialogue_history'],
            ai_response=example['ai_response']
        )

        # Добавляем результат
        result_entry = {
            'id': example['id'],
            'assessment': result['assessment'],
            'reasoning': result['reasoning'],
            'error_type': result.get('error_type'),
            'ground_truth': example.get('ground_truth')
        }

        results.append(result_entry)

        # Выводим результат
        print(f"   Оценка: {result['assessment']}")
        print(f"   Объяснение: {result['reasoning'][:100]}...")
        if example.get('ground_truth') is not None:
            match = "✓" if result['assessment'] == example['ground_truth'] else "✗"
            print(f"   Ground truth: {example['ground_truth']} {match}")

    print("\n" + "=" * 80)
    print("Разметка завершена!")

    return results

def calculate_and_save_metrics(results, output_dir):
    """Рассчитывает метрики и сохраняет результаты"""

    # Фильтруем только те примеры, где есть ground truth
    labeled_results = [r for r in results if r['ground_truth'] is not None]

    if len(labeled_results) > 0:
        predictions = [r['assessment'] for r in labeled_results]
        ground_truth = [int(r['ground_truth']) for r in labeled_results]

        metrics = calculate_metrics(predictions, ground_truth)

        print("\n" + "=" * 80)
        print("МЕТРИКИ КАЧЕСТВА")
        print("=" * 80)
        print(f"Accuracy:  {metrics['accuracy']:.2%}")
        print(f"Precision: {metrics['precision']:.2%}")
        print(f"Recall:    {metrics['recall']:.2%}")
        print(f"F1-Score:  {metrics['f1_score']:.2%}")
        print("\nConfusion Matrix:")
        print(f"  True Positive:  {metrics['confusion_matrix']['true_positive']}")
        print(f"  True Negative:  {metrics['confusion_matrix']['true_negative']}")
        print(f"  False Positive: {metrics['confusion_matrix']['false_positive']}")
        print(f"  False Negative: {metrics['confusion_matrix']['false_negative']}")
    else:
        metrics = None
        print("\nНет примеров с ground truth для расчета метрик")

    # Сохраняем результаты
    output_file = os.path.join(output_dir, 'results.json')
    output_data = {
        'model': 'claude-sonnet-4-5-20250929',
        'total_examples': len(results),
        'metrics': metrics,
        'results': results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\nРезультаты сохранены в {output_file}")

    # Сохраняем таблицу для сдачи
    table_file = os.path.join(output_dir, 'results_table.md')
    with open(table_file, 'w', encoding='utf-8') as f:
        f.write("# Результаты разметки примеров 1-45\n\n")
        f.write("| ID | Оценка | Краткое пояснение | Тип ошибки |\n")
        f.write("|----|--------|-------------------|------------|\n")
        for r in results:
            error_type = r['error_type'] if r['error_type'] else '-'
            reasoning = r['reasoning'].replace('|', '\\|')[:100]
            f.write(f"| {r['id']} | {r['assessment']} | {reasoning} | {error_type} |\n")

    print(f"Таблица результатов сохранена в {table_file}")

    return metrics

def main():
    # Путь к Excel файлу
    excel_path = '../31.xlsx'

    if not os.path.exists(excel_path):
        print(f"Ошибка: файл {excel_path} не найден")
        return

    # Загрузка данных
    df = load_data(excel_path)

    # Подготовка примеров
    examples = prepare_examples(df)

    if len(examples) == 0:
        print("Ошибка: не найдено примеров для разметки")
        return

    # Инициализация классификатора
    print("\nИнициализация классификатора Claude Sonnet 4.5...")
    classifier = MathErrorClassifier()

    # Разметка примеров
    results = annotate_examples(examples, classifier)

    # Расчет метрик и сохранение
    output_dir = os.path.dirname(os.path.abspath(__file__))
    calculate_and_save_metrics(results, output_dir)

    print("\n✅ Готово! Все результаты сохранены.")

if __name__ == "__main__":
    main()
