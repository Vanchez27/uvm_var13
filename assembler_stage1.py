from dataclasses import dataclass
import sys
@dataclass
class IRCommand:
    opcode: str
    args: list
    line: int

class AssemblerParser:
    VALID_OPCODES = {"PUSH", "LOAD", "STORE", "POPCNT"}

    def parse_line(self, line: str, line_number: int):
        line = line.strip()
        if not line or line.startswith("#"):
            return None

        parts = line.split()
        opcode = parts[0].upper()

        if opcode not in self.VALID_OPCODES:
            raise ValueError(f"Неизвестная команда '{opcode}' на строке {line_number}")

        args = []
        if opcode in ("PUSH", "LOAD", "STORE"):
            if len(parts) != 2:
                raise ValueError(f"Команда '{opcode}' ожидает 1 аргумент (строка {line_number})")
            args = [int(parts[1])]
        else:
            if len(parts) != 1:
                raise ValueError(f"Команда '{opcode}' не принимиет аргументы (строка {line_number})")

        return IRCommand(opcode, args, line_number)

    def parse_file(self, path: str):
        ir = []
        with open(path, "r") as f:
            for i, line in enumerate(f, start=1):
                cmd = self.parse_line(line, i)
                if cmd:
                    ir.append(cmd)
        return ir


if __name__ == "__main__":
    parser = AssemblerParser()
    ir = parser.parse_file(sys.argv[1])
    for cmd in ir:
        print(cmd)
