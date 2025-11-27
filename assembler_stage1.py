import argparse
import sys
from dataclasses import dataclass


@dataclass
class IRCommand:
    opcode: str
    operand: int
    line: int


class Assembler:
    # Словарь поле A
    OPCODE_MAP = {
        "PUSH": 34,  # Загрузка константы
        "LOAD": 33,  # Чтение значения из памяти
        "STORE": 80,  # Запись значения в память
        "POPCNT": 14  # Унарная операция popcnt (требует смещение)
    }

    def parse_line(self, line: str, line_number: int):
        line = line.split(';')[0].strip()  # Удаляет комментарий если есть ;
        if not line:
            return None

        parts = line.split()
        mnemonic = parts[0].upper()

        if mnemonic not in self.OPCODE_MAP:
            raise ValueError(f"Неизвестная команда '{mnemonic}' на строке {line_number}")

        if len(parts) != 2:
            raise ValueError(f"Команда '{mnemonic}' ожидает 1 аргумент (строка {line_number})")

        try:
            operand = int(parts[1])
        except ValueError:
            raise ValueError(f"Аргумент должен быть числом (строка {line_number})")

        return IRCommand(mnemonic, operand, line_number)

    def parse_file(self, source_path: str):
        ir = []
        with open(source_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                cmd = self.parse_line(line, i)
                if cmd:
                    ir.append(cmd)
        return ir

    def run(self):
        parser = argparse.ArgumentParser(description="УВМ")
        parser.add_argument("input_file", help="Путь к исходному файлу .asm")
        parser.add_argument("output_file", help="Путь к двоичному файлу-результату .bin")
        parser.add_argument("--log", action="store_true", help="Режим тестирования вывод лога")

        args = parser.parse_args()

        try:
            commands = self.parse_file(args.input_file)

            # 5 шаг
            if args.log:
                print("Log Mode (A=Opcode, B=Operand):")
                for cmd in commands:
                    a_val = self.OPCODE_MAP[cmd.opcode]
                    b_val = cmd.operand
                    print(f"A={a_val}, B={b_val}")

            with open(args.output_file, "wb") as f:
                pass  # Этапа 2 пока не реализован

            print(f"Ассемблирование завершено. Обработано команд: {len(commands)}")

        except Exception as e:
            print(f"Ошибка: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    app = Assembler()
    app.run()