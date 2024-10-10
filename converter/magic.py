import math
import re
import random
import time


def process_raw_csv(input_file, correct_file, incorrect_file):
    def extract_last_four_digits(phone_number):
        # Убираем любые символы, кроме цифр, и извлекаем последние 4 цифры
        digits = re.sub(r'\D', '', phone_number)
        return digits[-4:] if len(digits) >= 4 else None

    # Открываем файл в кодировке ISO-8859-1 (или другой, если необходимо)
    with open(input_file, 'r', encoding='ISO-8859-1') as infile, \
            open(correct_file, 'w', encoding='utf-8') as correct_outfile, \
            open(incorrect_file, 'w', encoding='utf-8') as incorrect_outfile:

        for line in infile:
            try:
                # Убираем лишние пробелы и точку с запятой в конце строки
                line = line.strip().replace('"', '').rstrip(';')

                # Убираем некорректные символы, такие как Ê
                line = re.sub(r'[^\x00-\x7F]+', '', line)

                # Разделяем строку по символу `;`
                parts = [part.strip() for part in line.split(';')]

                if len(parts) != 4:
                    raise ValueError("Некорректное количество столбцов")

                iin, password, target_url, phone_number = parts

                # Извлекаем последние 4 цифры номера телефона
                last_four_digits = extract_last_four_digits(phone_number)
                if not last_four_digits:
                    raise ValueError("Некорректный номер телефона")

                # Формируем строку для корректного файла
                child_in_order = "1"
                status = "Not Started"
                correct_outfile.write(f"{iin};{password};{last_four_digits};{target_url};{child_in_order};{status}\n")

            except Exception as e:
                # Записываем некорректные строки в отдельный файл
                incorrect_outfile.write(line + '\n')

    print("Обработка завершена.")


def rearrange_accounts(input_file, output_file):
    # Чтение строк из файла accounts.txt
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = [line.strip() for line in infile if line.strip()]

    # Группировка строк по ИИН
    iin_groups = {}
    for line in lines:
        parts = line.split(';')
        iin = parts[0]
        if iin not in iin_groups:
            iin_groups[iin] = []
        iin_groups[iin].append(line)

    # Определяем количество строк
    total_lines = len(lines)

    # Для каждого ИИН распределяем строки по максимально большим промежуткам
    rearranged_lines = [None] * total_lines  # Создаем пустой список для размещения строк

    # Сортируем ИИН-группы по убыванию длины
    sorted_iin_groups = sorted(iin_groups.items(), key=lambda x: len(x[1]), reverse=True)

    current_index = 0  # Текущий индекс для вставки

    for iin, group in sorted_iin_groups:
        group_size = len(group)
        # Рассчитываем шаг для равномерного распределения строк
        step = math.ceil(total_lines / group_size)

        for i, line in enumerate(group):
            # Найдем ближайший свободный слот
            while rearranged_lines[current_index] is not None:
                current_index = (current_index + 1) % total_lines

            rearranged_lines[current_index] = line
            current_index = (current_index + step) % total_lines  # Двигаемся вперед на шаг

    # Убираем возможные пустые места (если они есть)
    rearranged_lines = [line for line in rearranged_lines if line is not None]

    # Записываем результат в новый файл
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for line in rearranged_lines:
            outfile.write(line + '\n')

    print("Перестановка строк завершена.")


process_raw_csv('data/raw.csv', 'data/accounts.txt', 'data/incorrect_accounts.txt')
time.sleep(1)
rearrange_accounts('data/accounts.txt', 'data/rearranged_accounts.txt')
