import sys
import argparse
import csv


class VirtualMachine:
    def __init__(self, memory_size=1024):
        # Память команд и данных объединена (Требование №3)
        self.memory = [0] * memory_size
        self.stack = []
        self.pc = 0  # Program Counter

    def load_program(self, binary_path):
        """Загрузка бинарного файла в начало памяти"""
        with open(binary_path, "rb") as f:
            data = f.read()
            # Записываем байты программы в память (побайтово)
            # В реальной VM память обычно байтовая, но для удобства вычислений
            # здесь мы храним int, так как команды LOAD/STORE работают с числами.
            for i, byte in enumerate(data):
                if i < len(self.memory):
                    self.memory[i] = byte
                else:
                    raise MemoryError("Программа не влезает в память")

    def dump_memory(self, path, start, end):
        """Сохранение дампа памяти в CSV"""
        with open(path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Address", "Value"])
            for addr in range(start, min(end + 1, len(self.memory))):
                writer.writerow([addr, self.memory[addr]])
        print(f"Дамп памяти сохранен в {path} (диапазон {start}-{end})")

    def run(self):
        # Основной цикл интерпретации (Требование №4)
        while self.pc < len(self.memory):
            # Читаем 3 байта (Little Endian)
            if self.pc + 2 >= len(self.memory):
                break  # Конец памяти

            b0 = self.memory[self.pc]
            b1 = self.memory[self.pc + 1]
            b2 = self.memory[self.pc + 2]

            # Собираем команду обратно
            instruction = b0 | (b1 << 8) | (b2 << 16)

            if instruction == 0:
                # Остановимся, если встретили пустую память (нули)
                break

            opcode = instruction & 0x7F  # Биты 0-6
            operand = instruction >> 7  # Биты 7-20+

            self.pc += 3  # Переходим к следующей команде

            # --- Выполнение команд ---

            # 1. Загрузка константы (PUSH)
            if opcode == 34:
                self.stack.append(operand)

            # 2. Чтение из памяти (LOAD)
            # Операнд = абсолютный адрес
            elif opcode == 33:
                addr = operand
                if 0 <= addr < len(self.memory):
                    self.stack.append(self.memory[addr])
                else:
                    raise IndexError(f"LOAD: Адрес {addr} выходит за границы")

            # 3. Запись в память (STORE)
            # Операнд B = смещение
            # Стек: [... Значение, БазовыйАдрес] -> POP -> POP
            # В задании сказано: "адрес = элемент с вершины + смещение B".
            # Значит, на вершине лежит адрес. А значение должно быть под ним.
            elif opcode == 80:
                if len(self.stack) < 2:
                    raise IndexError("STORE: Пустой стек (нужно 2 элемента: Адрес и Значение)")

                base_addr = self.stack.pop()  # Вершина стека
                value = self.stack.pop()  # Следующий элемент

                target_addr = base_addr + operand

                if 0 <= target_addr < len(self.memory):
                    self.memory[target_addr] = value
                else:
                    raise IndexError(f"STORE: Адрес {target_addr} выходит за границы")

            # 4. POPCNT (Этап 4 - пока пропускаем или ставим заглушку)
            elif opcode == 14:
                pass  # Реализуем на следующем этапе

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

    # Сохраняем дамп в любом случае
    vm.dump_memory(args.dump_file, start, end)


if __name__ == "__main__":
    main()

# запуск: python assembler_stage1.py test_spec.asm output.bin --log