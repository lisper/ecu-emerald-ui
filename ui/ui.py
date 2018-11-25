#!/usr/bin/python

#
# Emerald ECU simple user interface using raspberri pi + 7" display
# Brad Parker <brad@heeltoe.com> 7/2018
#
# requires rs-232 adapter on rapsberri pi with cable to ECU
#

import os

import Tkinter
from Tkinter import *
from math import pi, cos, sin

import protocol
from protocol import *

logdirectory = "/logs"
polling = False

class Meter(Frame):
    def __init__(self, master=None, **kw):
        Frame.__init__(self, master, **kw)

        self.meter = []
        self.angle = []
        self.var = IntVar(self, 0)
        self.name = "unknown"
        self.min_v = 0.0
        self.max_v = 100.0

        self.canvas = Canvas(self, width=200, height=110,
                                borderwidth=2, relief='sunken',
                                bg='white')
#        self.scale = Scale(self, orient='horizontal', from_=0, to=100, variable=self.var)
        self.lbl = Label(self, text=self.name, font=("Arial Bold", 10))
        self.lbl.pack(fill=X, side=BOTTOM)

        self.vlbl = Label(self, text="", font=("Arial Bold", 8))
        self.vlbl.pack(fill=Y, side=BOTTOM)

        for j, i in enumerate(range(0, 100, 5)):
            self.meter.append(self.canvas.create_line(100, 100, 10, 100,
                                                      fill='grey%i' % i,
                                                      width=3,
                                                      arrow='last'))
            self.angle.append(0)
            self.canvas.lower(self.meter[j])
            self.updateMeterLine(0.2, j)

        self.canvas.create_arc(10, 10, 190, 190, extent=108, start=36,
                               style='arc', outline='red')

        for a in range(36, 145, 10):
            x1 = 100 - 90 * cos(float(a) * (pi / 180.0))
            y1 = 100 - 90 * sin(float(a) * (pi / 180.0))
            x2 = 100 - 95 * cos(float(a) * (pi / 180.0))
            y2 = 100 - 95 * sin(float(a) * (pi / 180.0))
            self.canvas.create_line(x1, y1, x2, y2, fill='red', width=1)


        self.canvas.pack(fill='both')
#        self.scale.pack()

        # if this line raises an error, change it to the old way of adding a trace: self.var.trace('w', self.updateMeter)
        #self.var.trace_add('write', self.updateMeter)
        self.var.trace('w', self.updateMeter)
        self.updateMeterTimer()

    def setName(self, n):
        self.name = n
        self.lbl.config(text=n)

    def setMinMax(self, min, max):
        self.min_v = min
        self.max_v = max
        self.canvas.create_text(20, 52, font=("Arial", 8), text=int(min))
        self.canvas.create_text(170, 52, font=("Arial", 8), text=int(max))

    def setValue(self, v):
        if (v != self.var.get()):
            print "setValue %s %d" % (self.name, v)
            self.var.set(v)
            if (isinstance(v, float)):
                self.vlbl.config(text="%6.2f" % v)
            else:
                self.vlbl.config(text=v)

    def updateMeterLine(self, a, l=0):
        """Draw a meter line (and recurse for lighter ones...)"""
        oldangle = self.angle[l]
        self.angle[l] = a
        x = 100 - 90 * cos(a * pi)
        y = 100 - 90 * sin(a * pi)
        self.canvas.coords(self.meter[l], 100, 100, x, y)
        l += 1
        if l < len(self.meter):
            self.updateMeterLine(oldangle, l)

    def updateMeter(self, name1, name2, op):
        """Convert variable to angle on trace"""
#        mini = self.scale.cget('from')
#        maxi = self.scale.cget('to')
        mini = 0.0
        maxi = 100.0
        mini = self.min_v
        maxi = self.max_v
        pos = (self.var.get() - mini) / (maxi - mini)
        self.updateMeterLine(pos * 0.6 + 0.2)

    def updateMeterTimer(self):
        """Fade over time"""
        self.var.set(self.var.get())
        self.after(20, self.updateMeterTimer)

def pick_new_logfile():
    global file_lbl, logdirectory, logfilename
    newcount = 1
    maxcount = 0
    if not os.path.isdir(logdirectory):
        logdirectory = ".";
    for dirname, dirnames, filenames in os.walk(logdirectory):
        for filename in filenames:
            if filename[0:7] == 'logfile':
                for l in range(7, len(filename)):
                    if filename[l] == '.':
                        break;
                count = 0
                if filename[7].isdigit():
                    count = int(filename[7:l])
                if count > maxcount:
                    maxcount = count;
        if maxcount != 0:
            newcount = maxcount + 1
        break
    logfilename = "logfile%d.dat" % newcount
    logfile = open(logfilename, "w")
    file_lbl.config(text="logging to %s" % logfilename)
    return logfile

def hit_start():
    global start_btn, stop_btn, proto, polling
    start_btn.config(state=DISABLED)
    stop_btn.config(state="normal")
    # create protocol object
    proto = Protocol()
    proto.open()
    # open new log file (figure out name)
    f = pick_new_logfile()
    proto.setLogfile(f)
    polling = True
    protocol_collect()


def hit_stop():
    global start_btn, stop_btn, proto, logfilename, polling
    start_btn.config(state="normal")
    stop_btn.config(state=DISABLED)
    f = proto.getLogfile()
    f.close()
    proto.close()
    # close log file
    file_lbl.config(text="last log: %s" % logfilename)
    polling = False

def hit_realtime_stop():
    global rwindow, realtime_stop
    realtime_stop = 1
    rwindow.destroy()
#    global meter1, meter2, meter3, meter4
#    global nn
#    nn = nn + 100
#    meter1.setValue(nn)

def protocol_poll():
    global rwindow, proto
    global meter1, meter2, meter3, meter4
    global meter5, meter6, meter7, meter8
    proto.poll()
    if (proto.check()):
        meter1.setValue(proto.rpm)
        meter2.setValue(proto.tps_perc)
        meter3.setValue(proto.afr)
        meter4.setValue(proto.ign_adv)
        meter5.setValue(proto.coolant_temp_f)
        meter6.setValue(proto.air_temp_f)
        meter7.setValue(proto.fuel_pressure)
        meter8.setValue(proto.battery)
    rwindow.after(1, protocol_poll)

def protocol_collect():
    global proto, window, polling
    proto.poll()
    if (polling):
        window.after(1, protocol_collect)


def hit_realtime():
    global rwindow, realtime_stop
    global proto
    global meter1, meter2, meter3, meter4
    global meter5, meter6, meter7, meter8
    global nn

    nn = 2

    rwindow = Tk()
    rwindow.title("REALTIME")

    rwindow.geometry("800x400")
    rwindow.resizable(0, 0)

    back = Frame(rwindow)
    back.pack_propagate(0)
    back.pack(fill=BOTH, expand=1)

    lbl = Label(back, text="REALTIME", font=("Arial Bold", 16))
    lbl.pack(fill=X, side=BOTTOM)

    button_frame = Frame(back)
    button_frame.pack(expand=0, side=TOP)

    stop_btn = Button(button_frame, text="STOP", font=("Arial Bold", 30), bg="red", command=hit_realtime_stop)
    stop_btn.grid(column=0, row=0)

    meter_frame = Frame(back)
    meter_frame.pack(fill=X, side=TOP)

    meter1 = Meter(meter_frame)
    meter1.grid(column=0, row=0)
    meter1.setName("RPM")
    meter1.setMinMax(0.0, 7000.0)

    meter2 = Meter(meter_frame)
    meter2.grid(column=1, row=0)
    meter2.setName("TPS%")
    meter2.setMinMax(0.0, 100.0)

    meter3 = Meter(meter_frame)
    meter3.grid(column=2, row=0)
    meter3.setName("AFR")
    meter3.setMinMax(0.0, 25.0)

    meter4 = Meter(meter_frame)
    meter4.grid(column=3, row=0)
    meter4.setName("ign adv")
    meter4.setMinMax(0.0, 50.0)

    #
    meter5 = Meter(meter_frame)
    meter5.grid(column=0, row=1)
    meter5.setName("H2O temp")
    meter5.setMinMax(0.0, 300.0)

    meter6 = Meter(meter_frame)
    meter6.grid(column=1, row=1)
    meter6.setName("air temp")
    meter6.setMinMax(0.0, 200.0)

    meter7 = Meter(meter_frame)
    meter7.grid(column=2, row=1)
    meter7.setName("fuel press")
    meter7.setMinMax(0.0, 80.0)

    meter8 = Meter(meter_frame)
    meter8.grid(column=3, row=1)
    meter8.setName("batt volts")
    meter8.setMinMax(0.0, 25.0)

    proto = Protocol()
    proto.open()

    rwindow.after(1, protocol_poll)
    rwindow.mainloop()
    proto.close()

def loop():
    global start_btn, stop_btn, realtime_btn, file_lbl, window

    window = Tk()
    window.title("UI")

    window.geometry("800x400")
    window.resizable(0, 0)

    back = Frame(window)
    back.pack_propagate(0)
    back.pack(fill=BOTH, expand=1)

    lbl = Label(back, text="Emerald ECU", font=("Arial Bold", 50))
    lbl.pack(fill=X, side=BOTTOM)

    button_frame = Frame(back)
    button_frame.pack(expand=0, side=TOP)

    start_btn = Button(button_frame, text="   START   ", font=("Arial Bold", 30), bg="green", command=hit_start)
    start_btn.grid(column=0,row=1, pady=20)

    stop_btn = Button(button_frame, text="    STOP    ", font=("Arial Bold", 30), bg="red", command=hit_stop)
    stop_btn.grid(column=0,row=2, pady=10)

    realtime_btn = Button(button_frame, text="REALTIME", font=("Arial Bold", 30), command=hit_realtime)
    realtime_btn.grid(column=0,row=3, pady=20)

    file_lbl = Label(back, text="<file>", font=("Arial Bold", 10))
    file_lbl.pack(side=TOP)

    stop_btn.config(state=DISABLED)

    window.mainloop()

#if __name__ == '__main__':
#    root = tk.Tk()
#    meter = Meter(root)
#    meter.pack()
#    root.mainloop()

loop()
