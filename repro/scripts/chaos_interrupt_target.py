import time
import os
import tempfile
from pathlib import Path
import json

def save_atomic(file_path, data):
    with tempfile.NamedTemporaryFile("w", dir=file_path.parent, delete=False) as tf:
        tf.write(json.dumps(data, indent=4))
        tf.flush()
        os.fsync(tf.fileno()) # Ensure it's on disk
        temp_name = tf.name
    os.replace(temp_name, file_path)

def main():
    file_path = Path("tmp_interrupt.json")
    data = {"items": ["item"] * 10000} # Make it a bit large to increase window
    while True:
        save_atomic(file_path, data)
        # We want to spend as much time as possible in the "atomic" part or just loop fast
        # No sleep to maximize window

if __name__ == "__main__":
    main()
