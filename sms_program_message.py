import os

def start_program(session_name):
    os.system(f"screen -dmS {session_name} python {session_name}.py")

def stop_program(session_name):
    os.system(f"screen -S {session_name} -X quit")

def restart_program(session_name):
    stop_program(session_name)
    start_program(session_name)