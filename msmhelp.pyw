from tkinter import Tk, Canvas, PhotoImage, Button, Label, font
from textwrap import wrap
from functools import partial
from PIL import Image

with open('#language.txt', 'r') as txt:
    language = txt.read()
    language = [''] + language.splitlines()

a = Tk()
a.title(language[198])
a.attributes('-fullscreen', True)
a.config(bg="#ff9696")
a.iconbitmap('C:\\Yosh\\msm_stuff\\msmhelp.ico')
w = a.winfo_screenwidth()
h = a.winfo_screenheight()

txt = Label(a, text=language[200], font=300, bg="#ff9696")
txt.place(x=33 * w / 84, y=h / 20)
title = Label(a, text=language[199], font=300, bg="#ff9696")
title.place(x=17 * w / 42, y=h / 50)
bye = Button(a, text=language[38], command=a.quit, bg="#9fff7f", font=2, activebackground='#8fff7f', width=24, height=2)
bye.place(x=63 * w / 80, y=h / 10)
# a.wm_attributes('-transparentcolor', a['bg'])

m = font.Font(family='MARIO Font v3 Solid', size=25)  # , weight='bold')


# print(font.families())

def menu(garbage):  # goes back to the menu with 16 little pictures
    for z in a.winfo_children():
        if z in static:
            continue
        z.destroy()


def display(picture, garbage_sent_by_bind):  # displays the big png
    c = Canvas(a, width=w, height=h, bd=-2, bg="#ff9696")
    c.bind("<Button-1>", menu)
    c.create_image(w / 2, h / 2, image=image_list[picture])
    c.place(x=0, y=0)
    left = c.create_text((w / 8, h / 9), text=text, font=m, fill=minicolor[i])
    right


def littlepic(num):  # adds text to the 16 littlepics
    # switch case
    lilpictext = Label(a, text=language[201 + num], font=m, bg="#ff9696")
    lilpictext.place(x=(num % 4 * 10 + 2) * w / 40, y=((num // 4 + 1) * 10 + 3) * h / 50)


name = ["h", "h2", "h3", "h4", "h5", "h6", "h7", "h8", "h9", "ha", "hb", "hc", "hd", "he", "hf", "hm", "m", "m2", "m3",
        "m4", "m5", "m6", "m7", "how-to-run-msm", "m9", "ma", "mb", "mc", "md", "me", "mf", "mm"]
miniatures = name[:16]  # from h to hm
large = name[16:]  # from m to end

with open("C:\\Yosh\\h.png", 'rb') as minipic:
    minipic.seek(16)
    byte = minipic.read(4)
    # pic_width = (byte[0] * 16777216) + (byte[1] * 65536) + (byte[2] * 256) + byte[3] - 64  # 4 bytes integer
    pic_width = (byte[0] << 24) + (byte[1] << 16) + (byte[2] << 8) + byte[3] - 64  # 4 bytes integer
    byte = minipic.read(4)
    pic_height = (byte[0] << 24) + (byte[1] << 16) + (byte[2] << 8) + byte[3] - 64  # 4 bytes integer

if (pic_width != w // 5) and (pic_height != h // 5):
    for n in range(len(miniatures)):
        picc = Image.open('C:\\Yosh\\' + miniatures[n] + '.png')
        new_pic = picc.resize((w // 5, h // 5))
        picc.close()
        new_pic.save('C:\\Yosh\\' + miniatures[n] + '.png')

with open("C:\\Yosh\\m.png", 'rb') as minipic:
    minipic.seek(16)
    byte = minipic.read(4)
    pic_width = (byte[0] << 24) + (byte[1] << 16) + (byte[2] << 8) + byte[3] - 64  # 4 bytes integer
    byte = minipic.read(4)
    pic_height = (byte[0] << 24) + (byte[1] << 16) + (byte[2] << 8) + byte[3] - 64  # 4 bytes integer

if (pic_width != w) and (pic_height != h):
    for p in range(16, len(miniatures)):
        picc = Image.open('C:\\Yosh\\' + miniatures[p] + '.png')
        new_pic = picc.resize((w, h))
        picc.close()
        new_pic.save('C:\\Yosh\\' + miniatures[p] + '.png')

image_list = []
for j in range(0, 32):
    pic = PhotoImage(file=f"C:\\Yosh\\{name[j]}.png")
    image_list.append(pic)
static = [title, txt, bye]
ListeNulle = [3, 7, 11]
eks = [0, w / 4, 2 * w / 4, 3 * w / 4]
whi = [h / 5, 2 * h / 5, 3 * h / 5, 4 * h / 5]
minicolor = ['#4fd5ff', '#0061ff', '#0000ff', '#7f00ff', '#006eff', '#952bff', '#ff00a1', '#ff5d00', '#5500a5',
             '#ff77df', '#ff8282', '#ffbf00', '#35ff7f', '#99ff00', '#c700ff', '#b70f00']

for i in range(0, 16):  # displays the 16 little pictures + bind left click to the full-screen ones
    print(wrap(language[201 + i], 15))
    list_text = wrap(language[201 + i], 12)
    text = ''
    for string in list_text:
        if string == list_text[-1]:
            text += (13 - 2 * len(string)) * ' ' + string + (12 - 2 * len(string)) * ' '
        else:
            text += (13 - 2 * len(string)) * ' ' + string + (12 - 2 * len(string)) * ' ' + '\n'

    f = Canvas(a, width=w / 4, height=h / 5, bd=-2, bg="#ff9696")
    func = partial(display, i + 16)
    f.bind("<Button-1>", func)
    f.create_image(w / 8, h / 10, image=image_list[i])
    f.place(x=eks[i % 4], y=whi[i // 4])  # + '\n' + language[201 + i][10:20] + '\n' + language[201 + i][20:]
    info = f.create_text((w / 8, h / 9), text=text, font=m, fill=minicolor[i])
    static.append(f)
    static.append(info)
a.mainloop()
