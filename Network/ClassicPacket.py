from enum import IntEnum

class PacketType(IntEnum):
    LOGIN = 0x00,
    PING = 0x01,
    LEVEL_INIT = 0x02,
    LEVEL_DATA = 0x03,
    LEVEL_END = 0x04,
    PLACE_BREAK_TILE = 0x05,
    UPDATE_TILE = 0x06,
    PLAYER_JOIN = 0x07,
    PLAYER_TELEPORT = 0x08,
    PLAYER_MOVE_ROTATE = 0x09,
    PLAYER_MOVE = 0x0A,
    PLAYER_ROTATE = 0x0B,
    PLAYER_LEAVE = 0x0C,
    CHAT = 0x0D,
    LOGOUT = 0x0E,
    UPDATE_USER_TYPE = 0x0F

def get_packet_size(type : PacketType) -> int:
    match type:
        case PacketType.LOGIN:
            return 1 + 64 + 64 + 1
        case PacketType.PING:
            return 0
        case PacketType.LEVEL_INIT:
            return 0
        case PacketType.LEVEL_DATA:
            return 2 + 1024 + 1
        case PacketType.LEVEL_END:
            return 2 + 2 + 2
        case PacketType.PLACE_BREAK_TILE:
            return 2 + 2 + 2 + 1 + 1
        case PacketType.UPDATE_TILE:
            return 2 + 2 + 2 + 1
        case PacketType.PLAYER_JOIN:
            return 1 + 64 + 2 + 2 + 2 + 1 + 1
        case PacketType.PLAYER_TELEPORT:
            return 1 + 2 + 2 + 2 + 1 +1
        case PacketType.PLAYER_MOVE_ROTATE:
            return 1 + 1 + 1 + 1 + 1 + 1
        case PacketType.PLAYER_MOVE:
            return 1 + 1 + 1 + 1
        case PacketType.PLAYER_ROTATE:
            return 1 + 1 + 1
        case PacketType.PLAYER_LEAVE:
            return 1
        case PacketType.CHAT:
            return 1 + 64
        case PacketType.LOGOUT:
            return 64
        case PacketType.UPDATE_USER_TYPE:
            return 1
        case _:
            return -1

def pt2bytes(type : PacketType) -> bytes:
    return int(type.value).to_bytes(1, "big", signed=False)

def int2pt(i : int) -> PacketType | None:
    if i < 0x00 or i > 0x0F:
        return None
    return PacketType(i)

def bytes2pt(b : bytes) -> PacketType | None:
    return int2pt(int.from_bytes(b, "big", signed=False))

def build_login_packet(pvn : int, username : str, mppass : str) -> bytearray:
    packet = bytearray()
    packet += pt2bytes(PacketType.LOGIN)
    packet += pvn.to_bytes(1, "big", signed=False)
    packet += username.ljust(64).encode("ascii")
    packet += mppass.ljust(64).encode("ascii")
    packet += b"\x00"
    return packet

def build_place_break_tile_packet(x : int, y : int, z : int, mode : bool, type : int) -> bytearray:
    packet = bytearray()
    packet += pt2bytes(PacketType.PLACE_BREAK_TILE)
    packet += x.to_bytes(2, "big", signed=False)
    packet += y.to_bytes(2, "big", signed=False)
    packet += z.to_bytes(2, "big", signed=False)
    packet += b"\x01" if mode else b"\x00"
    packet += type.to_bytes(1, "big", signed=False)
    return packet

def build_teleport_packet(x : float, y : float, z : float, yaw : float, pitch : float) -> bytearray:
    packet = bytearray()
    packet += pt2bytes(PacketType.PLAYER_TELEPORT)
    packet += (-1).to_bytes(1, "big", signed=True)
    packet += int(x * 32).to_bytes(2, "big", signed=False)
    packet += int(y * 32).to_bytes(2, "big", signed=False)
    packet += int(z * 32).to_bytes(2, "big", signed=False)
    packet += int(int((yaw * 256 / 360)) & 255).to_bytes(1, "big", signed=False)
    packet += int(int((pitch * 256 / 360)) & 255).to_bytes(1, "big", signed=False)
    return packet

def build_chat_packet(message : str) -> bytearray:
    packet = bytearray()
    packet += pt2bytes(PacketType.CHAT)
    packet += (-1).to_bytes(1, "big", signed=True)
    packet += message.ljust(64).encode("ascii")
    return packet