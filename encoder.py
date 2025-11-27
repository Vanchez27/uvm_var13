from assembler_stage1 import IRCommand

OPCODES = {
    "PUSH": 34,
    "LOAD": 33,
    "STORE": 80,
    "POPCNT": 14
}


def encode_ir(ir_program):
    output = bytearray()
    for cmd in ir_program:
        A = OPCODES[cmd.opcode]

        if cmd.opcode == "POPCNT":
            B = 0
        else:
            B = cmd.args[0]

        byte0 = 0x80 | A
        byte1 = B & 0xFF
        byte2 = 0x00

        output.extend([byte0, byte1, byte2])

    return bytes(output)

print(encode_ir([
    IRCommand("POPCNT", [391], 1)
]).hex())