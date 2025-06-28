from evennia import default_cmds
from evennia.utils import ansi
from commands.CmdPose import PoseBreakMixin
import re

class CmdEmit(PoseBreakMixin, default_cmds.MuxCommand):
    """
    @emit - Send a message to the room without your name attached.

    Usage:
      @emit <message>
      @emit/language <message>

    Switches:
      /language - Use this to emit a message in your set language.

    Examples:
      @emit A cool breeze blows through the room.
      @emit "~Bonjour, mes amis!" A voice calls out in French.
      @emit/language The entire message is in the set language.

    Use quotes with a leading tilde (~) for speech in your set language.
    This will be understood only by those who know the language.
    """

    key = "@emit"
    aliases = ["\\\\"]
    locks = "cmd:all()"
    help_category = "RP Commands"

    def process_special_characters(self, message):
        """
        Process %r and %t in the message, replacing them with appropriate ANSI codes.
        """
        message = message.replace('%r', '|/').replace('%t', '|-')
        return message

    def func(self):
        """Execute the @emit command"""
        caller = self.caller
        
        # Check if the room is a Quiet Room
        if hasattr(caller.location, 'db') and caller.location.db.roomtype == "Quiet Room":
            caller.msg("|rYou are in a Quiet Room and cannot emit messages.|n")
            return

        if not self.args:
            caller.msg("Usage: @emit <message>")
            return

        # Process special characters in the message
        processed_args = self.process_special_characters(self.args)

        # Check if there's a language-tagged speech and set speaking language
        if "~" in processed_args or 'language' in self.switches:
            speaking_language = caller.get_speaking_language()
            if not speaking_language:
                caller.msg("You need to set a speaking language first with +language <language>")
                return

        # Filter receivers based on reality layers
        filtered_receivers = []
        for obj in caller.location.contents:
            if not obj.has_account:
                continue
            
            # Check if they share the same reality layer
            if (caller.tags.get("in_umbra", category="state") and obj.tags.get("in_umbra", category="state")) or \
               (caller.tags.get("in_material", category="state") and obj.tags.get("in_material", category="state")) or \
               (caller.tags.get("in_dreaming", category="state") and obj.tags.get("in_dreaming", category="state")):
                filtered_receivers.append(obj)

        # Send pose break before the message
        self.send_pose_break()

        if 'language' in self.switches:
            # With /language switch, treat all quoted speech as being in the set language
            speaking_language = caller.get_speaking_language()
            
            for receiver in filtered_receivers:
                # Check for Universal Language merit
                has_universal = False
                if hasattr(receiver, 'db') and receiver.db.stats:
                    for category in receiver.db.stats.get('merits', {}).values():
                        if isinstance(category, dict):
                            for merit in category.keys():
                                if merit.lower().replace(' ', '') == 'universallanguage':
                                    has_universal = True
                                    break
                
                # Check if receiver understands the language
                understands_language = (receiver == caller or 
                                      has_universal or 
                                      (hasattr(receiver, 'get_languages') and 
                                       speaking_language in receiver.get_languages()))
                
                if understands_language:
                    # They understand - show original message
                    receiver.msg(processed_args)
                else:
                    # They don't understand - process quoted speech
                    message = processed_args
                    # Simple replacement of quoted text
                    import re
                    quote_pattern = r'"([^"]*)"'
                    def replace_quote(match):
                        return '"<< something in ' + speaking_language + ' >>"'
                    
                    processed_message = re.sub(quote_pattern, replace_quote, message)
                    receiver.msg(processed_message)
        else:
            # Handle mixed language content (original ~ system)
            for receiver in filtered_receivers:
                if "~" in processed_args:
                    parts = []
                    current_pos = 0
                    for match in re.finditer(r'"~([^"]+)"', processed_args):
                        # Add text before the speech
                        parts.append(processed_args[current_pos:match.start()])
                        
                        # Process the speech
                        speech = match.group(1)
                        
                        # Check for Universal Language merit
                        has_universal = any(
                            merit.lower().replace(' ', '') == 'universallanguage'
                            for category in receiver.db.stats.get('merits', {}).values()
                            for merit in category.keys()
                        )
                        
                        speaking_language = caller.get_speaking_language()
                        if receiver == caller or has_universal or (speaking_language and speaking_language in receiver.get_languages()):
                            _, msg_understand, _, _ = caller.prepare_say(speech, viewer=receiver, language_only=True, skip_english=True)
                            parts.append(f'"{msg_understand}"')
                        else:
                            _, _, msg_not_understand, _ = caller.prepare_say(speech, viewer=receiver, language_only=True, skip_english=True)
                            parts.append(f'"{msg_not_understand}"')
                        
                        current_pos = match.end()
                    
                    # Add any remaining text
                    parts.append(processed_args[current_pos:])
                    
                    # Send the final message
                    receiver.msg(''.join(parts))
                else:
                    # No language-tagged content, send as is
                    receiver.msg(processed_args)

        # Record scene activity
        caller.record_scene_activity()
