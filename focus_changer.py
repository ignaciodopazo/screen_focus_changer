import sys
from enum import Enum
from locale import atof, atoi
from time import sleep
from typing import List, Dict, Any
import subprocess


class MovementDirection(Enum):
    """
    Monitor change direction
    """
    LEFT = "left"
    RIGHT = "right"


def get_current_windows_position() -> Dict[str, int]:
    """
    :return: The current active windows position. i.e: { "x": 140, "y": 940 }
    """
    active_windows = subprocess.getoutput("xdotool getactivewindow")
    lines = subprocess.getoutput("xdotool getwindowgeometry " + active_windows).split("\n")[1:]
    position: Dict[str, int] = {}
    position["y"], position["x"] = {atoi(x.replace(" (screen", "")) for x in lines[0].split(": ")[1].split(",")}
    return position


def get_all_monitors() -> List[Dict[str, Any]]:
    """
    :return: all monitors array list sorted from left to right.
    i.e: [
        {'hr': 1366, 'vr': 768, 'ho': 0, 'vo': 914, 'name': 'eDP-1-1'},
        {'hr': 2560, 'vr': 1440, 'ho': 1366, 'vo': 0, 'name': 'HDMI-1-1'},
        ]
    """
    # all_monitors_xrand_resp_ is string like this:
    #    Monitors: 2
    # 0: +*HDMI-1-1 2560/621x1440/341+1366+0  HDMI-1-1
    # 1: +eDP-1-1 1366/309x768/174+0+45  eDP-1-1
    all_monitors_xrand_resp_ = subprocess.getoutput("xrandr --listmonitors")
    monitors_ = []
    for line_ in all_monitors_xrand_resp_.split(": ")[2:]:
        monitor = {
            # Horizontal resolution. i.e 2560
            "hr": atoi(line_.split(" ")[1].split("/")[0]),
            # Vertical resolution.   i.e 1440
            "vr": atoi(line_.split(" ")[1].split("/")[1].split("x")[1].split("/")[0]),
            # Horizontal offset.     i.e 1366
            "ho": atoi(line_.split(" ")[1].split("+")[1]),
            # Vertical offset.       i.e 0
            "vo": atoi(line_.split(" ")[1].split("+")[2]),
            # Monitor name.          i.e HDMI-1-1
            "name": line_.replace("  ", " ").rsplit(" ")[0].replace("+", "").replace("*", ""),
        }
        monitors_.append(monitor)
    return sorted(monitors_, key=lambda i: i['ho'])


def get_current_monitor_pos(monitors: List[Dict[str, Any]], pos: Dict[str, int]) -> int:
    for i in range(len(monitors)):
        if monitors[i]["ho"] <= pos["x"] < monitors[i]["hr"] + monitors[i]["ho"]:
            return i


def determine_monitor_to_move(mov: MovementDirection, current_pos: int, n_monitors: int) -> int:
    if mov == MovementDirection.LEFT:
        return current_pos - 1 if current_pos > 0 else 0
    if mov == MovementDirection.RIGHT:
        return current_pos + 1 if current_pos < n_monitors - 1 else n_monitors - 1
    exit("ERROR: Invalid numbers of monitors: {}".format(n_monitors))


def get_center_of_monitor(monitor: Dict[str, Any]) -> Dict[str, int]:
    return {
        "x": (monitor["hr"] / 2) + monitor["ho"],
        "y": (monitor["vr"] / 2) + monitor["vo"],
    }


def change_monitor_focus(mov: MovementDirection) -> int:
    pos = get_current_windows_position()
    monitors = get_all_monitors()
    current_monitor_pos = get_current_monitor_pos(monitors, pos)
    new_monitor_pos = determine_monitor_to_move(mov, current_monitor_pos, len(monitors))
    if new_monitor_pos == current_monitor_pos:
        return new_monitor_pos
    center_of_screen = get_center_of_monitor(monitors[new_monitor_pos])
    query_get_window_at = "xdotool mousemove {} {} getmouselocation --shell mousemove restore & echo $WINDOW ".format(
        center_of_screen["x"],
        center_of_screen["y"]
    )
    window_id = subprocess.getoutput(query_get_window_at).split("WINDOW=")[1]
    subprocess.getoutput("xdotool windowactivate {}".format(window_id))


def get_args() -> MovementDirection:
    if len(sys.argv) == 1:
        print("Arguments (left or right) are required")
        exit(1)
    if len(sys.argv) > 2:
        print("Only one argument is allowed")
        exit(1)
    mov = str(sys.argv[1]).lower()
    if mov == MovementDirection.RIGHT.value:
        return MovementDirection.RIGHT
    if mov == MovementDirection.LEFT.value:
        return MovementDirection.LEFT
    print("Invalid args: {}".format(mov))
    exit(1)


if __name__ == '__main__':
    change_monitor_focus(get_args())