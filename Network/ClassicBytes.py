import io

# XXX: Originally this extended io.BytesIO directly
#      But that became confusing really quick
class ClassicBytes():
    data : io.BytesIO | None = None

    def __init__(self, data : bytes) -> None:
        self.data = io.BytesIO(data)

    def read_byte(self) -> int:
        return int.from_bytes(self.data.read(1), "big", signed=False)
        
    def read_sbyte(self) -> int:
        return int.from_bytes(self.data.read(1), signed=True)
    
    def read_short(self) -> int:
        return int.from_bytes(self.data.read(2), "big", signed=False)
    
    def read_string(self) -> str:
        return self.data.read(64).decode("ascii").rstrip(" ")
    
    def read_byte_array(self) -> bytes:
        return self.data.read(1024)