import subprocess
import time

def run_script_every_5_seconds(script_path):
    while True:
        print("Running script...")
        try:
            subprocess.run(["python", script_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")
        time.sleep(5)  # Wait for 5 seconds before running the script again

# Replace 'path/to/your/script.py' with the path to the Python script you want to run
run_script_every_5_seconds('test-notebook.py')

