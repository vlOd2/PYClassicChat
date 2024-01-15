import socket
import threading
import re
import sys
from time import time, sleep
from Console import ConsoleWriter
from Console.ConsoleReader import ConsoleReader
from colorama.ansi import Fore, Style
from Network import ClassicPacket
from Network.ClassicPacket import PacketType
from Network.ClassicBytes import ClassicBytes

# Constants
_INPUT_REGEX = r"^[a-zA-Z0-9.,:\\\-\'*!\"#%/\(\)=+?\[\]\{\}<>@|$; ]*$"
_USERNAME_REGEX = r"^(?=.{3,16}$)[a-zA-Z0-9_]+$";
_PROTOCOL_VERSION = 7

class PYClassicChat():
    username : str | None = None
    connected : bool = True
    client_socket : socket.socket = None
    client_recv_thread : threading.Thread | None = None
    spawn_x : float = 0
    spawn_y : float = 0
    spawn_z : float = 0
    spawn_yaw : float = 0
    entity_x : float = 0
    entity_y : float = 0
    entity_z : float = 0
    entity_yaw : float = 0
    entity_pitch : float = 0

    def __init__(self) -> None:
        self.client_socket = socket.socket(socket.AddressFamily.AF_INET, 
                                                socket.SocketKind.SOCK_STREAM, 
                                                socket.IPPROTO_TCP)
        
    def disconnect(self) -> None:
        ConsoleWriter.write_info("Disconnecting...")
        self.connected = False

        if self.client_socket:
            self.client_socket.close()

        if self.client_recv_thread:
            self.client_recv_thread.join()

    def main(self) -> None:
        # XXX: To avoid circular imports
        from ClientSideCommands import handle_client_side_cmd
        from Network.RecvThreadFunc import _recv_thread_func

        if len(sys.argv) < 3:
            ConsoleWriter.write_info(f"USAGE: {sys.argv[0]} <server:port> <username> [mppass]")
            return

        server_raw = sys.argv[1].split(":")
        self.username = sys.argv[2]
        mppass = sys.argv[3] if len(sys.argv) > 3 else "-"

        if len(server_raw) < 2:
            ConsoleWriter.write_err("Invalid server!")
            ConsoleWriter.write_info("NOTE: You must specify the port manually")
            return

        server_host = server_raw[0]
        server_port_raw = server_raw[1]
        server_port = 0

        if not server_port_raw.isdigit():
            ConsoleWriter.write_err("Invalid server port!")
            return
        else:
            server_port = int(server_port_raw)

        if not re.search(_USERNAME_REGEX, self.username):
            ConsoleWriter.write_err("Not a valid Minecraft username!")
            return

        ConsoleWriter.write_info(f"Connecting to {server_host}:{server_port} as {self.username}...")
        try:
            self.client_socket.connect((server_host, server_port))
        except Exception as ex:
            ConsoleWriter.write_info(f"Failed to connect: {ex}")
            self.connected = False
            return
        
        ConsoleWriter.write_info("Logging in...")
        # Send the login packet
        self.client_socket.send(ClassicPacket.build_login_packet(_PROTOCOL_VERSION, self.username, mppass))
        # Receive the response packet
        login_packet_size = 1 + ClassicPacket.get_packet_size(PacketType.LOGIN)
        login_packet = ClassicBytes(self.client_socket.recv(login_packet_size))
        login_packet_type = ClassicPacket.int2pt(login_packet.read_byte())
        
        if login_packet_type == None:
            ConsoleWriter.write_err("Received invalid packet!")
            self.disconnect()
            return

        if login_packet_type == PacketType.LOGOUT:
            ConsoleWriter.write_info(f"Failed to login: {login_packet.read_string()}")
            self.disconnect()
            return
        elif login_packet_type != PacketType.LOGIN:
            ConsoleWriter.write_err("Received illegal packet!")
            self.disconnect()
            return

        # Just in-case you join some wonky server
        if login_packet.read_byte() != _PROTOCOL_VERSION:
            ConsoleWriter.write_err("Mismatched protocol version!")
            self.disconnect()
            return

        ConsoleWriter.write_info(f"Server name: {login_packet.read_string()}")
        ConsoleWriter.write_info(f"Server MOTD: {login_packet.read_string()}")
        ConsoleWriter.write_info(f"Operator status: {login_packet.read_byte() == 0x64}")

        ConsoleWriter.write_info("Starting receive thread...")
        client_recv_thread = threading.Thread(target=lambda: _recv_thread_func(self))
        client_recv_thread.start()

        # Use ConsoleReader for more control and no blocking
        console_reader = ConsoleReader()
        user_input = ""

        # Keep track of when we last sent a teleport packet
        last_teleport_packet = 0

        # Loop that runs whilst connected
        while self.connected:
            try:
                if last_teleport_packet < time():
                    self.client_socket.send(ClassicPacket.build_teleport_packet(self.entity_x, self.entity_y, self.entity_z, 
                                                                                self.entity_yaw, self.entity_pitch))
                    last_teleport_packet = time() + 1

                # XXX: Janky way to always print the user prompt at the bottom
                if ConsoleWriter.modified_stdout:
                    ConsoleWriter.modified_stdout = False
                    sleep(0.1)
                    if not ConsoleWriter.modified_stdout:
                        print(f"{Fore.GREEN}{self.username}@{server_host}:{server_port}{Style.RESET_ALL}$ {user_input}", end="", flush=True)

                if console_reader.update():
                    code = console_reader.read()
                    c = chr(code)

                    if code == 0x0A or code == 0x0D:
                        # Handle enter
                        ConsoleWriter.write("")
                        
                        if user_input.startswith("."):
                            handle_client_side_cmd(user_input[1:], self)
                        else:
                            self.client_socket.send(ClassicPacket.build_chat_packet(user_input))

                        user_input = ""
                    elif code == 0x08 or code == 0x7F:
                        # Handle backspace (delete is usually used on Linux)
                        if len(user_input) < 1:
                            continue

                        print("\b \b", end="", flush=True)
                        user_input = user_input[:-1]
                    else:
                        # Handle regular key
                        if (not re.search(_INPUT_REGEX, c) or len(user_input) + 1 > 64 or 
                            ((code == 0 or code == 0xE0) and console_reader.parse_arrow(console_reader.read()) != -1)):
                            continue
                        
                        print(c, end="", flush=True)
                        user_input += c
            except KeyboardInterrupt:
                self.disconnect()
                
        console_reader.cleanup()

if __name__ == "__main__":
    PYClassicChat().main()