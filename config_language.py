import sys
import json
import re

class ConfigSyntaxError(Exception):
    def __init__(self, message):
        super().__init__(message)

def parse_value(value_str):
    """Парсинг значения, которое может быть числом, строкой, массивом или словарем."""
    value_str = value_str.strip()
    #print(f"Обрабатываем значение: '{value_str}'")  # Отладка

    # Число
    if re.match(r'^\d+(\.\d+)?$', value_str):
        #print(f"Число: {value_str}")
        return float(value_str) if '.' in value_str else int(value_str)
    
    # Строка с @" (специальная строка с префиксом)
    if value_str.startswith('@"') and value_str.endswith('"'):
        #print(f"Строка с префиксом @: {value_str[2:-1]}")
        return value_str[2:-1]  # Убираем @" и " из строки
    
    # Строка обычная
    if value_str.startswith('"') and value_str.endswith('"'):
        #print(f"Строка: {value_str[1:-1]}")
        return value_str[1:-1]  # Убираем кавычки из строки
    
    # Массив
    if value_str.startswith('[') and value_str.endswith(']'):
        # Это словарь, мы его парсим
        dict_items = parse_dict(value_str[1:-1].strip())  # Убираем [] и обрабатываем
        #print(f"Словарь: {dict_items}")
        return dict_items

    # Массив (поддержка вложенности)
    if value_str.startswith('#(') and value_str.endswith(')'):
        array_items = parse_array(value_str[2:-1])  # Рекурсивный парсинг массива
        #print(f"Массив: {array_items}")
        return array_items
    
    # Константа (возможно выражение)
    if value_str.startswith('|') and value_str.endswith('|'):
        #print(f"Константа: {value_str[1:-1]}")
        return value_str[1:-1]  # Мы вернем имя константы как строку
    
    raise ConfigSyntaxError(f"Неизвестное значение: {value_str}")

def parse_array(array_str):
    """Парсинг массива с поддержкой вложенности."""
    #print(f"Парсим массив: {array_str}")
    items = []
    i = 0
    length = len(array_str)
    
    while i < length:
        if array_str[i] == '#':  # начало вложенного массива
            # Ищем пару скобок и рекурсивно обрабатываем вложенный массив
            start = i + 2  # пропускаем '#('
            depth = 1
            i = start
            while i < length and depth > 0:
                if array_str[i] == '(':
                    depth += 1
                elif array_str[i] == ')':
                    depth -= 1
                i += 1
            item_str = array_str[start:i-1]
            items.append(parse_array(item_str))  # Рекурсивно обрабатываем вложенный массив
        elif array_str[i] in (' ', '\t'):  # Пропускаем пробелы и табуляции
            i += 1
        else:
            # Ищем следующее значение
            start = i
            while i < length and array_str[i] not in (' ', '\t', '#', ')'):
                i += 1
            item_str = array_str[start:i].strip()
            items.append(parse_value(item_str))
    
    return items

def parse_dict(dict_str):
    """Парсинг словаря."""
    #print(f"Парсим словарь: {dict_str}")
    items = {}

    # Разделяем по запятой, но нужно учитывать, что значение может быть строкой с запятыми
    pairs = re.split(r',\s*(?=\w+\s*=>)', dict_str.strip())
    for pair in pairs:
        key_value = pair.split('=>', 1)
        if len(key_value) != 2:
            raise ConfigSyntaxError(f"Неверный формат записи в словаре: {pair}")
        key = key_value[0].strip()
        value_str = key_value[1].strip()
        value = parse_value(value_str)
        items[key] = value
    return items


def parse_define(def_str):
    """Парсим строку вида (define <name> <value>)"""
    match = re.match(r'^\(define\s+(\w+)\s+(.+)\)$', def_str.strip())
    if match:
        name = match.group(1)
        value = match.group(2)
        return name, value
    else:
        raise ConfigSyntaxError(f"Неверный формат объявления константы: {def_str}")

def parse_lines(lines):
    """Парсинг строк из конфигурационного файла."""
    #print(f"Начинаем парсить строки файла.")  # Отладка
    data = {}  # Используем 'data' для хранения значений
    defines = {}
    
    current_comment = ""
    for line in lines:
        line = line.strip()
        #print(f"Обрабатываем строку: '{line}'")  # Отладка
        
        # Пропускаем пустые строки и комментарии
        if not line or line.startswith('{-'):
            if current_comment:
                current_comment += "\n" + line
            else:
                current_comment = line
            continue
        
        if line.startswith('-}'):
            current_comment = ""
            continue
        
        # Обработка объявления констант
        if line.startswith('(define'):
            name, value = parse_define(line)
            defines[name] = value
            continue
        
        # Обработка значений
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = parse_value(value)
            data[key] = value  # Сохраняем в 'data'
    
    return data, defines

def main():
    if len(sys.argv) != 2:
        print("Использование: python task_3.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Парсим строки
        data, defines = parse_lines(lines)

        # Создаем финальный результат в формате JSON
        result = {
            **data,  # Просто объединяем все данные в корневой словарь
            "defines": defines
        }
        
        # Выводим результат в JSON-формате
        print("Результат:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    except FileNotFoundError:
        print(f"Файл {input_file} не найден.")
        sys.exit(1)
    except ConfigSyntaxError as e:
        print(f"Ошибка синтаксиса: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
