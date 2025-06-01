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

from flask import Flask, request, Response
from tabulate import tabulate
from waitress import serve
import urllib.request
import threading
import datetime
import requests
import socket
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

current_version = "1.1.0"

print(r"""        ____  _        _              """)
print(r""" __  __/ ___|| |_ __ _| |_ _   _ ___  """)
print(r""" \ \/ /\___ \| __/ _  | __| | | / __| """)
print(r"""  >  <  ___) |  | (_| | |_| |_| \ __\ """)
print(r""" /_/\_\|____/ \__\__,_|\__|\__,_|___/ """)

print("\nxStatus Copyright (C) 2025 TurboTech")

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
        
webserver = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>xStatus</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 20px;
            text-align: center;
            transition: background-color 0.3s, color 0.3s;
        }
        h1 {
            color: #333;
            transition: color 0.3s;
        }
        #editor-container {
            max-width: 800px;
            margin: 20px auto;
            background: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            transition: background 0.3s, box-shadow 0.3s;
        }
        label {
            display: block;
            margin-top: 16px;
            margin-bottom: 4px;
            font-weight: bold;
            text-align: left;
        }
        input[type="text"], input[type="time"], select {
            width: 95%;
            padding: 8px;
            margin-bottom: 8px;
            font-size: 15px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background: #fff;
            color: #222;
            transition: background 0.3s, color 0.3s, border 0.3s;
            box-sizing: border-box;
            display: block;
        }
        /* Keep the native dropdown arrow */
        select {
            /* No appearance override, so browser arrow is kept */
        }
        button {
            margin-top: 10px;
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 5px;
            transition: background 0.3s;
        }
        button:hover {
            background: #0056b3;
        }
        .darkmode-toggle {
            position: absolute;
            top: 20px;
            right: 30px;
        }
        /* Notification styles: bottom right */
        #notification {
            position: fixed;
            bottom: 35px;
            right: 35px;
            background: #28a745;
            color: #fff;
            padding: 16px 32px;
            border-radius: 6px;
            font-size: 18px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.4s;
            display: none;
        }
        #notification.show {
            display: block;
            opacity: 1;
            pointer-events: auto;
        }
        /* Dark mode styles */
        body.dark-mode {
            background-color: #181a1b;
            color: #e6e6e6;
        }
        body.dark-mode h1 {
            color: #f7f7f7;
        }
        body.dark-mode #editor-container {
            background: #23272b;
            box-shadow: 0 0 10px rgba(0,0,0,0.6);
        }
        body.dark-mode input[type="text"], 
        body.dark-mode input[type="time"],
        body.dark-mode select {
            background: #181a1b;
            color: #e6e6e6;
            border: 1px solid #444;
        }
        body.dark-mode button {
            background: #375a7f;
            color: #fff;
        }
        body.dark-mode button:hover {
            background: #24476a;
        }
        body.dark-mode #notification {
            background: #357d44;
            color: #e6e6e6;
        }
    </style>
</head>
<body>
    <button class="darkmode-toggle" onclick="toggleDarkMode()">🌙 Dark Mode</button>
    <h1>Configure xStatus</h1>
    <div id="editor-container">
        <form id="jsonForm" onsubmit="event.preventDefault(); saveJson();">
            <label for="xschedule_api_url">xSchedule API URL</label>
            <input type="text" id="xschedule_api_url" name="xschedule_api_url" required>

            <label for="method">Notification Method</label>
            <select id="method" name="method" required>
                <option value="discord">Discord</option>
                <option value="experimental">Experimental (No promises that this will work)</option>
            </select>

            <label for="discord_user">Discord Username</label>
            <input type="text" id="discord_user" name="discord_user" required>
            
            <label for="show_start_time">Show Start Time</label>
            <input type="time" id="show_start_time" name="show_start_time" required>
            
            <label for="show_end_time">Show End Time</label>
            <input type="time" id="show_end_time" name="show_end_time" required>
            
            <button type="submit">Save</button>
        </form>
    </div>
    <div id="notification" style="display:none;"></div>
    <script>
        // Dark mode logic
        function isDarkMode() {
            return localStorage.getItem('darkMode') === 'true';
        }
        function applyDarkMode(state) {
            if (state) {
                document.body.classList.add('dark-mode');
                document.querySelector('.darkmode-toggle').textContent = '☀️ Light Mode';
            } else {
                document.body.classList.remove('dark-mode');
                document.querySelector('.darkmode-toggle').textContent = '🌙 Dark Mode';
            }
        }
        function toggleDarkMode() {
            const dark = !isDarkMode();
            localStorage.setItem('darkMode', dark);
            applyDarkMode(dark);
        }
        document.addEventListener('DOMContentLoaded', () => {
            applyDarkMode(isDarkMode());
        });

        // Show custom notification
        function showNotification(message) {
            const notif = document.getElementById('notification');
            notif.textContent = message;
            notif.classList.add('show');
            notif.style.display = "block";
            setTimeout(() => {
                notif.classList.remove('show');
                setTimeout(() => notif.style.display = "none", 400);
            }, 2000);
        }

        // Load JSON and fill fields
        async function loadJson() {
            const response = await fetch('/get_json');
            const data = await response.json();
            document.getElementById('xschedule_api_url').value = data.xschedule_api_url || "";
            document.getElementById('method').value = data.method || "discord";
            document.getElementById('discord_user').value = data.discord_user || "";
            document.getElementById('show_start_time').value = data.show_start_time || "";
            document.getElementById('show_end_time').value = data.show_end_time || "";
        }

        // Save fields as JSON
        async function saveJson() {
            const data = {
                xschedule_api_url: document.getElementById('xschedule_api_url').value,
                method: document.getElementById('method').value,
                discord_user: document.getElementById('discord_user').value,
                show_start_time: document.getElementById('show_start_time').value,
                show_end_time: document.getElementById('show_end_time').value
            };
            await fetch('/update_json', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            showNotification('JSON config file updated successfully!');
        }

        loadJson();
    </script>
</body>
</html>
"""

def load_json():
    with open(CONFIG_PATH, 'r') as file:
        return json.load(file)

def save_json(data):
    with open(CONFIG_PATH, 'w') as file:
        json.dump(data, file, indent=4)

@webserver.route('/')
def index():
    return Response(HTML, mimetype='text/html')

@webserver.route('/get_json', methods=['GET'])
def get_json():
    data = load_json()
    return webserver.response_class(
        response=json.dumps(data, indent=4, ensure_ascii=False),
        mimetype='application/json'
    )

@webserver.route('/update_json', methods=['POST'])
def update_json():
    data = request.json
    save_json(data)
    return webserver.response_class(
        response=json.dumps({"message": "JSON config file updated successfully! Restart the app for the changes to take effect."}, indent=4),
        mimetype='application/json'
    )

def run_webserver():
    serve(webserver, host="0.0.0.0", port=8080)

thread = threading.Thread(target=run_webserver, daemon=True)
thread.start()
print(f"You can configure xStatus from your browser at '{socket.gethostbyname(socket.gethostname())}:8080'")

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
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Not within show time range ({start_time} - {end_time}), skipping loop.")

    time.sleep(15 - (time.perf_counter() - error_start_timer))