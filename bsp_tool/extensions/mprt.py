import struct


def generate(bsp, filename=""):
    if filename == "":
        filename = f"{bsp.filename.split('.')[0]}.mprt"
    with open(filename, "wb") as mprt_file:
        mprt_file.write(b"mprtFAKE")
        mprt_file.write(len(bsp.GAME_LUMP.sprp.props).to_bytes(4, "little"))
        for prop in bsp.GAME_LUMP.sprp.props:
            model_name = bsp.GAME_LUMP.sprp.model_names[prop.model_name].replace("\\", "/").rpartition("/")[2]
            model_name = model_name[:-4]  # strip .mdl from tail
            mprt_file.write(model_name.encode() + b"\0")
            position = prop.origin
            rotation = (prop.angles[2], prop.angles[0], prop.angles[1])
            scale = prop.scale
            mprt_file.write(struct.pack("7f", *position, *rotation, scale))
