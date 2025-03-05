def decimal_to_hex(number):
    number = int(number) & 0xffffffff
    return number >> 16, number & 0xffff