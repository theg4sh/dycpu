#!/usr/bin/python3.4m

import psutil;
import argparse;
import os, sys;
import re;
import threading;
import datetime;

class CPU_aggr:
    MIN_ONLINE = 2;
    LIMIT_HIST = 20;
    MAX_CPU_ID = -1;
    def __init__(self, path):
        print(path);
        m = re.match('.*/cpu([0-9]+)/.*', path);
        if m is None:
            raise Exception("Ivalid cpu path: %s" % path);
        self._path = path;
        self._cid = int(m.group(1));
        self._online = 0;
        self.updateOnlineStatus();
        self._load_hist = [0]*CPU_aggr.LIMIT_HIST;

        CPU_aggr.MAX_CPU_ID = max(CPU_aggr.MAX_CPU_ID, self._cid);

    def __repr__(self):
        return '<%sCPU_aggr[%d]:%-6.2f>' % ('+' if self.isOnline() else '-', self._cid, self.getLoad());

    def getId(self):
        return self._cid;
    def isOnline(self):
        return (self._online == 1);

    def _setOnline(self, val):
        if bool(self._online) == bool(val):
            return;
        else:
            with open(self._path, "w") as f:
                f.write("%d\n" % (int(val)));
            self._online = int(val);
    def setOnline(self):
        self._setOnline(True);
    def setOffline(self):
        self._setOnline(False);
    def updateOnlineStatus(self):
        with open(self._path, "r") as f:
            self._online = int(f.readline());

    def addLoad(self, pct):
        self._load_hist.append(pct);
        if len(self._load_hist) > CPU_aggr.LIMIT_HIST:
            self._load_hist = self._load_hist[-CPU_aggr.LIMIT_HIST:]

    def getLoad(self):
        if self.isOnline():
            return (1.0*sum(self._load_hist))/CPU_aggr.LIMIT_HIST;
        else:
            return 0.0;

def gen_online_cpu(cpus):
    for cpu in cpus.values():
        if cpu.isOnline():
            yield cpu;

cpu_dir = "/sys/devices/system/cpu/";
cpus = [CPU_aggr(os.path.join("%s%s" % (cpu_dir, c),'online')) for c in os.listdir(cpu_dir) if re.match(r'^cpu[0-9]+$', c)];
cpus = {i:c for i,c in enumerate(cpus)};
print(cpu_dir, cpus);

sleep_event = threading.Event();
ticks_lowusage = 0;
ticks_highusage = 0;
opts = {
  'daemon': False,
  'load_high': 60.0,
  'load_low':  10.0,
  'trig_high': 4,
  'trig_low':  50,
  'cpu_online_min': CPU_aggr.MIN_ONLINE,
}
# TODO: switch the cores to the next pair in list after few hours instead of first MIN_ONLINT cores always, e.g. +0h - 0:1, +1h - 1:2, +2 - 2:3, etc.
# TODO: detec core loading increasing in lower than 60.0 range and enable core to prevent loading stuck
while not sleep_event.wait(0.75):
    #tm = psutil.cpu_times(percpu=True);
    pc = psutil.cpu_percent(percpu=True);

    # Update cpus statuses to catch manually changed status
    for cpu in cpus.values():
        cpu.updateOnlineStatus();
    cc = len([c for c in cpus.values() if c.isOnline()])

    gcpu = gen_online_cpu(cpus);
    for p in pc:
        cpu = next(gcpu);
        cpu.addLoad(p);

    #print([c.getLoad() for c in cpus.values() if c.isOnline()], cc, "%.2f" % (sum(c.getLoad() for c in cpus.values() if c.isOnline())/cc) );
    avgload = 1.0*sum(c.getLoad() for c in cpus.values() if c.isOnline())/cc;
    if not opts['daemon']:
        sys.stdout.write("\ronline:%d/%d avgload:%-6.2f [lu:%-3d hu:%-3d] %s" % ( cc, CPU_aggr.MAX_CPU_ID+1,
                    avgload, ticks_lowusage, ticks_highusage,
                    " ".join(str(c) for c in cpus.values() if c.isOnline()) ) );

    if avgload >= opts['load_high']:
        ticks_lowusage = 0;
        ticks_highusage += 1;
        if ticks_highusage < opts['trig_high']:
            continue;

        for c in cpus.values():
            if not c.isOnline():
                cpu = c;
                break;
        else:
            # Offline CPU not found, so, continue
            continue;

        ticks_highusage = 0;
        if not opts['daemon']:
            sys.stdout.write("\n[%s] Detected high cpus usage. Enabling CPU %d\n" %  (str(datetime.datetime.now()), cpu.getId()) );
        cpu.setOnline();

    elif avgload < opts['load_low']:
        ticks_highusage = 0;
        if len([c for c in cpus.values() if c.isOnline()]) > opts['cpu_online_min']:
            ticks_lowusage += 1;
        if ticks_lowusage <  opts['trig_low']:
            continue;

        ticks_lowusage = 0;
        cpu = None;
        for c in gen_online_cpu(cpus):
            cpu = c;
        if cpu is None:
            continue;

        if not opts['daemon']:
            sys.stdout.write("\n[%s] Detected low cpus usage. Disabling CPU %d\n" % (str(datetime.datetime.now()), cpu.getId()) );
        cpu.setOffline();
    else:
        ticks_lowusage = 0;
        ticks_highusage = 0;
