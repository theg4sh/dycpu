# DyCPU
A tool mostly intended for IoT devices. It monitoring a CPU's loading and disable or enable CPUs depending on how currently enabled CPUs is loaded in configured time.
## Why?
In short, keeps a silent during a night making less temperature of MPU, peaks of which make a cooler to work.<br/>
#### Odroid XU4
The MPU have 8 cores and it using the cooler when temperature becomes to 68℃.<br/>
In avg, it happens each 1 min for 10s.<br/>
Using DyCPU allows to reduce upper bound to 57℃ and, as result of disabled cpu, reduce the power consumption.

# Usage
The tool required write access to <em>/sys/devices/system/cpu/cpuN/online</em>.<br/>
Regarding this, run the tool from root:<br/>
<code>screen -dmS dycpu python3 ./dycpu.py</code>
