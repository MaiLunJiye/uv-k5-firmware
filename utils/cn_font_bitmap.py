
"""
Copyright 2023 MaiLunjiye
https://github.com/MaiLunjiye

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import sys

STR_FILE = "./CN_list.txt"
FONT_FILE = "HZK12"

STR_LINES = []

class CharItem(object):
    def __init__(self, char):
        self.char = char
        self.cnt = 0
        self.origin_hexs = None
        self.uvk5_hexs = None
    
    def hexs2strs(self, hexs):
        return map(lambda x: "0x{:02x}".format(x), hexs)

    def origin2hexstr(self):
        return "{ " + ", ".join(self.hexs2strs(self.origin_hexs)) + " }"
    
    def uvk5_2hexstr(self):
        return "{ " + ", ".join(self.hexs2strs(self.uvk5_hexs)) + " }"
    
    def is_can_trans2uvk5(self):
        if self.origin_hexs is None:
            return False
        for num in self.origin_hexs[1::2]:
            if num & 0x0F != 0:
                return False

        return True
    
    def trans2UVK5(self):
        """
        FROM
            H             L  H             L
        0   □ □ ■ □ □ □ □ ■  □ □ □ □ □ □ □ □ 
        2   □ □ ■ □ □ □ □ ■  □ □ □ □ □ □ □ □ 
        4   □ ■ ■ ■ ■ □ ■ □  □ □ □ □ □ □ □ □ 
        6   □ ■ □ □ □ □ ■ ■  ■ ■ ■ ■ □ □ □ □ 
        8   ■ ■ ■ ■ ■ □ ■ □  □ □ ■ □ □ □ □ □ 
        10  □ □ ■ □ □ ■ □ ■  □ □ □ □ □ □ □ □ 
        12  □ □ ■ □ □ □ □ ■  □ □ □ □ □ □ □ □ 
        14  ■ ■ ■ ■ ■ □ □ ■  □ □ □ □ □ □ □ □ 
        16  □ □ ■ □ □ □ ■ □  ■ □ □ □ □ □ □ □ 
        18  □ □ ■ □ ■ □ ■ □  □ ■ □ □ □ □ □ □ 
        20  □ □ ■ ■ □ ■ □ □  □ □ ■ □ □ □ □ □ 
        22  □ □ ■ □ ■ □ □ □  □ □ □ ■ □ □ □ □ 
        
        TO
            0 1 2 3 4 5 6 7  8 9 10 11
        L   □ □ ■ □ □ □ □ ■  □ □ □ □  □ □ □ □ 
            □ □ ■ □ □ □ □ ■  □ □ □ □  □ □ □ □ 
            □ ■ ■ ■ ■ □ ■ □  □ □ □ □  □ □ □ □ 
            □ ■ □ □ □ □ ■ ■  ■ ■ ■ ■  □ □ □ □ 
            ■ ■ ■ ■ ■ □ ■ □  □ □ ■ □  □ □ □ □ 
            □ □ ■ □ □ ■ □ ■  □ □ □ □  □ □ □ □ 
            □ □ ■ □ □ □ □ ■  □ □ □ □  □ □ □ □ 
        H   ■ ■ ■ ■ ■ □ □ ■  □ □ □ □  □ □ □ □ 

        L   □ □ ■ □ □ □ ■ □  ■ □ □ □  □ □ □ □ 
            □ □ ■ □ ■ □ ■ □  □ ■ □ □  □ □ □ □ 
            □ □ ■ ■ □ ■ □ □  □ □ ■ □  □ □ □ □ 
        H   □ □ ■ □ ■ □ □ □  □ □ □ ■  □ □ □ □ 
            12| 13| 14| 15|  16| 17|
            H L
        """
        if self.is_can_trans2uvk5() is not True:
            return

        self.uvk5_hexs = []
        for out_idx in range(8):  # 0-7
            res = 0
            in_mask = 0x80 >> out_idx
            for in_idx, in_byte in enumerate(self.origin_hexs[0:16:2]):
                bit = 0
                if in_mask & in_byte == 0:
                    bit = 0
                else:
                    bit = 1
                res |= (bit << in_idx)
            self.uvk5_hexs.append(res)
        
        for out_idx in range(4):  # 8,9,10,11
            res = 0
            in_mask = 0x80 >> out_idx
            for in_idx, in_byte in enumerate(self.origin_hexs[1:16:2]):
                bit = 0
                if in_mask & in_byte == 0:
                    bit = 0
                else:
                    bit = 1
                res |= (bit << in_idx)
            self.uvk5_hexs.append(res)
        
        for out_idx in range(4): # 12 - 15
            res = 0
            in_mask_h = 0x80 >> (out_idx * 2)
            in_mask_l = 0x40 >> (out_idx * 2)
            for in_idx, in_byte in enumerate(self.origin_hexs[16:24:2]):
                bit_h = 0
                if in_mask_h & in_byte == 0:
                    bit_h = 0
                else:
                    bit_h = 1
                res |= bit_h << (in_idx + 4)

                bit_l = 0
                if in_mask_l & in_byte == 0:
                    bit_l = 0
                else:
                    bit_l = 1
                res |= bit_l << (in_idx)
            self.uvk5_hexs.append(res)

        for out_idx in range(2): # 16,17
            res = 0
            in_mask_h = 0x80 >> (out_idx * 2)
            in_mask_l = 0x40 >> (out_idx * 2)
            for in_idx, in_byte in enumerate(self.origin_hexs[17:24:2]):
                bit_h = 0
                if in_mask_h & in_byte == 0:
                    bit_h = 0
                else:
                    bit_h = 1
                res |= bit_h << (in_idx + 4)

                bit_l = 0
                if in_mask_l & in_byte == 0:
                    bit_l = 0
                else:
                    bit_l = 1
                res |= bit_l << (in_idx)
            self.uvk5_hexs.append(res)

class CharSet_CN(object):
    def __init__(self, font_file, font_m_len, str_file):
        self.font_file = font_file
        self.font_block = None
        self.font_m_len = font_m_len

        self.str_file = str_file

        self.lines = []
        self.char_dict = {}
        self.read_files()
        self.get_hexs()
    
    def read_files(self):
        with open(FONT_FILE, 'rb') as fh:
            self.block = fh.read()

        self.lines.clear()
        with open(STR_FILE, 'r') as fh:
            for line in fh:
                STR_LINES.append(line.strip())
                for c in line:
                    if c.isascii():
                        continue
                    if c not in self.char_dict:
                        new_char = CharItem(c)
                        new_char.cnt = 1
                        self.char_dict[c] = new_char
                    else:
                        self.char_dict[c].cnt += 1

    def get_origin_hexs(self, c):
        c_gb2312 = int.from_bytes(c.encode('gb2312'), 'big')
        idx = ((c_gb2312 >> 8) - 0xa1) * 94 + (c_gb2312 & 0xff) - 0xa1
        c_m = []
        for i in range(self.font_m_len):
            c_m.append(self.block[idx * self.font_m_len + i])
        return c_m


    def get_hexs(self):
        for c, char_item in self.char_dict.items():
            char_item.origin_hexs = self.get_origin_hexs(c)
            char_item.trans2UVK5()

    def printUVK5(self):
        for c, char_item in self.char_dict.items():
            print(f"{char_item.uvk5_2hexstr()} // {c}")

    

cs = CharSet_CN(FONT_FILE, 12 * 2, STR_FILE)
cs.printUVK5()
