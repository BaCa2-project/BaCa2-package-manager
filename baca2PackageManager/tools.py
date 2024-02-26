from baca2PackageManager.consts import MEM_SIZES


def bytes_from_str(val: str):
    """
     function is converting memory from others units to bytes

     :return: Memory converted to bytes. (In INT type)
    """
    mem_val = int(val[:-1])
    mem_letter = val[-1]
    mem_val *= MEM_SIZES.get(mem_letter, 1)
    return mem_val


def bytes_to_str(val: int) -> str:
    """
    function is converting memory from bytes to others units

    :param val: Memory in bytes
    :type val: int

    :return: Memory converted to other units. (In STR type)
    :rtype: str
    """

    res_id = 0
    mem_steps = list(MEM_SIZES.items())
    while val // mem_steps[res_id][1] > 0:
        res_id += 1
    if res_id == 1:
        return f"{val}{mem_steps[res_id - 1][0]}"
    elif res_id == 0:
        return f"{val}{mem_steps[res_id][0]}"
    return f"{val / mem_steps[res_id - 1][1]:.2f}{mem_steps[res_id - 1][0]}"
