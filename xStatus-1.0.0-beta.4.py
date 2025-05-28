# xStatus - A utility application that sends status notifications for Christmas light shows.
# Copyright (C) 2025 TurboTech

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation at version 3 of the License.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Not associated with the xLights organization.

from tabulate import tabulate
import urllib.request
import datetime
import requests
import json
import time
import os

CONFIG_PATH = "xStatus_config.json"
DEFAULT_CONFIG = {
    "xschedule_api_url": "http://localhost:80/xScheduleQuery?Query=GetPlayingStatus",
    "method": "discord",
    "discord_user": "your_discord_username",
    "show_start_time": "17:30",
    "show_end_time": "22:30"
}

MAKE_WEBHOOK_URL = "https://hook.us2.make.com/57hitx0g0r7rl8v56ofsdkac6a3slji9"
TURBOLIB = "https://raw.githubusercontent.com/Luk3210/TurboLib/refs/heads/main/project_versions.json"

current_version = "1.0.0-beta.4"

print(r"""        ____  _        _              """)
print(r""" __  __/ ___|| |_ __ _| |_ _   _ ___  """)
print(r""" \ \/ /\___ \| __/ _  | __| | | / __| """)
print(r"""  >  <  ___) |  | (_| | |_| |_| \ __\ """)
print(r""" /_/\_\|____/ \__\__,_|\__|\__,_|___/ """)
print()
print("xStatus Copyright (C) 2025 TurboTech")

try:
    with urllib.request.urlopen(TURBOLIB) as response:
        data = json.load(response)
        latest = data.get("xStatus")
        if latest == current_version:
            print(f"You are running the latest version ({current_version}).")
        if latest != current_version:
            print(f"WARNING: A newer version of xStatus is available ({latest}). You are using {current_version}.")
except Exception:
    print("ERROR: TurboLib is not accessable so the latest version could not be checked. Please check your internet connection and try again.")
    pass

offline_controllers = set()
if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)
    print(f"Created new config file with defaults at the active directory. \nPlease edit it with your own settings.")
    time.sleep(10)
    exit(0)
else:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

while True:
    now = datetime.datetime.now().time()
    start_time = datetime.datetime.strptime(config.get("show_start_time"), "%H:%M").time()
    end_time = datetime.datetime.strptime(config.get("show_end_time"), "%H:%M").time()
    error_start_timer = time.perf_counter()

    if start_time <= now and now < end_time:
        try:
            resp = requests.get(config["xschedule_api_url"], timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            print("ERROR: Failed to connect to the xSchedule API. Is xSchedule open?")
            time.sleep(5)
            exit(1)

        controllers = data["pingstatus"]
        
        if not controllers:
            print("No controllers to show.")
        else:
            table = []
            for c in controllers:
                table.append(
                    [
                        c.get("controller"),
                        c.get("ip"),
                        c.get("result"),
                        c.get("failcount"),
                    ]
                )
            headers = ["Controller", "IP", "Result", "Failcount"]
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] \n{tabulate(table, headers, tablefmt='grid')}")

            for controller in controllers:
                is_online = controller.get("result", "").lower() == "ok"

                if (not is_online and controller["controller"] not in offline_controllers):
                    print(f"Controller offline: {controller['controller']} ({controller['ip']})")
                    payload = {
                        "method": config["method"],
                        "discord_user": config["discord_user"],
                        "controller": controller["controller"],
                        "status": "offline"
                    }
                    headers_ = {"Content-Type": "application/json"}
                    try:
                        response = requests.post(MAKE_WEBHOOK_URL, json=payload, headers=headers_, timeout=10)
                        print(f"Webhook sent for {controller['controller']} (offline): {response.status_code} {response.text}")
                    except Exception as e:
                        print(f"Failed to send webhook for {controller['controller']}: {e}")
                        
                    offline_controllers.add(controller["controller"])
                elif is_online and controller["controller"] in offline_controllers:
                    print(f"Controller back online: {controller['controller']} ({controller['ip']})")
                    payload = {
                        "method": config["method"],
                        "discord_user": config["discord_user"],
                        "controller": controller["controller"],
                        "status": "online"
                    }
                    headers_ = {"Content-Type": "application/json"}
                    try:
                        response = requests.post(MAKE_WEBHOOK_URL, json=payload, headers=headers_, timeout=10)
                        print(f"Webhook sent for {controller['controller']} (online): {response.status_code} {response.text}")
                    except Exception as e:
                        print(f"Failed to send webhook for {controller['controller']}: {e}")
                    offline_controllers.remove(controller["controller"])

    else:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Not within allowed time range ({start_time} - {end_time}), skipping loop.")

    time.sleep(15 - (time.perf_counter() - error_start_timer))