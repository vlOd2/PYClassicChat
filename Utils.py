def is_float(s : str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def is_int(s : str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False