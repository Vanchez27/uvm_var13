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

    def assemble_command(self, cmd: IRCommand) -> bytes:
        a = self.OPCODE_MAP[cmd.opcode]
        b = cmd.operand

        # Формула упаковки битов
        value = a | (b << 7)

        # Преобразование в 3 байта
        return value.to_bytes(3, byteorder='little')

    def run(self):
        parser = argparse.ArgumentParser(description="Учебный Ассемблер (УВМ) - Этап 2")
        parser.add_argument("input_file", help="Путь к исходному файлу (.asm)")
        parser.add_argument("output_file", help="Путь к двоичному файлу-результату (.bin)")
        parser.add_argument("--log", action="store_true", help="Вывод лога (бинарный вид)")

        args = parser.parse_args()

        try:
            commands = self.parse_file(args.input_file)
            binary_data = bytearray()
            log_output = []

            for cmd in commands:
                machine_code = self.assemble_command(cmd)
                binary_data.extend(machine_code)

                # Формирование строки для лога
                hex_str = ", ".join(f"0x{b:02X}" for b in machine_code)
                log_output.append(f"{cmd.opcode} {cmd.operand}: \t{hex_str}")

            # Запись в бинарный файл
            with open(args.output_file, "wb") as f:
                f.write(binary_data)

            print(f"Размер выходного файла: {len(binary_data)} байт")

            # Вывод лога
            if args.log:
                print("\nLog Mode (Hex Dump):")
                for line in log_output:
                    print(line)

        except Exception as e:
            print(f"Ошибка: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    app = Assembler()
    app.run()