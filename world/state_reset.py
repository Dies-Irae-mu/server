from evennia.utils import logger
from evennia.utils.search import search_object
from typeclasses.characters import Character

def force_state_reset():
    """
    Force a state reset on all eligible characters.
    This simulates an OOC/IC and unpuppet/puppet cycle.
    """
    # Get all characters
    characters = search_object("", typeclass=Character)
    
    for char in characters:
        try:
            # Skip if not approved
            if not (char.tags.has("approved", category="approval") or char.db.approved):
                continue
                
            # Skip if no account or sessions
            if not char.has_account or not char.sessions.count():
                continue
                
            # Skip if in OOC Area
            if hasattr(char.location, 'db') and char.location.db.roomtype == "OOC Area":
                continue
                
            # Store current location
            current_location = char.location
            if not current_location:
                continue
                
            # Get account and session
            account = char.account
            if not account:
                continue
                
            session = char.sessions.get()[0] if char.sessions.count() else None
            if not session:
                continue
                
            logger.log_info(f"Resetting state for {char.name}")
            
            # Store location
            char.db.pre_reset_location = current_location
            
            # Unpuppet
            try:
                account.unpuppet_object(session)
            except Exception as e:
                logger.log_err(f"Error unpuppeting {char.name}: {e}")
                continue
                
            # Re-puppet
            try:
                account.puppet_object(session, char)
            except Exception as e:
                logger.log_err(f"Error puppeting {char.name}: {e}")
                # Try to restore location at least
                char.location = current_location
                continue
                
            # Ensure location is correct
            if char.location != current_location:
                char.location = current_location
                
            # Clean up
            char.attributes.remove("pre_reset_location")
            
        except Exception as e:
            logger.log_err(f"Error resetting {char.name}: {e}")
            continue 