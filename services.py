import subprocess
from flask import jsonify

class ProcessManager:
    def __init__(self):
        self.processes = {}

    def start_program(self, session_name, phone_number, proxy):
        if session_name not in self.processes:
            self.processes[session_name] = subprocess.Popen(['screen', '-dmS', session_name, 'python', 'sms_program.py', phone_number, proxy])
            return jsonify({"msg": f"Program {session_name} started"}), 200
        else:
            return jsonify({"msg": f"Program {session_name} is already running"}), 400

    def stop_program(self, session_name):
        if session_name in self.processes:
            self.processes[session_name].terminate()
            del self.processes[session_name]
            return jsonify({"msg": f"Program {session_name} stopped"}), 200
        else:
            return jsonify({"msg": f"Program {session_name} is not running"}), 404

    def restart_program(self, session_name, phone_number, proxy):
        self.stop_program(session_name)
        return self.start_program(session_name, phone_number, proxy)
