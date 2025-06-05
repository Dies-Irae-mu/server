from evennia.scripts.scripts import DefaultScript
from evennia.utils import logger
from world.state_reset import force_state_reset

class StateResetScript(DefaultScript):
    """
    Script for periodically resetting character states to prevent desync.
    """
    
    def at_script_creation(self):
        """Set up the script."""
        self.key = "state_reset_script"
        self.desc = "Resets character states periodically"
        self.interval = 30  # Run every 30 seconds
        self.persistent = True
        
    def at_repeat(self):
        """Called every self.interval seconds."""
        try:
            force_state_reset()
        except Exception as e:
            logger.log_err(f"Error in state reset script: {e}")

def start_state_reset_script():
    """
    Start the state reset script if it's not already running.
    Returns tuple: (success, message)
    """
    from evennia.scripts.models import ScriptDB
    
    # Check if script already exists
    existing = ScriptDB.objects.filter(db_key="state_reset_script")
    if existing:
        return False, "State reset script is already running."
        
    try:
        # Create and start the script
        script = StateResetScript()
        script.start()
        return True, "State reset script started successfully."
    except Exception as e:
        return False, f"Error starting state reset script: {e}"

def stop_state_reset_script():
    """
    Stop the state reset script if it's running.
    Returns tuple: (success, message)
    """
    from evennia.scripts.models import ScriptDB
    
    # Find and stop all instances
    scripts = ScriptDB.objects.filter(db_key="state_reset_script")
    if not scripts:
        return False, "No state reset script was running."
        
    try:
        for script in scripts:
            script.stop()
        return True, "State reset script stopped."
    except Exception as e:
        return False, f"Error stopping state reset script: {e}" 