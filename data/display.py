#!/usr/bin/python

import os
import sys

import Tkinter
from Tkinter import *

import dumper
from dumper import *

def plot_grid(log, plot_offset):
    global canvas, on_screen, on_screen_time

    ost = on_screen_time[0]
    data_len = len(log.data_list)
    for i in range(0,800):
        index = i + plot_offset
        if (index >= data_len):
            break;
        if on_screen_time[i] != ost:
            ost = on_screen_time[i]
            canvas.create_line(i, 0, i, 400, fill='gray', width=1)

#    for i in range(0,400):
#        if (i % 50) == 0:
#            canvas.create_line(0, i, 800, i, fill='gray', width=1)

def plot_time(log, plot_offset):
    pass

def plot_one(log, plot_offset, which, min, max, scale, color, displace, show):
    global canvas, on_screen, on_screen_time

    data_len = len(log.data_list)
    #print "plot_one() data_len %d, offset %d" % (data_len, plot_offset)
    old_i = 0
    old_p = 400
    old_v = 0

    want_id = 0
    orig_which = which
    if which > 8:
        want_id = 1
        which -= 8

    for i in range(0,800):
        index = i + plot_offset
        if (index >= data_len):
            break;
        x = l.data_list[index]
        id = x[0]
        if id == want_id:
            v = float(x[which])
            vscaled = v * scale
            s = (vscaled - min) / (max-min)
            s = (s * 400)
            p = 400 - int(s) - displace
            if i > 0 and show:
                canvas.create_line(old_i, old_p, i, p, fill=color, width=1)
            old_v = v
            old_p = p
            old_i = i
            on_screen[i][orig_which] = v
        else:
            on_screen[i][orig_which] = old_v

        on_screen_time[i] = l.data_time[index]

def hit_left():
    global canvas, old_cursor, plot_offset, pos_lbl
    if old_cursor != None:
        canvas.delete(old_cursor)
    canvas.delete("all")
    plot_offset -= 200
    if plot_offset < 0:
        plot_offset = 0
    pos_lbl.config(text="%d" % plot_offset)
    plot_at_offset()

def hit_right():
    global canvas, old_cursor, plot_offset, pos_lbl
    if old_cursor != None:
        canvas.delete(old_cursor)
    canvas.delete("all")
    plot_offset += 200
    pos_lbl.config(text="%d" % plot_offset)
    plot_at_offset()

def draw_cursor(event):
    global canvas, old_cursor, cursor_pos, plot_offset, pos_lbl
    global data_item, on_screen
    if str(event.type) == '4' or str(event.type) == '6':
        spot = event.x
        if old_cursor != None:
            canvas.delete(old_cursor)
        old_cursor = canvas.create_line(spot, 0, spot, 400, fill='red', width=1)
        cursor_pos = spot + plot_offset
        pos_lbl.config(text="%d (%d)" % (plot_offset, cursor_pos))
        #print "spot %d on_screen %d" % (spot, on_screen[spot][12])
        for i in range(0,8):
            data_item[i].update( on_screen[spot][data_item[i].item] )

def plot_at_offset():
    global log, plot_offset
    plot_one(log, plot_offset, 1,  0, 7000,  1.0, "green",    0, True)
    plot_one(log, plot_offset, 3,  0,  100,  1.0, "purple",   0, True)
    plot_one(log, plot_offset, 4,  0,   40,  1.0, "orange", 500, False)
    plot_one(log, plot_offset, 7,  0,   25,  1.0, "blue",     0, True)
    plot_one(log, plot_offset, 9,  0,  255,  1.0, "black",  300, False)
    plot_one(log, plot_offset, 10, 0,  255,  1.0, "red",    600, False)
    plot_one(log, plot_offset, 11, 0,  255,  1.0, "cyan",   300, False)
#    plot_one(log, plot_offset, 12, 0,  255, 0.25, "brown",  200, True)
    plot_one(log, plot_offset, 15, 0,  80,   0.5, "brown",  300, True)
    plot_grid(log, plot_offset)
    plot_time(log, plot_offset)

class data_thing():
    def __init__(self, frame, item, name, row, col):
        self.outer_frame = frame
        self.item = item
        self.name = name

        self.frame = Frame(self.outer_frame, width=100, height=50,
                           highlightbackground="green", highlightcolor="green", highlightthickness=1, bd=0)
        self.frame.grid(column=col,row=row)
        self.frame.pack_propagate(False) # don't shrink

        self.lbl = Label(self.frame, text=self.name, font=("Arial Bold", 8), width=10)
#        self.lbl.grid(row=0,column=0)
        self.lbl.pack()

        self.data_lbl = Label(self.frame, text="", font=("Arial Bold", 8), width=10)
#        self.data_lbl.grid(row=0,column=1)
        self.data_lbl.pack()

    def update(self, v):
        if (isinstance(v, float)):
            self.data_lbl.config(text="%6.2f" % v)
        else:
            self.data_lbl.config(text=v)

def make_frame(frame, item, name, row, col):
    thing = data_thing(frame, item, name, row, col)
    return thing

def loop(the_log):
    global canvas, old_cursor, log, plot_offset, pos_lbl
    global data_item, on_screen, on_screen_time

    log = the_log

    window = Tk()
    window.title("UI")

    window.geometry("800x600")
#    window.resizable(0, 0)

    back = Frame(window)
    back.pack_propagate(0)
    back.pack(fill=BOTH, expand=1)

    lbl = Label(back, text="Emerald ECU", font=("Arial Bold", 50))
    lbl.pack(fill=X, side=BOTTOM)

    frame = Frame(back, width=800, height=300)
    frame.grid(row=0, column=0)

    canvas = Canvas(frame, bg='#FFFFFF')

    canvas.config(width=670, height=400)
    canvas.grid(column=2,row=0)

    left_btn = Button(frame, text="<", font=("Arial Bold", 30), command=hit_left)
    left_btn.grid(column=1,row=0,sticky=N+S)

    right_btn = Button(frame, text=">", font=("Arial Bold", 30), command=hit_right)
    right_btn.grid(column=3,row=0,sticky=N+S)

    pos_lbl = Label(back, text="<pos>", font=("Arial Bold", 10))
    pos_lbl.pack()

    #
    data_frame = Frame(back, width=800, height=100)
    data_frame.grid(column=0,row=1,sticky=S)

    data_item = [None, None, None, None, None, None, None, None]
    data_item[0] = make_frame(data_frame, 1, "RPM", 0, 0)
    data_item[1] = make_frame(data_frame, 3, "TPS%", 0, 1)
    data_item[2] = make_frame(data_frame, 4, "ign adv", 0, 2)
    data_item[3] = make_frame(data_frame, 7, "AFR", 0, 3)

    data_item[4] = make_frame(data_frame, 9,  "air", 1, 0)
    data_item[5] = make_frame(data_frame, 10, "coolant", 1, 1)
    data_item[6] = make_frame(data_frame, 11, "battery", 1, 2)
#    data_item[7] = make_frame(data_frame, 12, "fuel", 1, 3)
    data_item[7] = make_frame(data_frame, 15, "fuel press", 1, 3)

    data_item[0].update(0)

    #
    on_screen = [[0 for i in range(0,16)] for i in range(0,800)]
    on_screen_time = [0 for i in range(0,800)]

    #
    plot_offset = 0
    plot_offset = 1600
    plot_at_offset()

    old_cursor = None
    canvas.bind('<ButtonPress-1>', draw_cursor)
    canvas.bind('<B1-Motion>', draw_cursor)

    window.mainloop()

if __name__ == '__main__':
    l = LogReader()
    l.open(sys.argv[1])
    l.absorb()
    loop(l)


#loop()

