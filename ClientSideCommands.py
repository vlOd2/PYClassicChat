from PYClassicChat import PYClassicChat
from ClientSideCMDRegister import *
from Console import ConsoleWriter
from Network import ClassicPacket
import Utils

@CommandDeclaration("help", "Lists all registered commands")
def _cmd_help(args : list[str], instance : PYClassicChat) -> None:
    ConsoleWriter.write_info(f"Available commands:")
    for cmd, func_desc in REGISTERED_CMDS.items():
        ConsoleWriter.write_info(f"  .{cmd} - {func_desc[1]}")

@CommandDeclaration("close", "Closes the connection to the server")
def _cmd_close(args : list[str], instance : PYClassicChat) -> None:
    instance.disconnect()

@CommandDeclaration("getpos", "Gets the current position")
def _cmd_getpos(args : list[str], instance : PYClassicChat) -> None:
    str = (
        f"X:{instance.entity_x} "
        f"Y:{instance.entity_y} "
        f"Z:{instance.entity_z} "
        f"Yaw:{instance.entity_yaw} "
        f"Pitch:{instance.entity_pitch}"
    )
    ConsoleWriter.write_info(str)

@CommandDeclaration("setpos", "Sets the current position")
def _cmd_setpos(args : list[str], instance : PYClassicChat) -> None:
    if len(args) < 3:
        ConsoleWriter.write_info("USAGE: setpos <x> <y> <z> <yaw> <pitch>")
        return
    
    x_raw = args[0]
    y_raw = args[1]
    z_raw = args[2]
    yaw_raw = args[3]
    pitch_raw = args[4]

    if (not Utils.is_float(x_raw) or not Utils.is_float(y_raw) or not Utils.is_float(z_raw) or 
        not Utils.is_float(yaw_raw) or not Utils.is_float(pitch_raw)):
        ConsoleWriter.write_err("Invalid arguments provided!")
        return
    
    instance.entity_x = float(x_raw)
    instance.entity_y = float(y_raw)
    instance.entity_z = float(z_raw)
    instance.entity_yaw = float(yaw_raw)
    instance.entity_pitch = float(pitch_raw)

    str = (
        "Set the position successfully ("
        f"X:{instance.entity_x} "
        f"Y:{instance.entity_y} "
        f"Z:{instance.entity_z} "
        f"Yaw:{instance.entity_yaw} "
        f"Pitch:{instance.entity_pitch})"
    )
    ConsoleWriter.write_info(str)

@CommandDeclaration("settile", "Sets a tile in the level")
def _cmd_settile(args : list[str], instance : PYClassicChat) -> None:
    if len(args) < 4:
        ConsoleWriter.write_info("USAGE: settile <x> <y> <z> <id>")
        return
    
    x_raw = args[0]
    y_raw = args[1]
    z_raw = args[2]
    id_raw = args[3]

    if (not Utils.is_int(x_raw) or not Utils.is_int(y_raw) or 
        not Utils.is_int(z_raw) or not Utils.is_int(id_raw)):
        ConsoleWriter.write_err("Invalid arguments provided!")
        return
    
    x = int(args[0])
    y = int(args[1])
    z = int(args[2])
    id = int(args[3])

    if id < 0 or id > 49:
        ConsoleWriter.write_err("Invalid tile ID provided!")
        return

    instance.client_socket.send(ClassicPacket.build_place_break_tile_packet(x, y, z, id > 0, id if id > 0 else 1))
    ConsoleWriter.write_info(f"Set the tile X:{x},Y:{y},Z:{z} to {id}")

def handle_client_side_cmd(cmd : str, instance : PYClassicChat) -> None:
    cmd_raw = cmd.split(" ")
    name = cmd_raw[0]
    args = cmd_raw[1:]

    if not name in REGISTERED_CMDS:
        ConsoleWriter.write_err(f"Invalid command \"{name}\"")
        return

    REGISTERED_CMDS[name][0](args, instance)