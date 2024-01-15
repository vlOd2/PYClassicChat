import os

if os.name == "nt":
    # Windows
    import msvcrt
else:
    # Posix (Linux, OS X)
    import sys
    import termios
    import atexit
    from select import select

class ConsoleReader:
    def __init__(self) -> None:
        if os.name == 'nt':
            pass
        else:
            # Save the terminal settings
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)
    
            # New terminal setting unbuffered
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)
    
            # Support normal-terminal reset at exit
            atexit.register(self.cleanup)
    
    def cleanup(self) -> None:
        if os.name == 'nt':
            pass
        else:
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def update(self) -> bool:
        if os.name == 'nt':
            return msvcrt.kbhit()
        else:
            dr,dw,de = select([sys.stdin], [], [], 0)
            return dr != []

    def read(self) -> int:
        if os.name == 'nt':
            b = msvcrt.getch()
        else:
            b = sys.stdin.buffer.read(1)
        
        return int.from_bytes(b, "big", signed=False)

    def parse_arrow(self, i : int) -> int:
        ''' 
        -1 : invalid
        0 : up
        1 : right
        2 : down
        3 : left
        '''

        if os.name == 'nt':
            vals = [72, 77, 80, 75]
        else:
            vals = [65, 67, 66, 68]
        
        try:
            return vals.index(i)
        except ValueError:
            return -1