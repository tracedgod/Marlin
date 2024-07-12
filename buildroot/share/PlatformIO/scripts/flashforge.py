# 
#   *========================================================================*
#   | File: flashforge.py                                                    |
#   | Author: Trace Bowes (tracedgod)                                        |
#   | Description: Post-Build Firmware Encoding on FlashForge_FF407ZG Boards |
#   |------------------------------------------------------------------------|
#   | Used in the following Environments:                                    |
#   | env: FLASHFORGE_DREAMER       FlashForge Dreamer                       |
#   *========================================================================*
# 

import pioutil
if pioutil.is_pio_build():
    import os,struct,marlin

    board = marlin.env.BoardConfig()

    swap_table_encode = [
        0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
        0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
        0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
        0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
        0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
        0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
        0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
        0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
        0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
        0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
        0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
        0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
        0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
        0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
        0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
        0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
    ]

    xor_key_table = [bytearray(16) for _ in range(11)]

    def xor_data_buffer(pbuf, pkey, size):
        if isinstance(pkey, int):
            key_int = [pkey] * size
        else:
            key_int = [ord(c) for c in pkey]
        pbuf = bytearray(pbuf)
        for i in range(size):
            pbuf[i] ^= key_int[i % len(key_int)]
        return pbuf
    
    def swap_data_buffer(pdata, size):
        swap_table = swap_table_encode
        pdata = bytearray(pdata)
        for i in range(size):
            pdata[i] = swap_table[pdata[i]]

    def shuffle_data_buffer(pdata):
        tmp = [0] * 4
        pdata = bytearray(pdata)
        if len(pdata) < 16:
            return

        for i in range(1, 4):
            for j in range(4):
                if 4 * j + i < len(pdata):
                    tmp[j] = pdata[4 * j + i]
                else:
                    return
            pos = i
            for n in range(4):
                if 4 * n + i < len(pdata):
                    pdata[4 * n + i] = tmp[(pos + n) % 4]

    def xor_byte(data):
        return (data << 1) ^ 0x1B if data & 0x80 else (data << 1) & 0xFF

    def xor_data_block(pdata):
        xor_array = [0] * 4
        pdata = bytearray(pdata)
        for i in range(4):
            xor_key = pdata[0] ^ pdata[1] ^ pdata[2] ^ pdata[3]
            xor_array[0] = xor_byte(pdata[0] ^ pdata[1]) ^ (pdata[0] ^ xor_key)
            xor_array[1] = xor_byte(pdata[1] ^ pdata[2]) ^ (pdata[1] ^ xor_key)
            xor_array[2] = xor_byte(pdata[2] ^ pdata[3]) ^ (pdata[2] ^ xor_key)
            xor_array[3] = xor_byte(pdata[3] ^ pdata[0]) ^ (pdata[3] ^ xor_key)
            xor_array = [x % 256 for x in xor_array]
            pdata[:4] = xor_array
        return pdata

    def encrypt_data_block(pdata, xor_key_table, pkey):
        encrypted_data = bytearray(pdata)
        encrypted_data = xor_data_buffer(encrypted_data, str(xor_key_table), len(encrypted_data))

        for i in range(1, 11):
            swap_data_buffer(encrypted_data, len(encrypted_data))
            shuffle_data_buffer(encrypted_data)
            if i != 10:
                encrypted_data = xor_data_block(encrypted_data)
            encrypted_data = xor_data_buffer(encrypted_data, xor_key_table[i], len(encrypted_data))

        return encrypted_data

    def encrypt_data_buffer(data, length, key, xor_key_table):
        if isinstance(key, int):
            key_int = [key] * 16
        else:
            key_int = [ord(c) for c in str(key)]

        encrypted_data = bytearray(data)
        for i in range(0, length, 16):
            pdata = encrypted_data[i:i + 16]
            xor_key_index = i // 16 % 11
            encrypted_block = encrypt_data_block(pdata, xor_key_table[xor_key_index], key_int)
            encrypted_data[i:i + 16] = encrypted_block
        return encrypted_data

    def rol_bytes(p):
        t = p[0]
        p[0] = p[1]
        p[1] = p[2]
        p[2] = p[3]
        p[3] = t

    def generate_xor_table(psz_key):
        key_len = len(psz_key)
        if key_len != 16:
            return -1

        xor_key_table[0][:key_len] = psz_key.encode()

        for i in range(1, 11):
            xor_data_buffer(xor_key_table[i - 1], str(xor_key_table[i - 1]), 16)
            xor_key = 0
            for j in range(4):
                xor_key_table[i][4 * j:4 * (j + 1)] = xor_data_buffer(xor_key_table[i - 1][4 * j:4 * (j + 1)], str(xor_key_table[i - 1]), 4)
                xor_key = xor_byte(xor_key & 0xFF)
            rol_bytes(xor_key_table[i])
            xor_data_buffer(xor_key_table[i], str(xor_key_table[i]), 16)

        return xor_key_table

    def encrypt_file(input_file, output_file, key):
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"File '{input_file}' not found.")

        if os.path.exists(output_file):
            os.remove(output_file)

        print(f"Encoding binary {input_file} to file {output_file} using key: {key}")

        key = str(key)

        xor_key_table = generate_xor_table(key)
        # print("XOR Key Table:")
        # for i, table in enumerate(xor_key_table):
        #     print(f"Table {i}: {table}")

        with open(input_file, "rb") as ifile, open(output_file, "wb") as ofile:
            while True:
                data = ifile.read(2048)
                if not data:
                    break

                if len(data) < 16:
                    data += bytes(16 - len(data))

                encrypted_data = encrypt_data_buffer(data, len(data), key, xor_key_table)
                ofile.write(encrypted_data)

        print("Finished encoding")
    
    def encrypt_flashforge(source, target, env):
       fwpath = target[0].path
       enname = board.get("build.encrypt_flashforge_bin")
       enkey = board.get("build.encrypt_flashforge_key")
       enfile = target[0].dir.path + "/" + enname

       encrypt_file(fwpath, enfile, enkey)

       os.remove(fwpath)

    if 'encrypt_flashforge_bin' in board.get("build").keys() and 'encrypt_flashforge_key' in board.get("build").keys():
       marlin.add_post_action(encrypt_flashforge)
    elif 'encrypt_flashforge_bin' in board.get("build").keys() and 'encrypt_flashforge_key' not in board.get("build").keys():
       print("board_build.encrypt_flashforge_bin not specified.\n")
       exit(1)
    elif 'encrypt_flashforge_bin' not in board.get("build").keys() and 'encrypt_flashforge_key' in board.get("build").keys():
      print("board_build.encrypt_flashforge_key not specified.\n")
      exit(2)
    elif 'encrypt_flashforge_bin' not in board.get("build").keys() and 'encrypt_flashforge_key' not in board.get("build").keys():
      print("neither board_build.encrypt_flashforge_bin or board_build.encrypt_flashforge_key specified.\n")
      exit(3)