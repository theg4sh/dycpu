# DyCPU
Control tool for IoT devices to manage online cpu in depends on system load.

# Usage
The tool required write access to <em>/sys/devices/system/cpu/cpuN/online</em>.<br/>
Regarding this, run the tool from root:<br/>
<code>screen -dmS dycpu python3 ./dycpu.py</code>
