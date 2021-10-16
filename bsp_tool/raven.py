from . import id_software


class RavenBsp(id_software.IdTechBsp):
    file_magic = b"RBSP"

    # includes marker lump:
    # https://github.com/TTimo/GtkRadiant/blob/master/tools/urt/tools/quake3/q3map2/bspfile_rbsp.c#L308
    # sprintf( marker, "I LOVE MY Q3MAP2 %s on %s)", Q3MAP_VERSION, asctime( localtime( &t ) ) );
