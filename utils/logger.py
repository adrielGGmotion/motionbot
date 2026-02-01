import os
import datetime
import traceback

def log_error(error, command_name):
    now = datetime.datetime.now()
    date_dir = now.strftime("%Y-%m-%d")
    hour_file = now.strftime("%H-00.log")
    
    logs_dir = os.path.join("logs", date_dir)
    log_file_path = os.path.join(logs_dir, hour_file)
    
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)
        
    timestamp = now.isoformat()
    stack = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    
    log_entry = f"""
[{timestamp}] COMMAND: {command_name}
MESSAGE: {str(error)}
STACK: {stack}
--------------------------------------------------------------------------------
"""
    
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(log_entry)
        
    return log_file_path
