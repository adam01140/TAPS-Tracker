import multiprocessing
import subprocess

# List of script file names
scripts = ["366.py", "377.py", "388.py", "399.py", "400.py"]

def run_script(script):
    try:
        subprocess.run(["python", script], check=True)
    except subprocess.CalledProcessError:
        print(f"Error running {script}")

if __name__ == "__main__":
    # Create a process for each script
    processes = [multiprocessing.Process(target=run_script, args=(script,)) for script in scripts]

    # Start all processes
    for process in processes:
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()
