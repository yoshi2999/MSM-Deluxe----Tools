import os
import struct
from functools import partial
from tkinter import Tk, Button, Label, Entry
from tkinter.filedialog import askopenfilename, askdirectory

if ':\\Windows' in os.getcwd():
    os.chdir(os.environ['userprofile'] + '\\Desktop')

install_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(install_dir, '#language.txt'), 'r', encoding="utf-8") as txt:
    language = txt.read()
    language = [''] + language.splitlines()
    
n = os.path.join(install_dir, 'n.exe')

arc = int(language[1].split(":")[7])
start = int(language[1].split(":")[15])
msm = int(language[1].split(":")[1])
hashtag = int(language[1].split(":")[3])
miku = int(language[1].split(":")[33])
a = Tk()
a.title(language[miku])
a.minsize(660, 440)
a.config(bg='#dfffaa')
ico = os.path.join('msm_stuff', 'miku.ico')
a.iconbitmap(os.path.join(install_dir, ico))
print(language[miku + 9])
print(language[miku + 10])
thrice = [b'U\xaa8-', b'bres', b'\x00 \xaf0', b'\x00\x00\x00\x00']  # arc, brres, tpl and rso files
twice = thrice[:2]
extensions = ['.mdl', '.bin', '.cmp', '.mot']  # extensions of compressed files recognized
# burow_extract = [6, 6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 10] + [6, 7, 8, 9, 10] * 5 + [11] * 8 + [12] * 8 + [13] * 8 + [14] * 8 + [15] * 8 + [16] * 8 + [17] * 8
# bucolumn = [0] + [0, 1, 2] * 5 + [3] * 5 + [4] * 5 + [5] * 5 + [6] * 5 + [7] * 5 + [0, 1, 2, 3, 4, 5, 6, 7] * 7
burow_extract = []
for j in range(6, 11):
    burow_extract += [j, j, j]
for j in range(6, 11):
    burow_extract += [j, j, j, j]
for j in range(11, 18):
    burow_extract += [j, j, j, j, j, j, j]

bucolumn = [0, 1, 2] * 5 + [3, 4, 5, 6] * 5 + [0, 1, 2, 3, 4, 5, 6] * 7

burow_repack = [burow_extract[i] + 16 for i in range(len(burow_extract))]

extract_list = []
repack_list = []

##################################################################################
#  TRANSLATION OF MSM BINARY TREE FROM C TO PYTHON 
#  SOURCE 1 : https://wiki.tockdom.com/wiki/BRRES_(File_Format)
#  SOURCE 2 : https://wiki.tockdom.com/wiki/BRRES_Index_Group_(File_Format)
#  Feel free to copy and paste this part into your own file,
#  All functions will not depend on any external variable or file.
##################################################################################
"""The ID of each entry is not a unique number, but is calculated from the name comparing it to another name (see below) and used to search for a given entry. The entries form a binary search tree, with the first entry being the root. The left and right indicies describe this tree.
Calculation of the ID

The ID is calculated by comparing a filename (subject) to an other filename (object) using the following algorithm:

    Find the last non equal character of both names and store the INDEX.
        If the length of the subject filename is greater than the length of the object filename, INDEX is the length of the subject filename minus 1.
        Otherwise compare each pair of characters until a difference is found.
    Now compare both characters of position INDEX and find the highest bit that is not equal. If INDEX exceeds the length of object, assume character value 0. Store the bit index (7 for 0x80 .. 0 for 0x01) as BITNUM.
    Calculate: ID := INDEX << 3 | BITNUM

Initially the subject filename is compared with the the root filename, which is always empty. If an ID with the same value is found while walking through the tree, then a new ID is calculated using the other filename as object. 
"""

def get_highest_bit(val):
    i = 7
    while i > 0 and not (val & 0x80):
        i -= 1
        val <<= 1
    return i


def calc_brres_id (
      object_name,
     object_len,
      subject_name,
     subject_len
):
    if ( object_len < subject_len ):
        return subject_len - 1 << 3 | get_highest_bit(ord(subject_name[subject_len-1]))

    while ( subject_len > 0 ):
    
        subject_len -= 1
        ch = ord(object_name[subject_len]) ^ ord(subject_name[subject_len])
        if (ch):
            return subject_len << 3 | get_highest_bit(ch)
    
    # default case if the root name is empty, for reference point
    return 65535 # ~(u16)0; // this was the C code


"""typedef struct brres_info_t
{
    u16  id;          // id
    u16  left_idx;    // left index
    u16  right_idx;   // right index
    ccp  name;        // pointer to name
    uint nlen;        // lenght of name

} brres_info_t;"""

# Define the structure as a dictionary
def create_brres_info(id, left_idx, right_idx, name, nlen):
    return {
        'id': id,
        'left_idx': left_idx,
        'right_idx': right_idx,
        'name': name,
        'nlen': nlen
    }

def ASSERT(var):
    if not var:
        raise InterruptedError
    
# info: a dictionnary with the C structure above
# id: a 2 bytes integer
def get_brres_id_bit (info, id):
    ASSERT(info) # check that info is not empty
    char_idx = id >> 3
    return char_idx < info["nlen"] and ord(info["name"][char_idx]) >> ( id & 7 ) & 1


def calc_brres_entry(info_list, entry_idx):
    ASSERT(info_list)
    
    # Extract entry
    entry = info_list[entry_idx]
    entry['id'] = calc_brres_id(0, 0, entry['name'], entry['nlen'])
    entry['left_idx'] = entry['right_idx'] = entry_idx
    
    # Previous item
    prev_idx = 0
    prev = info_list[prev_idx]
    
    # Current item
    current_idx = prev['left_idx']
    current = info_list[current_idx] if current_idx < len(info_list) else None
    
    is_right = False
    
    while current and entry['id'] <= current['id'] and current['id'] < prev['id']:
        if entry['id'] == current['id']:
            entry['id'] = calc_brres_id(current['name'], current['nlen'], entry['name'], entry['nlen'])
            if get_brres_id_bit(current, entry['id']):
                entry['left_idx'] = entry_idx
                entry['right_idx'] = current_idx
            else:
                entry['left_idx'] = current_idx
                entry['right_idx'] = entry_idx
        
        prev = current
        is_right = get_brres_id_bit(entry, current['id'])
        current_idx = current['right_idx'] if is_right else current['left_idx']
        current = info_list[current_idx] if current_idx < len(info_list) else None
    
    if current and current['nlen'] == entry['nlen'] and get_brres_id_bit(current, entry['id']):
        entry['right_idx'] = current_idx
    else:
        entry['left_idx'] = current_idx
    
    if is_right:
        prev['right_idx'] = entry_idx
    else:
        prev['left_idx'] = entry_idx


def calc_brres_entries(info_list):
    ASSERT(info_list)
    ASSERT(len(info_list) > 0)
    
    # Setup root entry
    root = info_list[0]
    root['id'] = 0xffff
    root['left_idx'] = root['right_idx'] = 0
    
    for idx in range(len(info_list)):
        calc_brres_entry(info_list, idx)

"""
# Example data for testing
info_list = [
    create_brres_info(id=0, left_idx=0, right_idx=0, name="", nlen=0),  # Root
    create_brres_info(id=0, left_idx=-1, right_idx=-1, name="3DModels(NW4R)", nlen=14),
    create_brres_info(id=0, left_idx=-1, right_idx=-1, name="Textures(NW4R)", nlen=14),
    create_brres_info(id=0, left_idx=-1, right_idx=-1, name="External", nlen=8)
]
calc_brres_entries(info_list)
print(info_list)"""

##################################################################################
#  REWRITE OF WSZST BRRES EXTRACTOR IN PYTHON BY HAND
#  ASSUMPTIONS : all ASSERT contents are true
#  SOURCE : me
#  USAGE : extract_brres('cmn_test_DECOMP.brres')
##################################################################################

msm_files_offset = []
msm_files_absolute_filepath = []
every_offset_of_a_new_thing = []
extracted_files = ['']


def extract_brres(brres):
    msm_files_offset.clear()
    msm_files_absolute_filepath.clear()
    every_offset_of_a_new_thing.clear()
    extracted_files.clear()
    with open(brres, "rb") as bina:
        data = bina.read(12)
        ASSERT(data[:4] == b'bres') # makes sure the file is a brres
        endian = data[4:6]
        # calculating filesize in case another editor added buch of crap after the end of the brres
        filesize = calc_int(data, 8, endian) # u32 = 4 bytes unsigned integer
        data += bina.read(filesize - 12) # read filesize minus what's already read
    # create extracted brres dir
    extracted_dir = os.path.splitext(brres)[0].split('_DECOMP')[0] + "_extracted"
    num = 1
    while os.path.exists(extracted_dir):
        if num == 1:
            extracted_dir = extracted_dir + str(num)
        else:
            extracted_dir = extracted_dir[:-len(str(num - 1))] + str(num)
        num += 1
    os.makedirs(extracted_dir)
    
    root_offset = calc_short(data, 12, endian) # u16 = 2 bytes unsigned short
    sections_number = calc_short(data, 14, endian) # number of files inside the first brres + 1
    # in cmn_test.bin, there are 1 mdl0 + 2 tex0 + 21 brres + 1 = 0x19 = 25
    
    # parse Brres Index Group 1
    ASSERT(data[root_offset:root_offset + 4] == b'root')
    # root_section_size = (data[root_offset + 4] << 24) + (data[root_offset + 5] << 16) + (data[root_offset + 6] << 8) + data[root_offset + 7] # u32
    parse_brres_index_group(data, root_offset + 8, "", extracted_dir, endian) # launch recursive func
    extract_msm_files(data)
    print(sections_number, extracted_files)
    ASSERT(sections_number == len(extracted_files) + 1)
    return extracted_dir # return extracted folder name

def calc_int(data, offset, endian):
    if endian == b'\xfe\xff': # big endian
        return (data[offset] << 24) + (data[offset + 1] << 16) + (data[offset + 2] << 8) + data[offset + 3] # u32integer
    elif endian == b'\xff\xfe': # little endian -> reversed order
        return (data[offset + 3] << 24) + (data[offset + 2] << 16) + (data[offset + 1] << 8) + data[offset] # u32integer
    else:
        raise RuntimeError # invalid endian
    
def calc_short(data, offset, endian):
    if endian == b'\xfe\xff': # big endian
        return (data[offset] << 8) + (data[offset + 1]) # u16 = 2 bytes unsigned short
    elif endian == b'\xff\xfe': # little endian -> reversed order
        return (data[offset + 1] << 8) + (data[offset]) # u16 = 2 bytes unsigned short
    else:
        raise RuntimeError # invalid endian

def hex_float(number): # number is of type float
    num = b''
    w = hex(struct.unpack('<I', struct.pack('<f', number))[0])[2:]
    # add zeros to always make the value length to 8
    # w = '0' * (8-len(w)) + w
    w = w.zfill(8)
    for octet in range(0, 8, 2):  # transform for example "3f800000" to b'\x3f\x80\x00\x00'
        num += bytes(chr(int(w[octet:(octet + 2)], 16)), 'latin-1')
    return num

def extract_brres_inside_brres(data, offset, root_name, root_absolute_filepath):
    endian = data[offset + 4: offset + 6]
    file_length = calc_int(data, offset + 8, endian) # u32
    with open(root_absolute_filepath, 'wb') as sub:
        sub.write(data[offset:offset+file_length])
        
def extract_xbin(data, offset, root_name, root_absolute_filepath, endian):
    file_length = calc_int(data, offset + 8, endian) # u32
    with open(root_absolute_filepath, 'wb') as sub:
        sub.write(data[offset:offset+file_length])
        
"""
algorithm:
parse 14 section offsets from 0x10 to 0x48
if zero, skip,  else parse brres index group at offset then change name offset for each entry
name offset is at the following offset, depending on the section it belongs to
section 0: skip
section 1: 0x08
section 2: 0x0c
section 3: 0x0c
section 4: 0x0c
section 5: 0x0c
section 6: 0x0c
section 7: 0x0c
section 8: 0x08 + (0x418 + 0x34 per new texture ref. textures int32 is at offset 0x2C of section 8)
section 9: skip
section 10: 0x38
section 11: skip
section 12: skip
section 13: 0x10
"""
name_offset_sections = [None, 0x08, 0x0c, 0x0c, 0xc, 0xc, 0xc, 0xc, 0x8, None, 0x38, None, None, 0x10]
# todo: know which sections are missing for v8, v9, and v10
def extract_mdl0(data, offset, file_length, root_name, endian, name_offset_in_the_header, version, extracted_data, sub_file_end):
    brres_index_groups_unsorted = {}
    entries_unsorted = {}
    sub_file_end += b'\x00' * 3
    x = 0x10
    for i in range(14): # TODO: change this number for other mdl0 versions than 11
        if version < 10 and i in [6, 7]:
            continue  # these sections don't exist in mdl0 version 8 and 9 
        if data[offset + x: offset + x + 4] != b'\x00' * 4: # if section exists
            brres_index_groups_unsorted[calc_int(data, offset + x, endian)] = i
        x += 4
    brres_index_groups = dict(sorted(brres_index_groups_unsorted.items()))
    
    for index, section in brres_index_groups.items(): # parse all brres index groups except the last one
        if section == 13:  # user data is at the end of the file
            continue
        entry_number = calc_int(data, offset + index + 4, endian)
        extracted_data += data[offset + len(extracted_data):offset + index + 24]
        x = index + 24
        for i in range(entry_number):  # parse each entry of the brres index group
            x += 8
            # print(section, index, x)
            # print(x)
            new_name_offset, sub_file_end = calc_new_name_offset(data, offset, x, endian, index, file_length, sub_file_end)
            entries_unsorted[calc_int(data, offset + x + 4, endian) + index] = section
            extracted_data += data[offset + x - 8:offset + x] + new_name_offset + data[offset + x + 4:offset + x + 8]
            x += 8
    entries = dict(sorted(entries_unsorted.items()))
    for index, section in entries.items():
        if name_offset_sections[section] is None:
            continue # no offset to change in this section
        x = name_offset_sections[section]
        new_name_offset, sub_file_end = calc_new_name_offset(data, offset, index + x, endian, index, file_length, sub_file_end)
        extracted_data += data[offset + len(extracted_data):offset + index + x] + new_name_offset
        if section == 8:
            x = 0x418
            num_textures = calc_int(data, offset + index + 0x2C, endian)
            for i in range(num_textures):
                new_name_offset, sub_file_end = calc_new_name_offset(data, offset, index + x, endian, index + x, file_length, sub_file_end)
                extracted_data += data[offset + len(extracted_data):offset + index + x] + new_name_offset
                x += 0x34
    if version == 11:
        # parse section 13, only here in mdl0 version 11
        entries_unsorted = {}
        for index, section in brres_index_groups.items(): # parse all brres index groups except the last one
            if section == 13:  # user data is at the end of the file
                entry_number = calc_int(data, offset + index + 8, endian)
                extracted_data += data[offset + len(extracted_data):offset + index + 28]
                x = index + 28
                for i in range(entry_number):  # parse each entry of the brres index group
                    x += 8
                    new_name_offset, sub_file_end = calc_new_name_offset(data, offset, x, endian, index, file_length, sub_file_end)
                    entries_unsorted[calc_int(data, offset + x + 4, endian) + index] = section
                    extracted_data += data[offset + x - 8:offset + x] + new_name_offset + data[offset + x + 4:offset + x + 8]
                    x += 8
        entries = dict(sorted(entries_unsorted.items()))
        for index, section in entries.items():
            x = name_offset_sections[section]
            new_name_offset, sub_file_end = calc_new_name_offset(data, offset, index + x, endian, index, file_length, sub_file_end)
            extracted_data += data[offset + len(extracted_data):offset + index + x] + new_name_offset
        
    extracted_data += data[offset + len(extracted_data):offset + file_length] + sub_file_end + b'\x00'
    return extracted_data

string_pool_table = {}

def extract_shp0(data, offset, file_length, root_name, endian, name_offset_in_the_header, extracted_data, sub_file_end):
    sub_file_end += b'\x00' * 3
    section_1_offset = calc_int(data, offset + 0x10, endian)
    section_2_offset = calc_int(data, offset + 0x14, endian)
    N_STR = calc_short(data, offset + section_1_offset - 6, endian)
    x = section_1_offset + 4
    data_offsets = []
    extracted_data += data[offset + len(extracted_data):offset + x + 20]
    entry_number = calc_int(data, offset + x, endian)
    x += 20
    for i in range(entry_number):  # parse each entry of the brres index group
        x += 8
        new_name_offset, sub_file_end = calc_new_name_offset(data, offset, x, endian, section_1_offset, file_length, sub_file_end)
        data_offsets.append(calc_int(data, offset + x + 4, endian) + section_1_offset + 4) # yeah, +4 because SHP0
        extracted_data += data[offset + x - 8:offset + x] + new_name_offset + data[offset + x + 4:offset + x + 8]
        x += 8
    if len(data_offsets) > 0:
        extracted_data += data[offset + x:offset + data_offsets[0]]
        data_offsets.sort()  # in case it isn't sorted already
    for i in range(entry_number):
        x = data_offsets[i]  # and -4 here because SHP0
        new_name_offset, sub_file_end = calc_new_name_offset(data, offset, x, endian, x - 4, file_length, sub_file_end)
        if i == entry_number - 1: # skip to section 2
            extracted_data += new_name_offset + data[offset + data_offsets[i] + 4:offset + section_2_offset]
        else:
            extracted_data += new_name_offset + data[offset + data_offsets[i] + 4:offset + data_offsets[i + 1]]
    x = section_2_offset
    for i in range(N_STR):
        new_name_offset, sub_file_end = calc_new_name_offset(data, offset, x, endian, section_2_offset, file_length, sub_file_end)
        extracted_data += new_name_offset
        x += 4
    extracted_data += data[offset + x: offset + file_length] + sub_file_end + b'\x00'
    return extracted_data
"""
SCN0 (File Format) Made by me
```Offset Size  Description
0x00    4    The magic "VIS0" to identify the sub file. 
0x04    4    Length of the sub file. (internal name/ other string at the end not counted)
0x08    4    Sub file version number. ( 00 00 00 04 else crash)
0x0C    4    Offset to outer BRRES File (negative value) -> (00 00 00 00).
0x10    4    section 1 offset (brres index group)
0x14    4    section 2 offset (lightset0)
0x18    4    section 3 offset (ambiantLight0)
0x1C    4    section 4 offset (light0)
0x20    4    section 5 offset (fogset0)
0x24    4    section 6 offset (camera0)
0x28    4    section 7 offset
0x2C    4    String offset to the name of this sub file. relative to SCN0 start (that means if it's 0 it will point to 'VIS0'. one byte before the string is its length, so it would read the byte before 'VIS0' if the pointer was 0 )
0x30    4    Unknown (00 00 00 00 in s20DO.bin)
0x34    4    Unknown (00 01 00 01 in s20DO.bin)
0x38    4    Frame count -1 (00 00 00 00 in s20DO.bin)
0x3C    2    Unknown (00 00 in s20DO.bin)
0x3E    2    Looping, 0=disabled, 1=enabled

v-- SCN0 section 1 brres index group --v
0x00    4    Size of the brres index group
0x04    4    Number of entries -1

v--- for each entry ----v
0x00    2    Binary tree ID
0x02    2    00 00
0x04    2    Binary tree Left index
0x06    2    Binary tree Right index
0x08    4    Name offset minus section 1 offset
0x0C    4    brres index group start offset minus section 1 offset

the first brres index group only references folder names and points to another brres index group for each folder.
so there are as much folders as brres index groups (+ 1, the first one)
these [depth 2] brres index group name "lightSet0" for example, and point to their respective data, which is also pointed by the section offsets in the header

v--- Section 234567 start offset ---v
0x00    4    Section size in bytes
0x04    4    Section start offset (negative value) relative to SCN0 start
0x08    4    Name offset relative to section start

v--- Section 2 (lightset0): ---v
0x00    4    Section size in bytes (00 00 00 4C)
0x04    4    Section start offset (negative value) relative to SCN0 start
0x08    4    Name offset relative to section 2 start offset
0x0C    4    lightset current number Index (count starts at 0)
0x10    4    lightset current number Index (count starts at 0)
0x14    4    Name offset to the AmbiantLight (or zero if unset) relative to section 2 start offset
0x18    2    FF FF
0x1A    1    number of lights set
0x1B    1    00
0x1C    4    offset to light0 (or zero if unset) relative to section 2 + 0x1C
0x20    4    offset to light1 (or zero if unset) relative to section 2 + 0x20
0x24    4    offset to light2 (or zero if unset) relative to section 2 + 0x24
0x28    4    offset to light3 (or zero if unset) relative to section 2 + 0x28
0x2C    4    offset to light4 (or zero if unset) relative to section 2 + 0x2C
0x30    4    offset to light5 (or zero if unset) relative to section 2 + 0x30
0x34    4    offset to light6 (or zero if unset) relative to section 2 + 0x34
0x38    4    offset to light7 (or zero if unset) relative to section 2 + 0x38
0x3C    4    FF FF FF FF
0x40    4    FF FF FF FF
0x44    4    FF FF FF FF
0x48    4    FF FF FF FF
0x4C    4    FF FF FF FF

v--- Section 3 (ambiantLight0): ---v
0x00    4    Section size in bytes (00 00 00 18) + ((Frame Num + 1) * 4)
0x04    4    Section start offset (negative value) relative to SCN0 start
0x08    4    Name offset relative to section 3 start offset
0x0C    4    00 00 00 00
0x10    4    00 00 00 00
0x14    1    80 if constant colour, 00 otherwise
0x15    2    00 00
0x17    1    +1 if color is enabled, +2 if alpha is enabled
0x18    1    Red byte for frame 0
0x19    1    Green byte for frame 0
0x1A    4    Blue byte for frame 0
0x1B    4    Alpha byte for frame 0
there will be 4 bytes more for each frame, with RGBA values between 00 and FF if it is not constant.

the rest of the data of each section is unknown to me
if you wanna edit SCN0 data, use brawlcrate
```
"""
def extract_scn0(data, offset, file_length, root_name, endian, name_offset_in_the_header, extracted_data, sub_file_end):
    sub_file_end += b'\x00' * 3
    section_1_offset = calc_int(data, offset + 0x10, endian)
    section_2_offset = calc_int(data, offset + 0x14, endian)
    section_3_offset = calc_int(data, offset + 0x18, endian)
    if section_3_offset == 0:
        section_3_offset = calc_int(data, offset + 0x1C, endian)
    if section_3_offset == 0:
        section_3_offset = calc_int(data, offset + 0x20, endian)
    if section_3_offset == 0:
        section_3_offset = calc_int(data, offset + 0x24, endian)
    x = section_1_offset + 4
    data_offsets = []
    brres_index_groups_offset = []
    extracted_data += data[offset + len(extracted_data):offset + x + 20]
    entry_number = calc_int(data, offset + x, endian)
    x += 20
    for i in range(entry_number):  # parse each entry of the brres index group
        x += 8
        new_name_offset, sub_file_end = calc_new_name_offset(data, offset, x, endian, section_1_offset, file_length, sub_file_end)
        brres_index_groups_offset.append(calc_int(data, offset + x + 4, endian) + section_1_offset)
        extracted_data += data[offset + x - 8:offset + x] + new_name_offset + data[offset + x + 4:offset + x + 8]
        x += 8
    if len(brres_index_groups_offset) > 0:
        extracted_data += data[offset + x:offset + brres_index_groups_offset[0]]
        brres_index_groups_offset.sort()  # in case it isn't sorted already
    for i in range(entry_number):
        x = brres_index_groups_offset[i]
        sub_entry_number = calc_int(data, offset + x + 4, endian)
        x += 24  # skip header + reference entry of brres index group
        extracted_data += data[offset + x - 24:offset + x]
        for _ in range(sub_entry_number):  # parse each entry of each brres index group
            x += 8
            # print(f"changing offset {x}, group {i}")
            new_name_offset, sub_file_end = calc_new_name_offset(data, offset, x, endian, brres_index_groups_offset[i], file_length, sub_file_end)
            data_offsets.append(calc_int(data, offset + x + 4, endian) + brres_index_groups_offset[i] + 8) # +8 because SCN0
            extracted_data += data[offset + x - 8:offset + x] + new_name_offset + data[offset + x + 4:offset + x + 8]
            x += 8
        if i != entry_number -1:
            extracted_data += data[offset + x:offset + brres_index_groups_offset[i+1]]
    if len(data_offsets) > 0:
        extracted_data += data[offset + x:offset + data_offsets[0]]
        data_offsets.sort()  # in case it isn't sorted already
    else:
        extracted_data += data[offset + x: offset + file_length]
    for i in range(len(data_offsets)):
        x = data_offsets[i] # -8 because SCN0
        new_name_offset, sub_file_end = calc_new_name_offset(data, offset, x, endian, x - 8, file_length, sub_file_end)
        if section_2_offset <= x < section_3_offset:  # lightset references
            ambiant_light_name_offset, sub_file_end = calc_new_name_offset(data, offset, x + 0xC, endian, x - 8, file_length, sub_file_end)
            num_lights = data[offset + x + 0x1A - 8]
            extracted_data += new_name_offset + data[offset + x + 4:offset + x + 0xC] + ambiant_light_name_offset + data[offset + x + 0x10:offset + x + 0x14]
            x += 0x14
            for _ in range(num_lights): # name of each light, relative to section 2 + 0x1C, but -8 because I've offset everything to +8
                light_name_offset, sub_file_end = calc_new_name_offset(data, offset, x, endian, x, file_length, sub_file_end)
                extracted_data += light_name_offset
                x += 4
            new_name_offset = b''
            x -= 4
        if i == entry_number - 1: # skip to section 3
            extracted_data += new_name_offset + data[offset + x + 4:offset + file_length]
        else:
            extracted_data += new_name_offset + data[offset + x + 4:offset + data_offsets[i + 1]]
    extracted_data += sub_file_end + b'\x00'
    return extracted_data

def extract_pat0(data, offset, file_length, root_name, endian, name_offset_in_the_header, extracted_data, sub_file_end):
    sub_file_end += b'\x00' * 3
    section_1_offset = calc_int(data, offset + 0x10, endian)
    section_2_offset = calc_int(data, offset + 0x14, endian)
    # section_3_offset = calc_int(data, offset + 0x18, endian)
    x = section_1_offset + 0x18
    N_BASE = calc_short(data, offset + x - 10, endian)
    N_STR = calc_short(data, offset + x - 8, endian)
    data_offsets = []
    extracted_data += data[offset + len(extracted_data):offset + x]
    for i in range(N_BASE):
        x += 8
        new_name_offset, sub_file_end = calc_new_name_offset(data, offset, x, endian, section_1_offset, file_length, sub_file_end)
        data_offsets.append(calc_int(data, offset + x + 4, endian) + section_1_offset)
        extracted_data += data[offset + x - 8:offset + x] + new_name_offset + data[offset + x + 4:offset + x + 8]
        x += 8
    if len(data_offsets) > 0:
        extracted_data += data[offset + x:offset + data_offsets[0]]
        data_offsets.sort()  # in case it isn't sorted already
    for i in range(N_BASE):
        x = data_offsets[i]
        new_name_offset, sub_file_end = calc_new_name_offset(data, offset, x, endian, x, file_length, sub_file_end)
        if i == N_BASE - 1: # skip to section 2
            extracted_data += new_name_offset + data[offset + data_offsets[i] + 4:offset + section_2_offset]
        else:
            extracted_data += new_name_offset + data[offset + data_offsets[i] + 4:offset + data_offsets[i + 1]]
    x = section_2_offset
    for i in range(N_STR):
        new_name_offset, sub_file_end = calc_new_name_offset(data, offset, x, endian, section_2_offset, file_length, sub_file_end)
        extracted_data += new_name_offset
        x += 4
    extracted_data += data[offset + x: offset + file_length] + sub_file_end + b'\x00'
    return extracted_data
"""
VIS0 (File Format) Made by me
```Offset Size  Description
0x00    4    The magic "VIS0" to identify the sub file. 
0x04    4    Length of the sub file. (internal name/ other string at the end not counted)
0x08    4    Sub file version number. ( 00 00 00 04 else crash)
0x0C    4    Offset to outer BRRES File (negative value) -> (00 00 00 00).
0x10    8    section offsets. (offset to when data is -> after each VIS0 subheader, usually 00 00 00 28 00 00 00 00)
0x18    4    String offset to the name of this sub file. relative to VIS0 start (that means if it's 0 it will point to 'VIS0'. one byte before the string is its length, so it would read the byte before 'VIS0' if the pointer was 0 )

v-- VIS0 SubHeader --v
0x1C    4    00 00 00 00.
0x20    2    Frame Count
0x22    2    Number of bones (entries / Nodes / Animation data count)
0x24    4    Looping 0x00=disabled 0x01=enabled.

v-- VIS0 brres index group --v
0x28    4    Size of the brres index group
0x2C    4    Number of entries -1

v--- for each entry ----v
0x00    2    Binary tree ID
0x02    2    00 00
0x04    2    Binary tree Left index
0x06    2    Binary tree Right index
0x08    4    Name offset minus section 1 offset (-0x28)
0x0C    4    data start offset minus section 1 offset (-0x28)

v--- data start ---v
0x00    4    Name offset minus data start offset
0x04    4    +2 if constant, and +1 if bone is visible
if not constant:
0x08    X    one bit per frame, 1 = visible, 0 = not visible
0x0Y    4    00 00 00 00

X = ceiling(number of frames / 8). fill with last byte with ones to make a full byte
Y = X + 8
```
"""
def extract_clr0_srt0_vis0_chr0(data, offset, file_length, root_name, endian, name_offset_in_the_header, extracted_data, sub_file_end):
    sub_file_end += b'\x00' * 3
    section_1_offset = calc_int(data, offset + 0x10, endian)
    x = section_1_offset + 4
    data_offsets = []
    extracted_data += data[offset + len(extracted_data):offset + x + 20]
    entry_number = calc_int(data, offset + x, endian)
    x += 20
    for i in range(entry_number):  # parse each entry of the brres index group
        x += 8
        new_name_offset, sub_file_end = calc_new_name_offset(data, offset, x, endian, section_1_offset, file_length, sub_file_end)
        data_offsets.append(calc_int(data, offset + x + 4, endian) + section_1_offset)
        extracted_data += data[offset + x - 8:offset + x] + new_name_offset + data[offset + x + 4:offset + x + 8]
        x += 8
    if len(data_offsets) > 0:
        extracted_data += data[offset + x:offset + data_offsets[0]]
        data_offsets.sort()  # in case it isn't sorted already
    for i in range(entry_number):
        x = data_offsets[i]
        new_name_offset, sub_file_end = calc_new_name_offset(data, offset, x, endian, x, file_length, sub_file_end)
        if i == entry_number - 1: # skip to section 2
            extracted_data += new_name_offset + data[offset + data_offsets[i] + 4:offset + file_length]
        else:
            extracted_data += new_name_offset + data[offset + data_offsets[i] + 4:offset + data_offsets[i + 1]]
    extracted_data += sub_file_end + b'\x00'
    return extracted_data
        
def calc_new_name_offset(data, offset, x, endian, section_offset, file_length, sub_file_end):
    name_offset = calc_int(data, offset + x, endian)
    # print(offset + x, x, name_offset)
    name_len = data[offset + section_offset + name_offset - 1]
    name = data[offset + section_offset + name_offset: offset + section_offset + name_offset + name_len]
    new_name_offset = string_pool_table.get(name)
    if new_name_offset is None:
        w = hex(file_length + len(sub_file_end) + 1 - section_offset)[2:].zfill(8)
        new_name_offset = b''
        for octet in range(0, 8, 2):  # transform for example "3f800000" to b'\x3f\x80\x00\x00'
            new_name_offset += bytes(chr(int(w[octet:(octet + 2)], 16)), 'latin-1')
        if endian == b'\xff\xfe':
            new_name_offset = new_name_offset[::-1] # reverse bytes order
        string_pool_table[name] = (new_name_offset, w, section_offset)
        sub_file_end += bytes(chr(name_len), 'latin-1') + name + b'\x00' * 3 + b'\x00' * (4 - (name_len % 4))
    else:
        # print(new_name_offset)
        w = hex(int(new_name_offset[1], 16) + new_name_offset[2] - section_offset)[2:].zfill(8)
        new_name_offset = b''
        for octet in range(0, 8, 2):  # transform for example "3f800000" to b'\x3f\x80\x00\x00'
            new_name_offset += bytes(chr(int(w[octet:(octet + 2)], 16)), 'latin-1')
        if endian == b'\xff\xfe':
            new_name_offset = new_name_offset[::-1] # reverse bytes order
    return new_name_offset, sub_file_end
    
def change_offsets(data, offset, file_length, root_name, endian, magic, outer_brres_offset_in_the_header, name_offset_in_the_header, version):
    extracted_data = data[offset: offset + outer_brres_offset_in_the_header] + b'\x00\x00\x00\x00' # change offset to brres file (no brres since it's an extracted file)
    name_bytes = bytes(root_name, 'latin-1') # don't ask me why ANSI is named latin-1 in python
    name_len = bytes(chr(len(name_bytes)), 'latin-1')
    sub_file_end = b'\x00' * 3
    string_pool_table.clear()
    w = hex(file_length + len(sub_file_end) + 1)[2:].zfill(8)
    new_name_offset = b''
    for octet in range(0, 8, 2):  # transform for example "3f800000" to b'\x3f\x80\x00\x00'
        new_name_offset += bytes(chr(int(w[octet:(octet + 2)], 16)), 'latin-1')
    if endian == b'\xff\xfe':
        new_name_offset = new_name_offset[::-1] # reverse bytes order
    extracted_data += data[offset + outer_brres_offset_in_the_header + 4:offset + name_offset_in_the_header] + new_name_offset # change offset to filename, even if the file itself is named like what's written
    
    string_pool_table[name_bytes] = (new_name_offset, w, 0)
    sub_file_end += name_len + name_bytes + b'\x00' * (12 - (name_len[0] % 12))
    # print(b'new name offset', new_name_offset, root_name, sub_file_end, file_length)
    if magic == b'PAT0':
        return extract_pat0(data, offset, file_length, root_name, endian, name_offset_in_the_header, extracted_data, sub_file_end)
    if magic in [b'CLR0', b'SRT0', b'VIS0', b'CHR0']:
        return extract_clr0_srt0_vis0_chr0(data, offset, file_length, root_name, endian, name_offset_in_the_header, extracted_data, sub_file_end)
    if magic == b'SHP0':
        return extract_shp0(data, offset, file_length, root_name, endian, name_offset_in_the_header, extracted_data, sub_file_end)
    if magic == b'SCN0':
        return extract_scn0(data, offset, file_length, root_name, endian, name_offset_in_the_header, extracted_data, sub_file_end)
    if magic == b'MDL0':
        return extract_mdl0(data, offset, file_length, root_name, endian, name_offset_in_the_header, version, extracted_data, sub_file_end)
    extracted_data += data[offset + name_offset_in_the_header + 4:offset + file_length]
    extracted_data += sub_file_end
    return extracted_data

magic_version_name_offset = {
    (b'MDL0', 11): 0x48, (b'MDL0', 10): 0x44, (b'MDL0', 9): 0x3C, (b'MDL0', 8): 0x3C,
    (b'TEX0', 1): 0x14, (b'TEX0', 2): 0x18, (b'TEX0', 3): 0x14,
    (b'PLT0', 1): 0x14, (b'PLT0', 3): 0x14,
    (b'SRT0', 4): 0x14, (b'SRT0', 5): 0x18,
    (b'CHR0', 4): 0x14, (b'CHR0', 5): 0x18,
    (b'PAT0', 3): 0x24, (b'PAT0', 4): 0x28,
    (b'CLR0', 3): 0x14, (b'CLR0', 4): 0x18,
    (b'SHP0', 3): 0x18, (b'SHP0', 4): 0x1C,
    (b'SCN0', 4): 0x28, (b'SCN0', 5): 0x2C,
    (b'VIS0', 3): 0x14, (b'VIS0', 4): 0x18
}
def extract_sub_file(data, offset, root_name, root_absolute_filepath, endian):
    file_length = calc_int(data, offset + 4, endian) # u32
    extracted_data = b''
    # now we need to change the file content and add data at the end, else brawlcrate crashes
    magic = data[offset:offset + 4]
    version = calc_int(data, offset + 8, endian)
    name_offset = magic_version_name_offset.get((magic, version))
    ASSERT(name_offset is not None)
    extracted_data = change_offsets(data, offset, file_length, root_name, endian, magic, 0xC, name_offset, version)
    with open(root_absolute_filepath + '.' + magic.decode('latin-1').lower(), 'wb') as sub:
        sub.write(extracted_data)

def extract_msm_files(data):  # these files have no filesize at offset 4 or 8
    every_offset_of_a_new_thing.sort()
    for i in range(len(msm_files_offset)):
        offset = msm_files_offset[i]
        file = msm_files_absolute_filepath[i]
        next_offset = every_offset_of_a_new_thing[every_offset_of_a_new_thing.index(offset) + 1]
        with open(file, 'wb') as administrator:
            administrator.write(data[offset:next_offset])

def parse_brres_index_group(data, offset, root_name, root_folder, endian):
    print(offset, root_name, root_folder, data[offset: offset + 4])
    if data[offset: offset + 4] in [b'bres']: 
        # root_folder is a file, and not a folder, so I will extract it and quit the function
        extract_brres_inside_brres(data, offset, root_name, root_folder)
        extracted_files.append(root_folder)
        return # end of tree
    if data[offset: offset + 4] in [b'MDL0', b'TEX0', b'SRT0', b'CHR0', b'PAT0', b'CLR0', b'SHP0', b'SCN0', b'PLT0', b'VIS0']:
        # root_folder is a file, and not a folder, so I will extract it and quit the function
        extract_sub_file(data, offset, root_name, root_folder, endian)
        extracted_files.append(root_folder)
        return # end of tree
    if data[offset: offset + 4] in [b'@ARN', b'@FOG', b'@LGT', b'MEI0']: # MSM Special files
        # store file information and extract at the end
        msm_files_offset.append(offset)
        msm_files_absolute_filepath.append(root_folder)
        extracted_files.append(root_folder)
        return # end of tree
    if data[offset: offset + 4] in [b'XBIN']:
        extract_xbin(data, offset, root_name, root_folder, endian)
        extracted_files.append(root_folder)
        return
    ASSERT(data[offset + 8: offset + 12] == b'\xff\xff\x00\x00') # add an if statement above this line with the 4 bytes to add then write your extract function
    if not os.path.exists(root_folder):
        os.makedirs(root_folder)
        
    # brres_index_group_length = calc_int(data, offset, endian) # u32
    number_of_entries = calc_int(data, offset + 4, endian)  # u32
    # print(brres_index_group_length, number_of_entries, hex(offset), data[offset: offset + 4])
    # parse Brres Index Group 1
    x = 8 + 16 # skip reference point since we're extracting
    # info_list = [create_brres_info(id=0, left_idx=0, right_idx=0, name=root_name, nlen=0)]
    # we're extracting!!! no creating the binary tree
    while number_of_entries > 0:
        x += 8 # skip binary tree info
        entry_name_offset = calc_int(data, offset + x, endian) + offset # u32
        entry_name_offset_len = data[entry_name_offset - 1] # u8
        entry_name = data[entry_name_offset:entry_name_offset + entry_name_offset_len].decode('latin-1') # converts to str using latin-1 encoding
        x += 4
        entry_start_offset = calc_int(data, offset + x, endian) + offset # u32
        every_offset_of_a_new_thing.append(entry_name_offset - 1)
        every_offset_of_a_new_thing.append(entry_start_offset)
        parse_brres_index_group(data, entry_start_offset, entry_name, os.path.join(root_folder, entry_name), endian)
        x += 4
        number_of_entries -= 1
        
##################################################################################
#  REWRITE OF WSZST BRRES CREATOR IN PYTHON BY HAND
#  ASSUMPTIONS : all brres are little endian. all ASSERT contents are true
#  SOURCE : me
#  USAGE : create_brres('cmn_test_DECOMP_new')
##################################################################################

def scan_directory():
    del repack_list[:]
    del extract_list[:]
    for tkstuff in a.winfo_children():
        if tkstuff not in [text_label, cwd_label, entry_dir, refreshbu, open_explorerbu]:
            tkstuff.destroy()

    def repack(cmn_dir):  # repack cmn_dir
        if not os.path.exists(cmn_dir):
            cmn_dir = print(f"folder doesn't exist => {cmn_dir}")
        out_name = cmn_dir + '.brres'
        name = cmn_dir.rsplit('_', 1)[1].lower()
        if name.startswith('extracted') or name.startswith('decomp'):
            out_name = cmn_dir.rsplit('_', 1)[0]
        if os.path.exists(out_name + '.brres'):
            number = 1
            while os.path.exists(f"{out_name}_{number}.brres"):
                number += 1
            out_name = f"{out_name}_{number}.brres"
        else:
            out_name = f"{out_name}.brres"
        os.system(f'wszst c "{cmn_dir}" --brres --no-compress -d "{out_name}"')
        manual_entry.delete(0, 'end')
        return language[arc + 1]

    def extract(brres):
        data = b''
        with open(brres, "rb") as bina:
            data = bina.read(8)
        if data[:8] != b'bres\xfe\xff\x00\x00': # if it's not a brres
            os.system(f'{n} "{brres}" -x') # convert it to brres
            brres = os.path.splitext(brres)[0] + '_DECOMP.bin'
        print(brres)
        extract_brres(brres)
        """except InterruptedError:
            raise InterruptedError
            print(language[cmn + 11])  # message that it's not a brres
        except FileNotFoundError:
            raise InterruptedError
            print(language[cmn + 11])  # message that it's not a brres"""
        return language[arc + 1]
    
    def explorer_repack():
        repack_dir = askdirectory(initialdir=cwd, title="Select a directory to repack")
        print(repack(repack_dir))

    def explorer_extract():
        file = askopenfilename(initialdir=cwd)
        try:
            extract_brres(file)
        except InterruptedError:
            print(language[miku + 11])  # message that it's not a brres
        except FileNotFoundError:
            print(language[miku + 11])  # message that it's not a brres
        print(language[arc + 1])

    def extract_file(file, number):
        label_text = extract(file)
        extract_list[number].destroy()
        patched = Label(a, text=label_text, bg='#dfffaa', width=30)
        patched.grid(row=burow_extract[number], column=bucolumn[number])

    def repack_folder(brres, num):
        text = repack(brres)
        repack_list[num].destroy()
        patched = Label(a, text=text, bg='#dfffaa', width=30)
        patched.grid(row=burow_extract[num], column=bucolumn[num])

    patched = Label(a, text=language[arc + 1], bg='#dfffaa', width=30)
    patched.grid(row=5, column=0)
    file_extract_label = Label(a, text=language[miku + 5], font=300, bg='#dfffaa', height=2, width=45)
    file_extract_label.grid(row=2, columnspan=20)

    explorer_extractbu = Button(a, text=language[msm + 19], activebackground='#96c7ff', bg='#c4e0ff', command=explorer_extract, width=87)
    explorer_extractbu.grid(row=5, column=0, columnspan=3)

    p = 0
    for file_to_extract in os.listdir('./'):
        try:
            if os.path.isfile(file_to_extract):
                size = os.path.getsize(file_to_extract)
                if size < 5 or p >= len(bucolumn):
                    continue
                with open(file_to_extract, 'rb') as check_xfile:
                    header = check_xfile.read(4)
                if header[:1] in [b'@', b'\x10', b'\x11', b'\x81', b'\x82', b'$', b'(', b'0', b'P', b'b'] and header != b'PK\x03\x04':  # lh @, old lz \x10, lz77 \x11, diff8 \x81, diff16 \x82, huff4 $, huff8 (, runlength 0, lrc P
                    run_extract_file = partial(extract_file, file_to_extract, p)
                    temp = Button(a, text=file_to_extract, command=run_extract_file, activebackground='#a9ff99', width=30)
                    temp.grid(row=burow_extract[p], column=bucolumn[p])
                    extract_list.append(temp)
                    # print(file_to_extract, p)
                    p += 1

        except PermissionError as error:
            print(error)
            continue

    cmn_repack_label = Label(a, text=language[miku + 6], font=300, bg='#dfffaa', height=2)
    cmn_repack_label.grid(row=18, columnspan=20)

    manual_explorerbu = Button(a, text=language[msm + 19], command=explorer_repack, activebackground='#ffc773', bg='#ffe4bd', width=87)
    manual_explorerbu.grid(row=21, column=0, columnspan=3)

    manual_label = Label(a, text=language[miku + 7], bg='#dfffaa', width=30)
    manual_label.grid(row=20, column=0)

    manual_entry = Entry(a, width=30)
    manual_entry.grid(row=20, column=1)

    manual_button = Button(a, text=language[miku + 8], activebackground='#a9ff91', bg='#c9ffba', width=30)
    manual_repack = partial(repack, manual_entry.get())
    manual_button.config(command=manual_repack)
    manual_button.grid(row=20, column=2)

    i = 0
    for dir_to_repack in os.listdir('./'):
        try:
            if os.path.isdir(dir_to_repack):
                run_repack_file = partial(repack_folder, dir_to_repack, i)
                temp2 = Button(a, text=dir_to_repack, command=run_repack_file, activebackground='#a9ff91', width=30)
                temp2.grid(row=burow_repack[i], column=bucolumn[i])
                repack_list.append(temp2)
                i += 1

        except PermissionError as error:
            print(error)
            continue
    if i > 50 or p > 50:  # creates a big exit button and make the window fullscreen as it was too tiny to display all buttons
        exitbu2 = Button(a, text=language[msm + 40], command=a.quit, activebackground='#d9ff8c', bg='#d9ff8c', fg='#ff2222', width=58, height=3, font=100)
        exitbu2.grid(row=0, column=4, rowspan=2, columnspan=3)
        a.attributes('-fullscreen', True)


def change_directory():  # enter button to change directory (take the entry content)
    entry_cwd = entry_dir.get()
    if entry_cwd == '':
        entry_cwd = os.getcwd()
    else:
        cwd_label.configure(text=entry_cwd)
    entry_dir.delete(0, 'end')
    os.chdir(entry_cwd)
    scan_directory()


def open_explorer():  # change directory with C:\Windows\explorer.exe GUI
    new_cwd = askdirectory(initialdir=os.getcwd)
    os.chdir(new_cwd)
    cwd_label.configure(text=new_cwd)
    scan_directory()


cwd = os.getcwd()
text_label = Label(a, text=language[msm + 18], bg='#dfffaa', width=30)
text_label.grid(row=0, column=0)
cwd_label = Label(a, text=cwd, bg='#dfffaa', width=60, anchor='w')
cwd_label.grid(row=0, column=1, columnspan=2)
entry_dir = Entry(a, width=30)
entry_dir.grid(row=1, column=1)
refreshbu = Button(a, text=language[msm + 40], command=change_directory, activebackground='#ff9999', width=30)
refreshbu.grid(row=1, column=2)
open_explorerbu = Button(a, text=language[msm + 19], command=open_explorer, activebackground='#96c7ff', width=15)
open_explorerbu.grid(row=1, column=0)
scan_directory()
a.mainloop()
