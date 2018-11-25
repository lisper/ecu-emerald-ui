#!/usr/bin/python

#
# Decode the serial protocol emitted by the Emerald ECU when running
# Brad Parker <brad@heeltoe.com> 7/2018
# 

import time
import serial
import struct

class Protocol():
    def __init__(self):
        self.devicename = '/dev/ttyS0'
        self.baudrate = 19200
        self.buffer = ''
        self.state = 0
        self.new_data = False
        self.dumping = False
        self.logging = False
        self.logfile = []

        self.proto_state = {
            0: self.state0,
            1: self.state1,
            2: self.state2,
            3: self.state3,
            }

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
        self.air_temp_f = 0
        self.coolant_temp_f = 0
        self.battery = 0.0
        self.coil_on_time = 0
        self.aux_in34 = 0
        self.aux_in35 = 0
        self.fuel_pressure = 0.0

    def setDevice(self, dev):
        self.devicename = dev

    def setBaudrate(self, rate):
        self.baudrate = rate

    def setLogfile(self, f):
        self.logfile = f
        self.logging = True

    def getLogfile(self):
        return self.logfile

    def open(self):
        self.ser = serial.Serial(port=self.devicename,
                                 baudrate=self.baudrate,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 bytesize=serial.EIGHTBITS
                                 )
#        self.ser.open()
        return self.ser.isOpen()

    def close(self):
        logging = False
        self.ser.close()

    def check(self):
        ret = self.new_data
        if (ret):
            self.new_data = False
        return ret

    # -----------------

    def start_state2(self):
        self.packet = b'\x00\x00'
        self.packet_time = int(time.time())
        self.state = 2

    def stop_state2(self):
        self.push_packet()
        self.state = 0

    def state0(self, ch):
        if (ch == b'\xdb'):
            self.state = 1

    def state1(self, ch):
        if (ch == b'\xc0'):
            self.start_state2()
        else:
            self.state = 1

    def state2(self, ch):
        if (ch == b'\xdb'):
            self.state = 3
        else:
            if (ch == b'\xc0'):
                self.stop_state2()
            else:
                self.packet += ch

    def state3(self, ch):
        if (ch == b'\xc0'):
            self.start_state2()
        else:
            if (ch == b'\xdc'):
                self.packet += b'\xc0'
                self.state = 2
            else:
                if (ch == b'\xdd'):
                    self.packet += b'\xdb'
                    self.state = 2

    #
    # log file format
    # 'DATA' + 4 byte unix timestamp + 2 byte packet length + packet
    #
    def log_data(self):
        self.logfile.write('DATA' + struct.pack(">I", self.packet_time) + struct.pack(">h", len(self.packet)) + self.packet)

    def dump_data(self):
        print "data: rpm %d tps %d ign_adv %f afr %f air %d coolant %d battery %f fuel %d" % (self.rpm, self.tps_perc, self.ign_adv, self.afr, self.air_temp_c, self.coolant_temp_c, self.battery, self.aux_in34)

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

    def push_packet(self):
        self.new_data = True
        id = ord(self.packet[2])
        #print "packet id %d" % id
        if (id == 0):
            self.packet0()
        else:
            if (id == 1):
                self.packet1()
        if (self.dumping):
            self.dump_data()
        if (self.logging):
            self.log_data()

    def poll(self):
        waiting = self.ser.inWaiting()
        if (waiting > 0):
            buffer = self.ser.read(waiting)
            for i in range(len(buffer)):
                func = self.proto_state.get(self.state, "nothing")
                ch = buffer[i]
                func(ch)

if __name__ == '__main__':
    p = Protocol()
    p.open()
    p.dumping = True
    while (1):
        p.poll()

