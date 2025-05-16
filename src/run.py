#?attr ENGINE

import threading
import subprocess
import sys
import time

from engine.core.builder import *



builder = Builder("./build", "./packaged", ["./src"], ["./src", "./res"])

builder.clear_build()
builder.build(BuildType.ENGINE_SERVER)
builder.build(BuildType.ENGINE_CLIENT)


def run_server():
    subprocess.run(["python", "packaged/server/src/main.py"])


def run_client():
    subprocess.run(["python", "packaged/client/src/main.py"])


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    time.sleep(0.5)

    run_client()

    server_thread.join()

    if "-b" in sys.argv:
        builder.build(BuildType.SERVER)
        builder.build(BuildType.CLIENT)


