import os

empty_zip_file = b"PK\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
"\x00\x00\x00\x00\x00 \x00XZP1 0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

def tf2m_compliance_test(bsp, mdls, vmts):
        complies = True
        filename = os.path.basename(bsp.filename)
        if bsp.RAW_LIGHTING.replace(b'\x00', b'') == b'':
            print(f"{filename} is fullbright")
            complies = False
        #if not hasattr(self, 'LIGHTING_HDR'):
            # {filename} was not compiled with HDR
        
        has_cubemaps = True if hasattr(bsp, "CUBEMAPS") else False
        
        if self.RAW_PAKFILE == empty_zip_file:
            if cubemaps:
                # maps/{mapname}/texdir/texture_X_Y_Z.vmt (cubemap)
                # check all XYZs and XYZ_hdrs are packed
                print(f"{filename}'s cubemaps have not been compiled")
            else:
                print(f"{filename} has no packed assets")
        else:
            if b'.vhv'in bsp.RAW_PAKFILE:
                print(f"{filename}'s cubemaps are compiled and packed!")
        
        for material in bsp.TEXDATA_STRING_DATA:
            vmt = 'materials/' + material.lower() + '.vmt'
            if material_name not in vmts:
                print('{filename} references {material} and is', end=' ')
                if bytes(vmt, 'utf-8') in self.RAW_PAKFILE:
                    pass # material is packed
                else: # a custom material is not packed
                    # recorded missed material in log
                    complies = False

        referenced_models
        # search "sprp" GAME_LUMP    
        for entity in self.ENTITIES:
            if 'prop' in entity.classname:
                referenced_models.append(entity['model'])
        # check all models are either in vpk or pakfile
        # log all unpacked assets
        
        return complies
