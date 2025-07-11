import subprocess
import socket
import time
import sys
import os
from flask import Flask, redirect, url_for
from dougdraw.routes import dougdraw_bp

INVOKEAI_HOST = "127.0.0.1"
INVOKEAI_PORT = 9090

def is_invokeai_running(host=INVOKEAI_HOST, port=INVOKEAI_PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) == 0

# Start InvokeAI server if not running
if is_invokeai_running():
    print("✅ InvokeAI server is running.")
else:
    print("⚠️  InvokeAI server is not running. Starting it now...")
    subprocess.Popen(["start", "start_invokeai_server.bat"], shell=True)
    # Wait for server to start
    for _ in range(30):
        if is_invokeai_running():
            print("✅ InvokeAI server started.")
            break
        time.sleep(2)
    else:
        print("❌ Failed to start InvokeAI server.")
        sys.exit(1)

app = Flask(__name__)
app.register_blueprint(dougdraw_bp)

@app.route('/')
def index():
    return redirect(url_for('dougdraw.dougdraw_home'))

if __name__ == '__main__':
    app.run(debug=True)