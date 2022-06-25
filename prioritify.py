#!/usr/bin/env python3

import psutil
from Xlib import X
from Xlib.display import Display
from Xlib.protocol.rq import Event

disp = Display()
root = disp.screen().root

active_window = disp.intern_atom("_NET_ACTIVE_WINDOW")
pid = disp.intern_atom("_NET_WM_PID")

latest = None

DEFAULT_NICENESS = 0
TARGET_NICENESS = -10


def get_pid(wid) -> int:
    win = disp.create_resource_object("window", wid)

    try:
        r = win.get_full_property(pid, X.AnyPropertyType)
    except:
        return 0

    if not r:
        return 0

    return r.value[0]


def set_nice(pid, niceness):
    if pid == -1:
        return

    p = psutil.Process(pid)

    p.nice(niceness)

    print(f"changed {pid} niceness to {niceness}")


def handle(e: Event):
    global latest

    if e.type != X.PropertyNotify:
        return

    if e.atom == active_window:
        r = root.get_full_property(active_window, X.AnyPropertyType)

        if not r:
            return
        wid = r.value[0]

        if wid != active_window and wid:
            if latest == wid:
                return

            latest_pid = -1
            if latest:
                latest_pid = get_pid(latest)
            wid_pid = get_pid(wid)

            if not latest_pid or not wid_pid:
                return

            set_nice(latest_pid, DEFAULT_NICENESS)
            set_nice(wid_pid, TARGET_NICENESS)

            latest = wid


def main():
    root.change_attributes(event_mask=X.PropertyChangeMask)

    while True:
        handle(disp.next_event())


if __name__ == "__main__":
    main()
