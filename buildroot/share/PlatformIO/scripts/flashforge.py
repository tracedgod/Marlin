#
# flashforge.py
# Customizations for FlashForge build environments:
#   env: FLASHFORGE_DREAMER       FlashForge Dreamer
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

    def xor_byte(data):
        if data & 0x80:
            return ((data << 1) ^ 0x1B) & 0xFF
        else:
            return (data << 1) & 0xFF

    def generate_xor_table(key):
        xor_key_table = [bytearray(key, 'utf-8') for _ in range(11)]
        xor_key = 1

        for i in range(4, 44):
            index = i // 4
            xor_key_table[index] = xor_key_table[index - 1][:]

            if i % 4 == 0:
                xor_key_table[index] = xor_key_table[index][1:] + xor_key_table[index][:1]
                xor_key_table[index] = bytes(swap_table_encode[x] for x in xor_key_table[index])
                xor_key_table[index] = bytearray(xor_key_table[index])
                xor_key_table[index] = bytearray((xor_key_table[index][j] ^ xor_key) for j in range(16))
                xor_key = xor_byte(xor_key & 0xFF)

            for j in range(16):
                xor_key_table[index][j] ^= xor_key_table[index - 1][j]

        return xor_key_table

    def xor_data_buffer(pbuf, pkey):
        pbuf = bytearray(pbuf)
        pkey = bytearray(pkey)

        for i in range(len(pbuf)):
            pbuf[i] ^= pkey[i % len(pkey)]

        return bytes(pbuf)

    def swap_data_buffer(pdata):
        pdata = bytearray(pdata)

        for i in range(len(pdata)):
            if pdata[i] < len(swap_table_encode):
                pdata[i] = swap_table_encode[pdata[i]]

        return bytes(pdata)

    def shuffle_data_buffer(pdata):
        pdata = bytearray(pdata)
        tmp = bytearray(4)

        # Iterate over the range of indices that are within the length of pdata
        for i in range(1, min(len(pdata), 17), 4):
            for j in range(4):
                if 4 * j + i < len(pdata):
                    tmp[j] = pdata[4 * j + i]
                else:
                    tmp[j] = 0
            pos = 4 - i
            for n in range(4):
                index = 4 * n + i
                if index < len(pdata):
                    pdata[index] = tmp[(pos + n) % 4]

        return bytes(pdata)

    def xor_data_block(pdata):
        pdata = bytearray(pdata)
        xor_array = bytearray(4)
        
        for i in range(0, len(pdata), 4):
            xor_key = pdata[i] ^ pdata[i + 1] ^ pdata[i + 2] ^ pdata[i + 3]
            xor_array[0] = xor_byte(pdata[i] ^ pdata[i + 1]) ^ (pdata[i] ^ xor_key)
            xor_array[1] = xor_byte(pdata[i + 1] ^ pdata[i + 2]) ^ (pdata[i + 1] ^ xor_key)
            xor_array[2] = xor_byte(pdata[i + 2] ^ pdata[i + 3]) ^ (pdata[i + 2] ^ xor_key)
            xor_array[3] = xor_byte(pdata[i + 3] ^ pdata[i]) ^ (pdata[i + 3] ^ xor_key)
            pdata[i:i + 4] = xor_array
    
        return bytes(pdata)

    def encrypt_data_block(pdata, xor_key_table):
        pdata = xor_data_buffer(pdata, xor_key_table[0])
        pdata = swap_data_buffer(pdata)
        pdata = shuffle_data_buffer(pdata)
        pdata = xor_data_block(pdata)
        pdata = xor_data_buffer(pdata, xor_key_table[1])

        return pdata

    def encrypt_data_buffer(pdata, size, pkey):
        xor_key_table = generate_xor_table(pkey)
        encrypted_data = b""
        for i in range(0, size, 16):
            encrypted_data += encrypt_data_block(pdata[i:i + 16], xor_key_table)
        return encrypted_data

    def encrypt_file(input_file, output_file, key):
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"File '{input_file}' not found.")

        if os.path.exists(output_file):
            os.remove(output_file)

        print(
            f"Encoding binary {input_file} to file {output_file} with key: {key}"
        )
        with open(input_file, "rb") as ifile, open(output_file, "wb") as ofile:
            data = ifile.read()
            encrypted_data = encrypt_data_buffer(data, len(data), key)
            ofile.write(encrypted_data)

        return encrypted_data

    def encrypt_flashforge(source, target, env):
       fwpath = target[0].path
       enname = board.get("build.encrypt_flashforge_bin")
       enkey = board.get("build.encrypt_flashforge_key")
       enfile = target[0].dir.path + "/" + enname

       encrypt_file(fwpath, enfile, enkey)

       os.remove(fwpath)

       print("Successfully encoded binary")

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