import subprocess
import time
import os
import signal
from pathlib import Path
import json

def main():
    target_script = "repro/scripts/chaos_interrupt_target.py"
    file_path = Path("tmp_interrupt.json")
    if file_path.exists():
        file_path.unlink()
    
    print("Starting target script...")
    proc = subprocess.Popen(["python3", target_script])
    
    time.sleep(0.5) # Let it run for a bit
    
    print(f"Killing process {proc.pid} with SIGKILL...")
    proc.kill() # SIGKILL
    proc.wait()
    
    if file_path.exists():
        try:
            content = file_path.read_text()
            data = json.loads(content)
            print("File is valid JSON.")
            if len(data.get("items", [])) == 10000:
                print("Data integrity preserved.")
            else:
                print(f"Data mismatch: found {len(data.get('items', []))} items.")
        except json.JSONDecodeError as e:
            print(f"CORRUPTION DETECTED! {e}")
            print(f"File content start: {content[:100]}...")
            print(f"File content end: {content[-100:]}...")
    else:
        print("File was never created.")

if __name__ == "__main__":
    main()
