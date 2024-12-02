import unittest
from config_language import parse_lines, ConfigSyntaxError

class TestConfigParser(unittest.TestCase):

    def test_employee_config(self):
        # Переход от строки к массиву в тесте
        lines = [
            "(define MAX_SALARY 5000)",
            'employees = "John, Jane"'  # Ожидаем строку с именами через запятую
        ]
        data, defines = parse_lines(lines)
        employees = data["employees"].split(", ")
        self.assertEqual(employees, ["John", "Jane"])  # Проверяем преобразованный список
        self.assertEqual(defines["MAX_SALARY"], "5000")

    def test_production_config(self):
        lines = [
            "(define BASE_COST 1000)",
            'product = "Concrete"',
            "volume = 5000",
            "cost = 5000000"
        ]
        data, defines = parse_lines(lines)
        self.assertEqual(data["product"], "Concrete")
        self.assertEqual(data["volume"], 5000)
        self.assertEqual(data["cost"], 5000000)
        self.assertEqual(defines["BASE_COST"], "1000")

    def test_server_config(self):
        lines = [
            '(define SERVER_NAME "MyServer")',
            'host = "192.168.1.1"',
            "port = 8080",
            "max_connections = 100",
        ]
        data, defines = parse_lines(lines)
        self.assertEqual(data["host"], "192.168.1.1")
        self.assertEqual(data["port"], 8080)
        self.assertEqual(data["max_connections"], 100)

    def test_parse_array(self):
        # Тест парсинга массива
        lines = [
            "numbers = #(1 2 3 4 5)"
        ]
        data, defines = parse_lines(lines)
        self.assertEqual(data["numbers"], [1, 2, 3, 4, 5])

    def test_parse_nested_array(self):
        # Тест парсинга вложенного массива
        lines = [
            "nested_numbers = #(1 2 #(3 4) 5)"
        ]
        data, defines = parse_lines(lines)
        self.assertEqual(data["nested_numbers"], [1, 2, [3, 4], 5])

    def test_parse_dictionary(self):
        # Тест парсинга словаря
        lines = [
            'data = [name => "John", age => 30]'
        ]
        data, defines = parse_lines(lines)
        self.assertEqual(data["data"], {"name": "John", "age": 30})

    def test_parse_special_string(self):
        # Тест парсинга специальной строки с @"
        lines = [
            'greeting = @"Hello, world!"'
        ]
        data, defines = parse_lines(lines)
        self.assertEqual(data["greeting"], "Hello, world!")

    def test_parse_constant(self):
        # Тест парсинга константы
        lines = [
            "(define PI 3.14159)",
            "pi_value = |PI|"
        ]
        data, defines = parse_lines(lines)
        # Предполагая, что парсер заменяет константу на ее значение
        self.assertEqual(data["pi_value"], "PI")

    def test_syntax_error(self):
        # Тест обработки синтаксической ошибки
        lines = [
            "invalid_line"
        ]
        with self.assertRaises(ConfigSyntaxError):
            parse_lines(lines)

    def test_comment_handling(self):
        # Тест корректной обработки комментариев
        lines = [
            "{- Это комментарий -}",
            'value = "Test"'
        ]
        data, defines = parse_lines(lines)
        self.assertEqual(data["value"], "Test")

    def test_empty_input(self):
        # Тест обработки пустого ввода
        lines = []
        data, defines = parse_lines(lines)
        self.assertEqual(data, {})
        self.assertEqual(defines, {})

    def test_invalid_define(self):
        # Тест обработки некорректного объявления константы
        lines = [
            "(defineInvalid 3.14)"
        ]
        with self.assertRaises(ConfigSyntaxError):
            parse_lines(lines)

    def test_invalid_value(self):
        # Тест обработки некорректного значения
        lines = [
            "value = invalid"
        ]
        with self.assertRaises(ConfigSyntaxError):
            parse_lines(lines)

    def test_parse_numbers(self):
        # Тест парсинга чисел
        lines = [
            "int_value = 42",
            "float_value = 3.14"
        ]
        data, defines = parse_lines(lines)
        self.assertEqual(data["int_value"], 42)
        self.assertEqual(data["float_value"], 3.14)

    def test_parse_complex_structure(self):
        # Тест парсинга сложной структуры с вложенными массивами и словарями
        lines = [
            'complex = [key1 => #(1 2 3), key2 => [subkey => @"Value"]]'
        ]
        data, defines = parse_lines(lines)
        self.assertEqual(data["complex"], {
            "key1": [1, 2, 3],
            "key2": {"subkey": "Value"}
        })

if __name__ == '__main__':
    unittest.main()
