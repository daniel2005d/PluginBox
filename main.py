import os
import sys
import importlib


TASKS_DIR = "tasks"

def list_tasks():
    """Lists all available Python scripts in the tasks directory."""
    if not os.path.exists(TASKS_DIR):
        print(f"[-] Error: '{TASKS_DIR}' directory not found.")
        return []
    
    # Get all .py files except __init__.py
    files = os.listdir(TASKS_DIR)
    tasks = [f[:-3] for f in files if f.endswith(".py") and f != "__init__.py"]
    return tasks

def main():
    
    tasks = list_tasks()
    
    if len(sys.argv) < 2:
        print("[-] Usage: python main.py <script_name> [arguments]")
        print("\nAvailable scripts:")
        for task in tasks:
            print(f"  - {task}")
        sys.exit(1)
        
    target_task = sys.argv[1]
    task_args = sys.argv[2:] # Arguments meant for the specific script

    if target_task not in tasks:
        print(f"[-] Error: Script '{target_task}' not found in '{TASKS_DIR}' folder.")
        sys.exit(1)

    try:
        # Dynamically import the selected module
        module = importlib.import_module(f"{TASKS_DIR}.{target_task}")
        
        # Every script must implement a standard run(args) function
        if hasattr(module, "run"):
            module.run(task_args)
        else:
            print(f"[-] Error: Script '{target_task}' does not have a 'run(args)' function.")
            
    except Exception as e:
        print(f"[-] Execution failed: {e}")

if __name__ == "__main__":
    main()