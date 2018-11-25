#!/usr/bin/python

import sys
import time
import struct

class LogReader():
    def __init__(self):
        self.logfilename = ''
        self.data_list = []
        self.data_time = []

        self.rpm = 0
        self.tps = 0
        self.tps_perc = 0
        self.ign_adv = 0.0
        self.primary_inj_bank_on_time = 0
        self.afr_target = 0.0
        self.afr = 0.0
        self.seconary_inj_bank_on_time = 0
        self.air_temp_c = 0
        self.coolant_temp_c = 0
        self.battery = 0.0
        self.coil_on_time = 0
        self.aux_in34 = 0
        self.aux_in35 = 0
        self.fuel_pressure = 0

    def open(self, fn):
        self.logfilename = fn
        self.f = open(self.logfilename, "rb")

    def close(self):
        if self.logfilename != '':
            self.f.close()
            self.logfilename = ''

    def packet0(self):
        self.rpm = (ord(self.packet[4]) << 8) | ord(self.packet[5])
        self.tps = (ord(self.packet[8]) << 8) | ord(self.packet[9])
        self.tps_perc = ord(self.packet[12])
        self.ign_adv = float(ord(self.packet[14])) / 2.0
        self.primary_inj_bank_on_time = (ord(self.packet[16]) << 8) | ord(self.packet[17])
        self.afr_target = float(ord(self.packet[20])) / 10.0
        self.afr = float(ord(self.packet[21])) / 10.0
        self.seconary_inj_bank_on_time = (ord(self.packet[28]) << 8) | ord(self.packet[29])

    def packet1(self):
        self.air_temp_c = ord(self.packet[4]) - 40
        self.coolant_temp_c = ord(self.packet[5]) - 40
        self.air_temp_f = self.air_temp_c * 1.8 + 32.0
        self.coolant_temp_f = self.coolant_temp_c * 1.8 + 32.0
        self.battery = float(ord(self.packet[7])) / 11.0
        self.aux_in34 = (ord(self.packet[12]) << 8) | ord(self.packet[13])
        self.aux_in35 = (ord(self.packet[14]) << 8) | ord(self.packet[15])
        self.coil_on_time = ord(self.packet[55])

        # linear voltage output, 0ps = 0.5v, 40psi 2.5v, 80psi output 4.5v
        v = (5.0 * float(self.aux_in34)) / 1023.0
        self.fuel_pressure = ((v - 0.5) / 4.0) * 80.0

    def push_record(self):
        id = ord(self.packet[2])
        self.last_id = id
        if (id == 0):
            self.packet0()
        else:
            if (id == 1):
                self.packet1()

    def dump_record(self):
        print "data: rpm %d tps %d ign_adv %4.1f afr %4.1f air %d coolant %d battery %4.1f fuel %d" % (self.rpm, self.tps_perc, self.ign_adv, self.afr, self.air_temp_c, self.coolant_temp_c, self.battery, self.aux_in34)


    def get_record(self):
        while True:
            snip = self.f.read(4)
            if len(snip) < 4 or snip == None:
                return False
            if snip == 'DATA':
                hdr = self.f.read(6)
                if len(hdr) != 6:
                    return False
                (self.packet_time, self.packet_len) = struct.unpack(">Ih", hdr)
                self.packet = self.f.read(self.packet_len)
                return True;

    def show(self):
        data_len = len(self.data_list)
        rpm = 0
        battery = 0
        raw = 0
        fp = 0
        for i in range(0,data_len):
            t = self.data_time[i]
            x = self.data_list[i]
            id = x[0]
            if id == 0:
                rpm = x[1]
            if id == 1:
                battery = x[3]
                raw = x[4]
                fp = x[7]
            lt = time.localtime(float(t))
            ts = time.strftime("%H:%M:%S", lt)
            v = (5.0 * float(raw)) / 1023.0
            print "[%d] %s %d %d %d %5.2f %5.2f %5.2f" % (i, ts, id, rpm, raw, v, battery, fp)

    def dump(self):
        while True:
            if not self.get_record():
                break;
            self.push_record()
            self.dump_record()

    def absorb(self):
        while True:
            if not self.get_record():
                break;
            self.push_record()
            if self.last_id == 0:
                self.data_list.append([0, self.rpm, self.tps, self.tps_perc, self.ign_adv,
                                       self.primary_inj_bank_on_time, self.afr_target, self.afr,
                                       self.seconary_inj_bank_on_time])
            elif self.last_id == 1:
                self.data_list.append([1, self.air_temp_f, self.coolant_temp_f, self.battery,
                                       self.aux_in34, self.aux_in35, self.coil_on_time, self.fuel_pressure])
            self.data_time.append(self.packet_time)

        print "read file, %d records" % len(self.data_list)

if __name__ == '__main__':
    l = LogReader()
    l.open(sys.argv[1])
    l.absorb()
#    l.dump()
    l.show()
