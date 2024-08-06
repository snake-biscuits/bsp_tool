#!/usr/bin/python3
# https://github.com/ata4/bspsrc/blob/master/src/main/java/info/ata4/bsplib/BspFile.java#L254
# https://github.com/ata4/bspsrc/blob/master/src/main/java/info/ata4/io/util/XORUtils.java
import shutil
import sys


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} FILENAME_TO_DECRYPT")
        sys.exit(0)

    with open(sys.argv[1], "rb") as encrypted_file:
        encrypted_file.seek(384)
        key = encrypted_file.read(32)
        encrypted_file.seek(0)
        encrypted_data = encrypted_file.read()

    shutil.copyfile(f"{sys.argv[1]}.backup")
    long_key = key * (len(encrypted_data) // 32 + 1)

    with open(sys.argv[1], "wb") as decrypted_file:
        decrypted_file.write(bytes([b ^ k for b, k in zip(encrypted_data, long_key)]))
