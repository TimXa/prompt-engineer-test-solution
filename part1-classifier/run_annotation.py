"""
Автоматический запуск разметки 45 примеров через Deepseek API
"""

import pandas as pd
import sys
import os
import time
from universal_classifier import UniversalMathErrorClassifier, calculate_metrics
import json

def load_data(excel_path):
    """Загружает данные из Excel файла"""
    print(f"Загрузка данных из {excel_path}...")
    df = pd.read_excel(excel_path, sheet_name='Рабочий лист 1')
    print(f"Загружено строк: {len(df)}")
    return df

def prepare_examples(df):
    """Подготавливает примеры для классификации"""
    examples = []
    for idx, row in df.iterrows():
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

    print(f"[OK] Подготовлено примеров: {len(examples)}")
    return examples

def annotate_examples(examples, classifier):
    """Размечает примеры с помощью классификатора"""
    print("\n" + "=" * 80)
    print("НАЧАЛО РАЗМЕТКИ")
    print("=" * 80)

    results = []
    for i, example in enumerate(examples, 1):
        print(f"\n[{i}/{len(examples)}] Пример ID {example['id']}...")

        result = classifier.classify(
            task_text=example['task_text'],
            dialogue_history=example['dialogue_history'],
            ai_response=example['ai_response']
        )

        result_entry = {
            'id': example['id'],
            'assessment': result['assessment'],
            'reasoning': result['reasoning'],
            'error_type': result.get('error_type'),
            'ground_truth': example.get('ground_truth')
        }

        results.append(result_entry)

        print(f"   [OK] Оценка: {result['assessment']}")
        print(f"    Объяснение: {result['reasoning'][:80]}...")

        if example.get('ground_truth') is not None:
            match = "[OK]" if result['assessment'] == example['ground_truth'] else "[X]"
            print(f"    Ground truth: {example['ground_truth']} {match}")

        # Задержка между запросами чтобы избежать rate limiting
        if i < len(examples):
            time.sleep(2)

    print("\n" + "=" * 80)
    print("[DONE] РАЗМЕТКА ЗАВЕРШЕНА!")
    print("=" * 80)

    return results

def save_results(results, metrics, output_dir, provider):
    """Сохраняет результаты"""
    output_file = os.path.join(output_dir, f'results_{provider}.json')
    output_data = {
        'provider': provider,
        'total_examples': len(results),
        'metrics': metrics,
        'results': results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n Результаты сохранены в {output_file}")

    table_file = os.path.join(output_dir, f'results_table_{provider}.md')
    with open(table_file, 'w', encoding='utf-8') as f:
        f.write(f"# Результаты разметки (провайдер: {provider.upper()})\n\n")

        if metrics:
            f.write("## Метрики качества\n\n")
            f.write(f"- **Accuracy**: {metrics['accuracy']:.2%}\n")
            f.write(f"- **Precision**: {metrics['precision']:.2%}\n")
            f.write(f"- **Recall**: {metrics['recall']:.2%}\n")
            f.write(f"- **F1-Score**: {metrics['f1_score']:.2%}\n\n")
            f.write("### Confusion Matrix\n\n")
            f.write(f"- True Positive: {metrics['confusion_matrix']['true_positive']}\n")
            f.write(f"- True Negative: {metrics['confusion_matrix']['true_negative']}\n")
            f.write(f"- False Positive: {metrics['confusion_matrix']['false_positive']}\n")
            f.write(f"- False Negative: {metrics['confusion_matrix']['false_negative']}\n\n")

        f.write("## Результаты разметки\n\n")
        f.write("| ID | Оценка | Краткое пояснение | Тип ошибки |\n")
        f.write("|----|--------|-------------------|------------|\n")

        for r in results:
            error_type = r['error_type'] if r['error_type'] else '-'
            reasoning = r['reasoning'].replace('|', '\\|')[:150]
            f.write(f"| {r['id']} | {r['assessment']} | {reasoning} | {error_type} |\n")

    print(f" Таблица сохранена в {table_file}")

def main():
    print("\n" + "=" * 80)
    print(" АВТОМАТИЧЕСКАЯ РАЗМЕТКА 45 ПРИМЕРОВ")
    print(" Провайдер: Deepseek через Artemox прокси")
    print("=" * 80)

    excel_path = '../31.xlsx'

    if not os.path.exists(excel_path):
        print(f"[ERROR] Ошибка: файл {excel_path} не найден")
        return

    # Загрузка данных
    df = load_data(excel_path)
    examples = prepare_examples(df)

    if len(examples) == 0:
        print("[ERROR] Не найдено примеров для разметки")
        return

    # Инициализация классификатора с Artemox прокси
    print("\n Инициализация Deepseek через Artemox прокси...")
    classifier = UniversalMathErrorClassifier(
        provider='deepseek',
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url='https://api.artemox.com/v1'
    )

    # Разметка
    results = annotate_examples(examples, classifier)

    # Расчет метрик
    labeled_results = [r for r in results if r['ground_truth'] is not None]

    if len(labeled_results) > 0:
        predictions = [r['assessment'] for r in labeled_results]
        ground_truth = [int(r['ground_truth']) for r in labeled_results]

        metrics = calculate_metrics(predictions, ground_truth)

        print("\n" + "=" * 80)
        print(" МЕТРИКИ КАЧЕСТВА")
        print("=" * 80)
        print(f"Accuracy:  {metrics['accuracy']:.2%}")
        print(f"Precision: {metrics['precision']:.2%}")
        print(f"Recall:    {metrics['recall']:.2%}")
        print(f"F1-Score:  {metrics['f1_score']:.2%}")
        print("\nConfusion Matrix:")
        print(f"  TP: {metrics['confusion_matrix']['true_positive']}")
        print(f"  TN: {metrics['confusion_matrix']['true_negative']}")
        print(f"  FP: {metrics['confusion_matrix']['false_positive']}")
        print(f"  FN: {metrics['confusion_matrix']['false_negative']}")
    else:
        metrics = None
        print("\n Нет примеров с ground truth для расчета метрик")

    # Сохранение
    output_dir = os.path.dirname(os.path.abspath(__file__))
    save_results(results, metrics, output_dir, 'deepseek')

    print("\n" + "=" * 80)
    print("[DONE] ГОТОВО! Все результаты сохранены.")
    print("=" * 80)

if __name__ == "__main__":
    main()
