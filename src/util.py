def decimal_to_hex(value):
    # 32ビット値を上位16ビットと下位16ビットに分割
    upper = (value >> 16) & 0xFFFF
    lower = value & 0xFFFF
    return upper, lower