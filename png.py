import os

with open('#language.txt', 'r') as txt:
    language = txt.read()
    language = [''] + language.splitlines()

tex0 = [0]
name, position, bres_list = [], [], []
add_png = keep = filetype = file = header = 0
colourenc = ['I4', 'I8', 'IA4', 'IA8', 'RGB565', 'RGB5A3', 'RGBA8', 0, 'CI4', 'CI8', 'CI14x2', 0, 0, 0, 'CMPR']
extensions = ['.bin', '.mdl', '.cmp']
bresarc = [b'U\xaa8-', b'bres']


def message():
    print(f"\n\n{language[122]},\n{language[123]}\n{language[124]}\n{language[125]}\n\n{language[126]}\n")


for file in os.listdir('./'):
    if not os.path.isfile(file) or os.path.getsize(file) < 4:
        continue
    try:
        with open(file, 'rb') as stuff:
            header = stuff.read(4)

    except PermissionError as error:
        # print(error)
        continue
    if header in bresarc:
        break
if header not in bresarc:  # the for can ends after browsing a complete directory without finding any brres or arc file.
    input(f'{language[127]}.\n{language[128]}.')
    exit()
compress = True
mode = input(f"{language[129]} : {file}\n{language[130]}\n{language[131]}\n{language[132]}\n{language[133]}\n{language[134]}\n{language[135]}\n{language[136]}\n{language[137]} : ")
if mode in ['2', '3', '5', '6']:  # keep encoded textures
    keep = True
if mode in ['4', '5', '6']:  # don't compress
    compress = False
while mode in ["1", "3", "6"]:  # that's not the file you want, so type manually the filename
    file = input(f'{language[138]} : ')
    if not os.path.exists(file):
        continue
    with open(file, 'rb') as check:
        if check.read(4) not in bresarc:
            print(f'{language[139]}.')
        else:
            mode = '0'
with open(file, 'r+b') as arc:  # though arc could have been named brres as it's the same process for both files
    size = cursor = os.path.getsize(file)
    if '_' in file:
        short = file.rsplit('_', 1)[0]
    elif '.' in file:
        short = os.path.splitext(file)[0]
    else:
        short = file  # short has high probabilities to be the name used in the filesystem of the game
    print(language[140])  # in case it's long
    for z in range(0, size-17, 16):
        arc.seek(z)
        header = arc.read(4)
        if header == b'TEX0':
            tex0.append(z)  # list of all the textures offsets
        if header == b'bres':
            bres_list.append(z)   # list of all the brres offsets
    bres_list.append(0)
    bres_list.reverse()   # make 0 the last element of the last if it's empty and the first brres offset if not empty
    cmd_list = []
    if compress:
        for indice in range(3):
            if f"{short}{extensions[indice]}" == file:  # don't delete the file this script is editing
                short += extensions[indice]
                break
            else:  # os.remove crashes the script if the file doesn't exists while del doesn't
                os.system(f'del "{short}{extensions[indice]}"')  # overwrite files if compressing
    while add_png != '1':  # while user enters a wrong name
        picture = input(f'{language[151]} : ')  # remember quote is a forbidden character in windows
        picture = picture.strip('"')     # if you drag and drop it adds quotes and create a name that doesn't exists
        if not os.path.exists(picture):  # yes, python considers quotes as part of a file name
            print(f'{picture} {language[142]}.\n{language[143]}.')
            continue
        with open(f'{picture}', 'r+b') as png:
            header = png.read(4)
        if header != b'\x89PNG':
            print(f"{language[144]}.")
            continue
        while header != 1:  # while user enters a wrong number
            pos = input(f'{language[145]} : ')
            if pos in ['0', '-0', '']:
                print(language[146])
            elif pos.lstrip('-').isdigit():
                if int(pos.lstrip('-')) > len(tex0):  # if position entered is greater than the max number of tex0 found
                    message()
                    continue
                header = 1  # position entered is valid
                pos = int(pos)
            else:
                message()
        name.append(picture)
        position.append(pos)
        print()  # creates a blank line in cmd, else it looks too compressed
        offset = tex0[pos] + 39
        arc.seek(offset)
        nmipmap = arc.read(1)[0] - 1  # the 39th byte of a tex0 file is the number of mipmaps +1
        arc.seek(offset - 4)          # a mipmap is a duplicate of a texture downscaled by 2, used when far away
        colour = arc.read(1)[0]       # to use less RAM, and also looks better visually when far away (not distorted)
        cmd_list.append(f'wimgt encode "{picture}" -x {colourenc[colour]} --n-mm {nmipmap} -o')
        print(language[147])
        add_png = input(f'{language[148]}\n')
        if add_png == '1':
            for command in cmd_list:
                os.system(command)
    # ^ while add_png != 1 ^
    # wimgt will convert all png to encoded texture files called tex0 because their header is tex0

    for i in range(len(name)):  # replace textures in the file by the png given
        tex_name = name[i].rstrip('.png')
        pos = position[i]
        with open(tex_name, 'rb') as texture:
            if texture.read(4) != b'TEX0':
                continue
            byte = texture.read(4)
            data_size = (byte[0] * 16777216) + (byte[1] * 65536) + (byte[2] * 256) + byte[3] - 64  # 4 bytes integer
            texture.seek(64)  # the header of a tex0 is 64 bytes long
            tex = texture.read(data_size)  # custom texture data

            texture.seek(28)  # the 28th byte of a tex0 file is the offset of dimensions
            dim_tex = texture.read(4)  # 2 bytes integer for width then height

            arc_tex0_data_pos = tex0[pos] + 64
            arc.seek(arc_tex0_data_pos - 36)
            arc_tex_dim = arc.read(4)
        if dim_tex != arc_tex_dim:  # don't replace vanilla texture if the custom one doesn't have the same size
            input(f'{picture} is {dim_tex[0] * 256 + dim_tex[1]}x{dim_tex[2] * 256 + dim_tex[3]} while {file} texture is {arc_tex_dim[0] * 256 + arc_tex_dim[1]}x{arc_tex_dim[2] * 256 + arc_tex_dim[3]}\nDid you opened external folder ???\n\nNote also that all textures are counted for all brres in an arc file.\n\nPress enter to replace all other textures.\n')
            continue
        next_tex0_pos = arc_tex0_data_pos + data_size
        if pos == -1 or pos == len(tex0) - 1:  # if the texture is the last one, it doesn't have a next
            next_tex0_pos = arc_tex0_data_pos - 64
        arc.seek(next_tex0_pos)
        header = arc.read(4)
        brres = bres_list[-1]  # equals zero if the list is empty or the first brres offset if not empty
        if (brres == 0 or next_tex0_pos < brres) and header != b'TEX0':
            print(language[149])
            print(f'dev info : current file = {file} ; picture name = {picture} ; tex0 data size = {data_size}')
            print(f'offset of next tex0 = {next_tex0_pos} ; next brres offset = {brres}')
            input(language[150])
            continue
        arc.seek(arc_tex0_data_pos)
        arc.write(tex)  # custom texture data

if not keep:
    for line in cmd_list:
        if line.startswith("del "):
            continue
        texname = line.split('wimgt encode ')[1]
        texname = texname.split('.png')[0]
        os.system(f'del "{texname}"')
if compress:
    with open(file, 'rb') as check_mdl:
        check_mdl.seek(0)
        if check_mdl.read(1) == b'\x00':
            filetype = 2  # .cmp
        while cursor > size - 2222:
            cursor -= 1
            check_mdl.seek(cursor)
            if check_mdl.read(6) == b'body_h':
                filetype = 1  # .mdl
                break
    os.system(f'C:\\Yosh\\n.exe "{file}" -lh -o "{short}{extensions[filetype]}"')
