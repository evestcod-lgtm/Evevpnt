import os
import json
import subprocess
import threading
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

SERVERS = [
    {"id": 0, "name": "Germany Premium", "flag": "🇩🇪", "host": "de2.pineappled.org", "port": 443, "uuid": "71322f86-f37a-4929-ada0-05e6a2688145"},
    {"id": 1, "name": "Finland Fast", "flag": "🇫🇮", "host": "fi1.pineappled.org", "port": 443, "uuid": "71322f86-f37a-4929-ada0-05e6a2688145"},
    {"id": 2, "name": "Netherlands", "flag": "🇳🇱", "host": "nl1.pineappled.org", "port": 443, "uuid": "71322f86-f37a-4929-ada0-05e6a2688145"}
]

def generate_xray_config(server):
    config = {
        "inbounds": [{"port": 10808, "protocol": "socks", "settings": {"auth": "noauth"}}],
        "outbounds": [{
            "protocol": "vless",
            "settings": {
                "vnext": [{
                    "address": server["host"],
                    "port": server["port"],
                    "users": [{"id": server["uuid"], "encryption": "none"}]
                }]
            },
            "streamSettings": {"network": "tcp", "security": "reality", "realitySettings": {"sni": "www.apple.com"}}
        }]
    }
    with open("config.json", "w") as f:
        json.dump(config, f)

def start_xray():
    subprocess.Popen(["./xray", "-c", "config.json"])

def stop_xray():
    os.system("pkill xray")

@app.route('/vpn/connect/<int:srv_id>')
def connect(srv_id):
    server = next(s for s in SERVERS if s['id'] == srv_id)
    generate_xray_config(server)
    start_xray()
    return jsonify({"status": "connected", "server": server["name"]})

@app.route('/vpn/disconnect')
def disconnect():
    stop_xray()
    return jsonify({"status": "disconnected"})

HTML_CONTENT = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root { --red: #ff0000; --bg: #080808; --card: #121212; }
        body { background: var(--bg); color: white; font-family: sans-serif; text-align: center; margin: 0; padding-bottom: 20px; }
        .header { padding: 40px 0 10px; text-transform: uppercase; letter-spacing: 5px; color: var(--red); font-weight: bold; font-size: 24px; }
        #timerDisplay { font-family: monospace; color: #333; font-size: 26px; margin-bottom: 10px; transition: 0.3s; font-weight: bold; }
        #timerDisplay.active { color: var(--red); text-shadow: 0 0 20px var(--red); }
        .btn-box { margin: 20px 0; display: flex; justify-content: center; }
        .power-btn { width: 170px; height: 170px; border-radius: 50%; background: #111; border: 4px solid #1a1a1a; box-shadow: 10px 10px 25px #000; cursor: pointer; display: flex; justify-content: center; align-items: center; outline: none; transition: 0.4s; }
        .emoji-icon { font-size: 70px; filter: grayscale(100%) brightness(30%); transition: 0.4s; }
        .power-btn.active { border-color: var(--red); box-shadow: 0 0 50px rgba(255, 0, 0, 0.4); }
        .power-btn.active .emoji-icon { filter: grayscale(0%) brightness(100%); transform: scale(1.1); }
        #stText { font-size: 14px; font-weight: bold; margin-bottom: 30px; letter-spacing: 2px; color: #444; }
        #stText.active { color: var(--red); }
        .server-list { width: 92%; margin: 0 auto; text-align: left; }
        .server-item { background: var(--card); margin-bottom: 12px; padding: 16px; border-radius: 15px; display: flex; align-items: center; border: 1px solid #1a1a1a; cursor: pointer; }
        .server-item.selected { border-color: var(--red); background: #1a0505; }
        .flag { font-size: 26px; margin-right: 15px; }
        .srv-name { flex-grow: 1; font-weight: bold; font-size: 15px; }
    </style>
</head>
<body>
    <div class="header">EVEVPN</div>
    <div id="timerDisplay">00:00:00</div>
    <div class="btn-box"><button class="power-btn" id="mainBtn" onclick="toggleConnect()"><span class="emoji-icon">🩻</span></button></div>
    <div id="stText">DISCONNECTED</div>
    <div class="server-list"><div id="serversContainer"></div></div>
    <script>
        let servers = ''' + str(SERVERS) + ''';
        let selectedId = 0;
        let isConnected = false;
        let seconds = 0;
        let timerInterval;

        function renderServers() {
            const container = document.getElementById('serversContainer');
            container.innerHTML = servers.map(s => `
                <div class="server-item ${s.id === selectedId ? 'selected' : ''}" onclick="selectServer(${s.id})">
                    <span class="flag">${s.flag}</span>
                    <span class="srv-name">${s.name}</span>
                </div>
            `).join('');
        }

        function selectServer(id) {
            selectedId = id;
            renderServers();
            if(isConnected) {
                fetch('/vpn/connect/' + id);
                seconds = 0;
            }
        }

        function toggleConnect() {
            isConnected = !isConnected;
            document.getElementById('mainBtn').classList.toggle('active');
            const st = document.getElementById('stText');
            const tm = document.getElementById('timerDisplay');
            if(isConnected) {
                fetch('/vpn/connect/' + selectedId);
                st.innerText = "CONNECTED";
                st.classList.add('active');
                tm.classList.add('active');
                timerInterval = setInterval(() => {
                    seconds++;
                    let h = Math.floor(seconds/3600).toString().padStart(2,'0');
                    let m = Math.floor((seconds%3600)/60).toString().padStart(2,'0');
                    let s = (seconds%60).toString().padStart(2,'0');
                    tm.innerText = h + ':' + m + ':' + s;
                }, 1000);
            } else {
                fetch('/vpn/disconnect');
                clearInterval(timerInterval);
                seconds = 0;
                st.innerText = "DISCONNECTED";
                st.classList.remove('active');
                tm.classList.remove('active');
                tm.innerText = "00:00:00";
            }
        }
        renderServers();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
