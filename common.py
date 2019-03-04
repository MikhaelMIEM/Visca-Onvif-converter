

def check_addr(addr):
    if not isinstance(addr, tuple) or not isinstance(addr[0], str) or not isinstance(addr[1], int):
        raise TypeError(f'addr must be of type tuple(str, int)')

