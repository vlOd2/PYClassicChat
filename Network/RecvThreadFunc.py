from traceback import print_exc
from PYClassicChat import PYClassicChat
from Console import ConsoleWriter
from . import ClassicPacket
from .ClassicPacket import PacketType
from .ClassicBytes import ClassicBytes

_ANSI_CLEAR_LINE = "\x1B[2K"

def _recv_thread_func(instance : PYClassicChat) -> None:
    while instance.connected:
        try:
            packet_type = ClassicPacket.bytes2pt(instance.client_socket.recv(1))

            if packet_type == None:
                raise Exception("Received invalid packet")
            
            packet_data = bytearray()
            packet_size = ClassicPacket.get_packet_size(packet_type)
            while len(packet_data) < packet_size:
                packet_data += instance.client_socket.recv(packet_size - len(packet_data))
            packet = ClassicBytes(packet_data)

            match packet_type:
                case PacketType.PING:
                    pass

                case PacketType.LEVEL_INIT:
                    ConsoleWriter.write_info("Server is sending the level...")

                case PacketType.LEVEL_DATA:
                    packet.read_short()
                    packet.read_byte_array()
                    percent = packet.read_byte()
                    ConsoleWriter.write_info(f"Server sent {percent}% of the level")

                case PacketType.LEVEL_END:
                    packet.read_short()
                    packet.read_short()
                    packet.read_short()
                    ConsoleWriter.write_info(f"Server has finished sending the level")

                case PacketType.UPDATE_TILE:
                    pass

                case PacketType.PLAYER_JOIN:
                    id = packet.read_sbyte()
                    packet.read_string()
                    x = packet.read_short() / 32 
                    y = packet.read_short() / 32 
                    z = packet.read_short() / 32  
                    yaw = packet.read_byte() * 320 / 256
                    packet.read_byte()

                    if id < 0:
                        instance.spawn_x = x
                        instance.spawn_y = y
                        instance.spawn_z = z
                        instance.spawn_yaw = yaw
                        instance.entity_x = x
                        instance.entity_y = y
                        instance.entity_z = z
                        instance.entity_yaw = yaw
                        instance.entity_pitch = 0
                        ConsoleWriter.write_info(f"Received spawnpoint -> X:{x} Y:{y} Z:{z} Yaw:{yaw}")
                        ConsoleWriter.write_cc("&1(INFO) &2Welcome to &6PYClassicChat&2!")
                        ConsoleWriter.write_cc("&1(INFO) &2Type &6.help &2to get a list of &5client side commands")

                case PacketType.PLAYER_TELEPORT:
                    id = packet.read_sbyte()
                    x = packet.read_short() / 32 
                    y = packet.read_short() / 32 
                    z = packet.read_short() / 32  
                    yaw = packet.read_byte() * 320 / 256
                    pitch = packet.read_byte() * 320 / 256

                    if id < 0:
                        ConsoleWriter.write_info(f"Teleported by the server -> X:{x} Y:{y} Z:{z} Yaw:{yaw} Pitch:{pitch}")
                        instance.entity_x = x
                        instance.entity_y = y
                        instance.entity_z = z
                        instance.entity_yaw = yaw
                        instance.entity_pitch = pitch

                case PacketType.PLAYER_MOVE_ROTATE:
                    pass

                case PacketType.PLAYER_MOVE:
                    pass

                case PacketType.PLAYER_ROTATE:
                    pass

                case PacketType.PLAYER_LEAVE:
                    pass

                case PacketType.CHAT:
                    packet.read_sbyte()
                    ConsoleWriter.write_cc(f"{_ANSI_CLEAR_LINE}\r{packet.read_string()}")

                case PacketType.LOGOUT:
                    ConsoleWriter.write_info(f"Kicked by the server: {packet.read_string()}")
                    instance.disconnect()
                    return
                
                case PacketType.UPDATE_USER_TYPE:
                    pass
        except Exception as ex:
            if not instance.connected:
                return
            ConsoleWriter.write_err(f"Encountered network error -> {ex}")
            instance.disconnect()

            return