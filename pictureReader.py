import copy
import os
import tkinter as tk
import tkinter.colorchooser
import tkinter.filedialog

import PIL.Image as Image
import numpy as np
from PIL import ImageTk

# create the main window
window = tk.Tk()
window.title("Picture Editor")
window.geometry('500x100')

# image display area
canvas = tk.Canvas(window, height=500, width=980)
canvas.place(x=0, y=100)

# selected color on image display
display_old_color = tk.Label(window, bg='white', width=1, height=1)
display_old_color.place(x=300, y=5)

# target color display
display_new_color = tk.Label(window, bg='white', width=1, height=1)
display_new_color.place(x=300, y=35)

# render range label
render_text = tk.Label(window, text='Render range:')
render_text.place(x=350, y=0)

# render range input
render_range = tk.Entry(window, show=None)
render_range.place(x=350, y=30, width=100)

edit_image_array = None
display_image = None
selected_color = None
selected_new_color = None
render_range_number = None
operations = []


def get_picture():
    file_name = tk.filedialog.askopenfilename(title='Picture', filetypes=[("PNG", ".png"), ("JPG", ".jpg")])
    if file_name is None or file_name == '':
        return
    global edit_image_array, display_image
    edit_image = Image.open(file_name)
    edit_image_array = np.array(edit_image)
    # height and width
    height = len(edit_image_array)
    width = len(edit_image_array[0])
    window.update()
    if width < window.winfo_width():
        width = window.winfo_width()
    window.geometry(str(width + 10) + 'x' + str(height + 130))
    canvas.config(height=height, width=width)

    display_image = ImageTk.PhotoImage(edit_image)
    canvas.create_image(0, 0, anchor='nw', image=display_image)


load_picture_button = tk.Button(window, text="Select Picture", width=11, height=1, command=get_picture)
load_picture_button.place(x=0, y=1)


def save_picture():
    if edit_image_array is not None:
        save_name = tk.filedialog.asksaveasfilename(title='Save')
        if save_name is None or save_name == '':
            return
        image_stream = Image.fromarray(edit_image_array)
        image_stream.save(save_name + '.png')


save_picture_button = tk.Button(window, text="Save Picture", width=10, height=1, command=save_picture)
save_picture_button.place(x=100, y=1)


def click(event):
    print("click width position " + str(event.x) + ", height position " + str(event.y))
    canvas.unbind("<Button-1>")
    if edit_image_array is not None:
        global selected_color
        selected_color = copy.deepcopy(edit_image_array[event.y][event.x])
        print(selected_color)

        real_color = '#'
        for i in selected_color:
            real_color += str(hex(i))[-2:].replace('x', '0').upper()
        display_old_color.configure(bg=real_color)


def activate_selection():
    canvas.bind("<Button-1>", click)


select_color_button = tk.Button(window, text="Select Color", width=10, height=1, command=activate_selection)
select_color_button.place(x=200, y=1)


def choose_color():
    color = tkinter.colorchooser.askcolor()
    if color is None or color == (None, None):
        return
    display_new_color.configure(bg=color[1])
    global selected_new_color
    color_array = color[0]
    selected_new_color = [0, 0, 0]
    selected_new_color[0] = color_array[0]
    selected_new_color[1] = color_array[1]
    selected_new_color[2] = color_array[2]


change_to_color_button = tk.Button(window, text="Change To", width=10, height=1, command=choose_color)
change_to_color_button.place(x=200, y=30)


def is_same(one, two):
    dis = 0
    for i in range(0, 3):
        num = abs(int(one[i]) - int(two[i]))
        dis += num * num

    if dis < render_range_number:
        return True
    return False


def render_image():
    image_stream = Image.fromarray(edit_image_array)
    image_stream.save('temp$1.png')

    global display_image
    edit_image = Image.open('temp$1.png')
    display_image = ImageTk.PhotoImage(edit_image)
    canvas.create_image(0, 0, anchor='nw', image=display_image)


def change_all_entry():
    global render_range_number
    render_range_number = render_range.get()
    if render_range_number is None:
        return

    # verify it is a number
    try:
        render_range_number = int(render_range.get())
    except ValueError as e:
        render_range.delete(0, len(render_range.get()))
        return

    global edit_image_array, selected_color, operations

    # copy the array before edit
    step = copy.deepcopy(edit_image_array)
    operations.append(step)

    if edit_image_array is not None and selected_color is not None and selected_new_color is not None:
        for row in edit_image_array:
            for cell in row:
                if is_same(cell, selected_color):
                    cell[0] = selected_new_color[0]
                    cell[1] = selected_new_color[1]
                    cell[2] = selected_new_color[2]
        render_image()


confirm_change_button = tk.Button(window, text="Do Change", width=10, height=1, command=change_all_entry)
confirm_change_button.place(x=200, y=60)


def undo():
    global operations, edit_image_array
    if len(operations) < 1:
        return
    edit_image_array = operations.pop(len(operations) - 1)
    render_image()


undo_button = tk.Button(window, text="Undo", width=10, height=1, command=undo)
undo_button.place(x=350, y=60)


# custom destroy function, clean up the temp file
def close_window():
    if os.path.exists('temp$1.png'):
        os.remove('temp$1.png')
    window.destroy()


window.protocol('WM_DELETE_WINDOW', close_window)

window.mainloop()
