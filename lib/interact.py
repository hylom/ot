"""interact.py - implements user interaction commands"""

def confirm(message: str) -> bool:
    msg = f"{message} (yes/no): "
    while True:
        s = input(msg).lower()
        if s in ("yes", "y"):
            return True
        if s in ("no", "n"):
            return False
        print("Please answer yes or no.\n")

def prompt(message:str, default: str|None):
    if default is None:
        msg = f"{message}: "
    else:
        msg = f"{message} (default: {default}): "
    while True:
        s = input(msg)
        if len(s) > 0:
            return s
        if default is not None:
            return default
