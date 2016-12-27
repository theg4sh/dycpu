# DyCPU
Control tool for IoT devices to manage online cpu in depends on system load.
## Why?
It gives less working temperature in a time.<br/>
E.g. Odroid XU4 have 8 cores and it will use cooler when temperature get equals to 68℃.<br/>
In avg, it happends in ~1 min for a 10s.<br/>
Using DyCPU allows to decrease that region to 57℃ and, as result of disabled cpu, reduce the power consumption.

# Usage
The tool required write access to <em>/sys/devices/system/cpu/cpuN/online</em>.<br/>
Regarding this, run the tool from root:<br/>
<code>screen -dmS dycpu python3 ./dycpu.py</code>
