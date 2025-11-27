# Содержит общие структуры данных и конфигурацию языка.

from dataclasses import dataclass, field

@dataclass
class OpcodeSpec:
    opcode_val: int   # Числовое значение опкода (поле A)
    arg_count: int      # Ожидаемое количество аргументов
    arg_bits: int       # Сколько бит выделено под аргумент (поле B)
    shift: int          # На сколько сдвигать аргумент при упаковке

@dataclass
class IRCommand:
    mnemonic: str
    args: list[int]
    line: int
    spec: OpcodeSpec = field(repr=False) # Ссылка на спецификацию для удобства

# Единственный источник спецификации языка ассемблера
OPCODE_CONFIG = {
    "LOAD_CONST": OpcodeSpec(opcode_val=34, arg_count=1, arg_bits=9,  shift=7), # Биты 7-15 -> 9 бит
    "READ_MEM":   OpcodeSpec(opcode_val=33, arg_count=1, arg_bits=14, shift=7), # Биты 7-20 -> 14 бит
    "WRITE_MEM":  OpcodeSpec(opcode_val=80, arg_count=1, arg_bits=11, shift=7), # Биты 7-17 -> 11 бит
    "POPCNT":     OpcodeSpec(opcode_val=14, arg_count=1, arg_bits=11, shift=7), # Биты 7-17 -> 11 бит
}