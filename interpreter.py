import sys
import argparse
import csv


class VirtualMachine:
    def __init__(self, memory_size=1024):
        # Память команд и данных объединена (Требование 3)
        self.memory = [0] * memory_size
        self.stack = []
        self.pc = 0  # Program Counter указывает на каком байте находимся

    def load_program(self, binary_path):
        #Загрузка бинарного файла в начало памяти
        with open(binary_path, "rb") as f:
            data = f.read()
            # Запись байтов программы в память побайтово
            for i, byte in enumerate(data):
                if i < len(self.memory):
                    self.memory[i] = byte
                else:
                    raise MemoryError("Программа не влезает в память")

    def dump_memory(self, path, start, end):
        #Сохранение дампа памяти в CSV
        with open(path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Address", "Value"])
            for addr in range(start, min(end + 1, len(self.memory))):
                writer.writerow([addr, self.memory[addr]])
        print(f"Дамп памяти сохранен в {path} (диапазон {start}-{end})")

    def run(self):
        # Основной цикл интерпретаци
        while self.pc < len(self.memory):
            # Читает 3 байта
            if self.pc + 2 >= len(self.memory):
                break  # Конец памяти

            b0 = self.memory[self.pc]
            b1 = self.memory[self.pc + 1]
            b2 = self.memory[self.pc + 2]

            # Собирает команду обратно
            instruction = b0 | (b1 << 8) | (b2 << 16)

            if instruction == 0:
                # Остановится если встретили пустую память (нули)
                break

            opcode = instruction & 0x7F  # Биты 0-6
            operand = instruction >> 7  # Биты 7-20+

            self.pc += 3  # Переход к следующей команде

            # Выполнение команд

            # Загрузка константы (PUSH)
            if opcode == 34:
                self.stack.append(operand)

            # Чтение из памяти (LOAD)
            # Операнд = абсолютный адрес
            elif opcode == 33:
                addr = operand
                if 0 <= addr < len(self.memory):
                    self.stack.append(self.memory[addr])
                else:
                    raise IndexError(f"LOAD: Адрес {addr} выходит за границы")

            # Запись в память (STORE)
            # Операнд B = смещение
            # Стек: [... Значение, БазовыйАдрес] -> POP -> POP
            elif opcode == 80:
                if len(self.stack) < 2:
                    raise IndexError("STORE: Пустой стек (нужно 2 элемента: Адрес и Значение)")

                base_addr = self.stack.pop()
                value = self.stack.pop()

                target_addr = base_addr + operand

                if 0 <= target_addr < len(self.memory):
                    self.memory[target_addr] = value
                else:
                    raise IndexError(f"STORE: Адрес {target_addr} выходит за границы")

            # POPCNT (Этап 4 - пока пропуск)
            elif opcode == 14:
                if len(self.stack) < 1:
                    raise IndexError("POPCNT: Пустой стек (нужен Базовый адрес)")

                base_addr = self.stack.pop()
                target_addr = base_addr + operand  # Адрес = TOS + B

                if 0 <= target_addr < len(self.memory):
                    value = self.memory[target_addr]

                    # Считает количество единиц в двоичном представлении числа
                    # bin(5) -> '0b101' -> count('1') -> 2
                    res = bin(value).count('1')

                    self.stack.append(res)
                else:
                    raise IndexError(f"POPCNT: Адрес {target_addr} выходит за границы")

            else:
                print(f"Неизвестная команда: A={opcode} на адресе {self.pc - 3}")
                break


def main():
    parser = argparse.ArgumentParser(description="Интерпретатор УВМ")
    parser.add_argument("binary_file", help="Путь к бинарному файлу (.bin)")
    parser.add_argument("dump_file", help="Путь для сохранения дампа памяти (.csv)")
    parser.add_argument("memory_range", help="Диапазон памяти для дампа (например, 0-100)")

    args = parser.parse_args()

    try:
        start, end = map(int, args.memory_range.split('-'))
    except ValueError:
        print("Ошибка: Диапазон памяти должен быть в формате START-END (например 0-50)")
        return

    vm = VirtualMachine(memory_size=2048)  # Память побольше

    try:
        vm.load_program(args.binary_file)
        vm.run()
    except Exception as e:
        print(f"Ошибка выполнения: {e}")

    # Сохраняет дамп в любом случае
    vm.dump_memory(args.dump_file, start, end)


if __name__ == "__main__":
    main()

# запуск: python assembler_stage1.py test_spec.asm output.bin --log