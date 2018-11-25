# ecu-emerald-ui
Simple python based data logger/user interface for Emerald K3 ECU

[RaspberryPI Data logger device](pics/IMG_1010.jpg)

Python code which runs on a Raspberrypi and connects via RS-232 to the
Emerald ECU data port. The Emerald ECU is a nice aftermarket engine
control computer which is very easy to setup and
use. http://www.emeraldm3d.com

The python UI program runs as an X window ui with the RaspberryPI 7"
LCD touch screen.  Data can be collected and real time data can be
displayed.  Handy in cases where strapping a laptop to the passenger
seat and taking 5 laps around the track is difficult.

[Readtime data screen](pics/IMG_1019.jpg)

(we tried the laptop strapped down a while but found it was
impractical.  the smaller raspberrypi datalogger was much easier to
setup and eeasy to use to log critical data).

There is also a python data display program which will graph the
connected log files and allow one to scroll through them and look at
data.

Brad Parker
brad@heeltoe.com
7/2018

Hardware parts needed:

https://www.amazon.com/gp/product/B01C6Q2GSY/ref=od_aui_detailpages00?ie=UTF8&psc=1
https://www.amazon.com/gp/product/B0153R2A9I/ref=od_aui_detailpages00?ie=UTF8&psc=1
https://www.amazon.com/gp/product/B071J7SLM8/ref=od_aui_detailpages01?ie=UTF8&psc=1
https://www.amazon.com/gp/product/B01HV97F64/ref=od_aui_detailpages01?ie=UTF8&psc=1

You'll also need a 3.3V TTL RS-232 adapter, like this one:

https://www.amazon.com/NulSom-Inc-Ultra-Compact-Converter/dp/B00OPU2QJ4/ref=sr_1_6_sspa?s=electronics&ie=UTF8&qid=1543182638&sr=1-6-spons&keywords=3.3v+ttl+to+rs-232+adapter&psc=1

With that, any DB-9 to DB-9 serial cable will connect the RS-232 adapter to the Emerald ECU
