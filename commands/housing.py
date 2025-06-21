"""
Hangouts system for listing and managing hangout locations.
"""

from evennia import Command, CmdSet
from evennia.utils.evtable import EvTable
from evennia.utils.utils import list_to_string
from world.hangouts.models import HangoutDB, HANGOUT_CATEGORIES
from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils import search

class CmdHangout(MuxCommand):
    """
    View and manage hangout locations.

    Usage:
        +hangout[/all]
        +hangout/type [<category>]
        +hangout <number>
        +hangout[/jump /tel /join /visit] <number>

        Staff/Builder Commands:
        +hangout/create <name>
        +hangout/setroom <#>=<room dbref or 'here'>
        +hangout/setdesc <#>=<description>
        +hangout/settype <#>=<category>
        +hangout/setdistrict <#>=<district name>
        +hangout/setsplat <#>=<splat type>
        +hangout/delete <#>
        +hangout/hidden <#>=<yes/no>

    The +hangout command allows you to view a list of hangout spots and landmarks 
    in the reality your character is currently in.

    Switches:
        /all        - Show all hangouts you have access to see
        /type       - List hangouts by category or show available categories
        /jump       - Teleport to the specified hangout (OOC convenience)
        /tel        - Alias for /jump
        /join       - Alias for /jump
        /visit      - Alias for /jump

        Staff Only:
        /create     - Create a new hangout
        /setroom    - Set the room location for a hangout
        /setdesc    - Set the description for a hangout
        /settype    - Set the category for a hangout
        /setdistrict - Set the district for a hangout
        /setsplat   - Set splat requirements for a hangout
        /delete     - Delete a hangout
        /hidden     - Set whether the hangout is hidden from non-splat members

    Examples:
        +hangout            - Show hangouts with active visitors
        +hangout/all       - Show all hangouts you can access
        +hangout/type      - List all available categories
        +hangout/type Club - Show all Club category hangouts
        +hangout 42        - View detailed info about hangout #42
        +hangout/jump 42   - Teleport to hangout #42
        
        Staff Examples:
        +hangout/create The Perils
        +hangout/setroom 42=here
        +hangout/setdesc 42=A dark and moody fetish club.
        +hangout/settype 42=Club
        +hangout/setdistrict 42=Downtown
        +hangout/setsplat 42=Mage
        +hangout/hidden 42=yes
    """
    
    key = "+hangout"
    aliases = ["+hangouts", "+hotspot", "+hotspots",
              "+dir", "+directory", "+yp", "+yellowpages"]
    help_category = "RP Commands"
    
    def _check_staff_perms(self):
        """Check if the caller has staff permissions."""
        return self.caller.check_permstring("builders") or self.caller.check_permstring("wizards")

    def _has_splat_access(self, hangout):
        """Check if the caller has access to the splat-restricted hangout."""
        # If the hangout isn't hidden, everyone has access regardless of splat
        if not hangout.db.hidden:
            return True
            
        # Staff always have access
        if self._check_staff_perms():
            return True
            
        # If hidden but no splat requirements, everyone has access
        if not hangout.db.required_splats:
            return True
            
        # Get character's splat from the stats structure
        try:
            stats = self.caller.db.stats
            if stats and 'other' in stats:
                if 'splat' in stats['other']:
                    if 'Splat' in stats['other']['splat']:
                        character_splat = stats['other']['splat']['Splat']['perm']
                    else:
                        character_splat = None
                else:
                    character_splat = None
            else:
                character_splat = None
        except (AttributeError, KeyError, TypeError):
            character_splat = None
            
        if not character_splat:
            return False
            
        # Check if the character's splat matches any required splat
        return character_splat in hangout.db.required_splats

    def _get_hangout_by_id(self, hangout_id):
        """Get a hangout by ID, with staff override for visibility."""
        try:
            hangout_id = int(hangout_id)
            if self._check_staff_perms():
                return HangoutDB.get_by_hangout_id(hangout_id)
            else:
                hangouts = HangoutDB.get_visible_hangouts(self.caller)
                return next((h for h in hangouts if h.db.hangout_id == hangout_id), None)
        except (ValueError, TypeError):
            return None

    def _format_header(self, text):
        """Format a header with custom borders."""
        width = 78
        return f"{'|b=|n' * width}\n {text}\n{'|b=|n' * width}"

    def _format_separator(self):
        """Format a section separator."""
        return "|b-|n" * 78

    def _display_hangout_details(self, hangout):
        """Create a detailed display for a single hangout."""
        if not hangout:
            self.caller.msg("Hangout not found.")
            return
            
        # Check splat access for viewing details only if hangout is hidden
        if hangout.db.hidden and hangout.db.required_splats and not self._has_splat_access(hangout):
            self.caller.msg("You do not have access to view this hangout.")
            return

        # Get access requirements
        access_tags = []
        if hangout.db.required_splats:
            access_tags.extend(hangout.db.required_splats)
        if hangout.db.required_merits:
            access_tags.extend(hangout.db.required_merits)
        if hangout.db.required_factions:
            access_tags.extend(hangout.db.required_factions)
        
        access_display = "All" if not access_tags else ", ".join(access_tags)

        # Header
        self.caller.msg(self._format_header(f"Hangout {hangout.db.hangout_id}"))
        
        # Info section with custom formatting
        self.caller.msg("|wName:|n " + hangout.key)
        self.caller.msg("|wDistrict:|n " + hangout.db.district)
        self.caller.msg("|wCategory:|n " + hangout.db.category)
        self.caller.msg("|wAccess Tags:|n " + access_display)
        
        # Description section
        self.caller.msg(self._format_separator())
        self.caller.msg("|yDescription|n")
        self.caller.msg(hangout.db.description)
        self.caller.msg(self._format_separator())

    def _display_hangout_list(self, hangouts, show_all=False):
        """Create a formatted list of hangouts."""
        if not hangouts:
            self.caller.msg("No hangouts found.")
            return

        # Group hangouts by district
        district_groups = {}
        for h in hangouts:
            # Skip if hangout is hidden and user doesn't have splat access
            if h.db.hidden and h.db.required_splats and not self._has_splat_access(h):
                continue
                
            # Ensure hangout has an ID before displaying
            if h.db.hangout_id is None:
                h.attributes.add("hangout_id", HangoutDB._get_next_hangout_id())
            
            # Check if the hangout has players before adding to district group
            room = h.db.room
            player_count = len([obj for obj in room.contents if obj.has_account]) if room else 0
            
            if show_all or player_count > 0:
                district = h.db.district or "Uncategorized"
                if district not in district_groups:
                    district_groups[district] = []
                district_groups[district].append((h, player_count))

        # If no hangouts to display
        if not district_groups:
            self.caller.msg("No active hangouts found.")
            return

        # Header
        self.caller.msg(self._format_header("Hangouts"))
        
        # Header row - custom formatting
        self.caller.msg("|w  # | Info" + "Players".rjust(55) + "|n")

        # Display each district group
        for district in sorted(district_groups.keys()):
            # District separator
            self.caller.msg(self._format_separator())
            self.caller.msg(f"|w{district}|n")
            
            # Display hangouts in this district, sorted by hangout_id
            district_hangouts = sorted(district_groups[district], key=lambda x: x[0].db.hangout_id)
            for hangout, player_count in district_hangouts:
                number, info_line, desc_line = hangout.get_display_entry(show_restricted=True)
                
                # Format the hangout ID to be right-aligned in 3 spaces
                formatted_id = str(hangout.db.hangout_id).rjust(3)
                self.caller.msg(f"{formatted_id} | {info_line}")
                self.caller.msg(desc_line)

        # Footer with help text
        self.caller.msg(self._format_separator())
        self.caller.msg("|w* = Hidden Hangout|n")
        self.caller.msg("|y+hangouts/all - show all hangouts|n")
        self.caller.msg("|y+hangouts/type <category> - show all hangouts of a certain category|n")
        self.caller.msg("|y+hangouts/type - show all hangouts separated by category|n")
        self.caller.msg(self._format_separator())
        # Add categories list
        self.caller.msg("|yCategories are:|n " + ", ".join(sorted(HANGOUT_CATEGORIES)))
        self.caller.msg("|b=" * 78)

    def func(self):
        """Execute the hangout command."""
        
        # Check if the room is a Quiet Room
        if hasattr(self.caller.location, 'db') and self.caller.location.db.roomtype == "Quiet Room":
            self.caller.msg("|rYou cannot use the +hangout command from a Quiet Room.|n")
            return
            
        # Check if the room is an RP Room
        if hasattr(self.caller.location, 'db') and self.caller.location.db.roomtype and "RP Room" in self.caller.location.db.roomtype:
            self.caller.msg("|rYou cannot use the +hangout command from an RP Room. Please return to the grid first.|n")
            return
        
        # Basic +hangout command - show active hangouts
        if not self.args and not self.switches:
            hangouts = HangoutDB.get_visible_hangouts(self.caller)
            self._display_hangout_list(hangouts, show_all=False)
            return

        # Handle non-staff switches first
        if "all" in self.switches:
            # Show all hangouts, including empty ones
            hangouts = HangoutDB.get_visible_hangouts(self.caller)
            self._display_hangout_list(hangouts, show_all=True)
            return

        if "type" in self.switches:
            if not self.args:
                # Display available categories
                self.caller.msg("Available Categories:")
                self.caller.msg(", ".join(sorted(HANGOUT_CATEGORIES)))
                return
                
            category = self.args.strip().title()
            if category not in HANGOUT_CATEGORIES:
                self.caller.msg(f"Invalid category. Valid categories are: {', '.join(HANGOUT_CATEGORIES)}")
                return
                
            hangouts = HangoutDB.get_hangouts_by_category(category, self.caller)
            self._display_hangout_list(hangouts, show_all=True)
            return

        # Handle teleport switches
        if any(switch in ["jump", "tel", "join", "visit"] for switch in self.switches):
            try:
                # Check if player is in an OOC area
                current_location = self.caller.location
                if current_location and hasattr(current_location, 'db') and current_location.db.roomtype == "OOC Area":
                    self.caller.msg("You cannot teleport directly from the OOC area. Use +ic first to return to IC areas.")
                    return
                # Check if player is in an RP Room
                if current_location and hasattr(current_location, 'db') and current_location.db.roomtype and "RP Room" in current_location.db.roomtype:
                    self.caller.msg("|rYou cannot teleport from an RP Room using +hangout. Please return to the grid first.|n")
                    return
                    
                hangout_id = int(self.args)
                hangouts = HangoutDB.get_visible_hangouts(self.caller)
                hangout = next((h for h in hangouts if h.db.hangout_id == hangout_id), None)
                
                if not hangout:
                    self.caller.msg("That hangout was not found or is not accessible.")
                    return
                
                # Check splat requirements for teleporting only if hangout is hidden
                if hangout.db.hidden and hangout.db.required_splats and not self._has_splat_access(hangout):
                    self.caller.msg("You do not have the required splat type to access this location.")
                    return
                    
                room = hangout.db.room
                if not room:
                    self.caller.msg("That hangout's location is not properly set up.")
                    return
                
                # Store the current location before moving
                old_location = self.caller.location
                
                # Announce departure to the old room
                old_location.msg_contents(f"{self.caller.name} has left for hangout {hangout_id}.")
                    
                # Ensure all sessions know we're moving to prevent ghosts
                for session in self.caller.sessions.all():
                    if session:
                        session.msg(text=f"Moving to {hangout.key}...")
                
                # Move the character
                if self.caller.move_to(room, quiet=True):
                    # Force location refresh for everyone in the room
                    for obj in room.contents:
                        if obj.has_account:
                            obj.location = room  # Force location refresh
                    
                    # Send explicit messages to force session synchronization
                    for obj in room.contents:
                        if obj.has_account and obj != self.caller:
                            # Message other players about the arrival
                            obj.msg(f"{self.caller.name} has arrived.")
                            # Message the teleporter about seeing the other player
                            self.caller.msg(f"You see {obj.name} here.")
                    
                    # Announce arrival to the new room
                    room.msg_contents(f"{self.caller.name} has arrived.", exclude=self.caller)
                    
                    # Message to the character
                    self.caller.msg(f"You teleport to {hangout.key}.")
                    
                    # Force the character to look around
                    self.caller.execute_cmd("look")
                else:
                    self.caller.msg("Failed to teleport to the hangout.")
                
                return
                
            except ValueError:
                self.caller.msg("Please specify a valid hangout number.")
                return
        
        # Staff/Builder commands
        if self.switches and self._check_staff_perms():
            if "create" in self.switches:
                if not self.args:
                    self.caller.msg("Usage: +hangout/create <name>")
                    return
                    
                name = self.args.strip()
                hangout = HangoutDB.create(
                    key=name,
                    room=None,
                    category="Uncategorized",
                    district="Unassigned",
                    description="No description set."
                )
                self.caller.msg(f"Created hangout #{hangout.db.hangout_id}: {name}")
                return

            # All other staff commands require a hangout ID
            if not self.args or "=" not in self.args:
                self.caller.msg("Usage: +hangout/<switch> <#>=<value>")
                return

            hangout_id, value = self.args.split("=", 1)
            hangout = self._get_hangout_by_id(hangout_id)
            
            if not hangout:
                self.caller.msg("Invalid hangout ID.")
                return

            if "setroom" in self.switches:
                if value.lower() == "here":
                    room = self.caller.location
                else:
                    room = search.search_object(value)
                    if not room or len(room) != 1:
                        self.caller.msg("Room not found.")
                        return
                    room = room[0]
                
                hangout.db.room = room
                self.caller.msg(f"Set room for hangout #{hangout.db.hangout_id} to {room}")
                
            elif "setdesc" in self.switches:
                hangout.db.description = value
                self.caller.msg(f"Updated description for hangout #{hangout.db.hangout_id}")
                
            elif "settype" in self.switches:
                category = value.strip().title()
                if category not in HANGOUT_CATEGORIES:
                    self.caller.msg(f"Invalid category. Valid categories are: {', '.join(HANGOUT_CATEGORIES)}")
                    return
                    
                hangout.db.category = category
                self.caller.msg(f"Set category for hangout #{hangout.db.hangout_id} to {category}")
                
            elif "setdistrict" in self.switches:
                hangout.db.district = value.strip()
                self.caller.msg(f"Set district for hangout #{hangout.db.hangout_id} to {value}")
                
            elif "setsplat" in self.switches:
                if not value.strip():
                    hangout.db.required_splats = []
                    self.caller.msg(f"Removed splat requirements for hangout #{hangout.db.hangout_id}")
                else:
                    hangout.db.required_splats = [value.strip()]
                    self.caller.msg(f"Set splat requirement for hangout #{hangout.db.hangout_id} to {value}")
                
            elif "hidden" in self.switches:
                hidden = value.lower() in ("yes", "true", "1")
                hangout.db.hidden = hidden
                self.caller.msg(f"Set hidden status for hangout #{hangout.db.hangout_id} to {hidden}")
                
            elif "delete" in self.switches:
                if value.lower() != "yes":
                    self.caller.msg("To delete, use: +hangout/delete <#>=yes")
                    return
                    
                name = hangout.key
                hangout.delete()
                self.caller.msg(f"Deleted hangout: {name}")
                
            return

        # Handle viewing a specific hangout (no switches)
        try:
            hangout_id = int(self.args)
            hangouts = HangoutDB.get_visible_hangouts(self.caller)
            hangout = next((h for h in hangouts if h.db.hangout_id == hangout_id), None)
            
            if not hangout:
                self.caller.msg("That hangout was not found or is not accessible.")
                return
                
            self._display_hangout_details(hangout)
            
        except ValueError:
            self.caller.msg("Please specify a valid hangout number.")

class CmdVacate(MuxCommand):
    """
    Vacate your residence or force vacate another's residence (staff only).
    
    Usage:
        +vacate              - Vacate your residence in current building
        +vacate/all         - List all your residences
        +vacate <number>    - Vacate specific residence (if you own it)
        +vacate/force <number> - Force vacate a residence (staff only)
    """
    
    key = "+vacate"
    locks = "cmd:all()"
    help_category = "Building and Housing"
    
    def find_residence(self, residence_number=None):
        """Helper method to find building containing player's residence."""
        # Search all rooms for housing data
        for room in ObjectDB.objects.filter(db_typeclass_path__contains="rooms.Room"):
            if room.is_housing_area():
                tenants = room.db.housing_data.get('current_tenants', {})
                for res_id, tenant_id in tenants.items():
                    if tenant_id == self.caller.id:
                        try:
                            residence = ObjectDB.objects.get(id=res_id)
                            if residence_number is None or residence.key.endswith(str(residence_number)):
                                return room, residence
                        except ObjectDB.DoesNotExist:
                            continue
        return None, None

    def is_owner(self, room, player):
        """Check if a player owns a residence."""
        if not room or not player or not hasattr(room, 'db'):
            return False

        # Check home_data first
        home_data = room.db.home_data if hasattr(room.db, 'home_data') else None
        if home_data:
            if home_data.get('owner') and home_data['owner'].id == player.id:
                return True
            if player.id in home_data.get('co_owners', set()):
                return True
            
        # Check housing_data next
        housing_data = room.db.housing_data if hasattr(room.db, 'housing_data') else None
        if housing_data:
            if housing_data.get('owner'):
                if housing_data['owner'].id == player.id:
                    return True
            
            if housing_data.get('current_tenants'):
                if str(room.id) in housing_data['current_tenants'] and housing_data['current_tenants'][str(room.id)] == player.id:
                    return True
            
        # Finally check legacy owner
        if hasattr(room.db, 'owner') and room.db.owner:
            if room.db.owner.id == player.id:
                return True
            
        return False

    def func(self):
        from evennia.objects.models import ObjectDB
        from evennia.utils import evtable
        
        if "all" in self.switches:
            # List all residences owned by player
            residences = []
            for room in ObjectDB.objects.filter(db_typeclass_path__contains="rooms.Room"):
                if room.is_housing_area():
                    tenants = room.db.housing_data.get('current_tenants', {})
                    for res_id, tenant_id in tenants.items():
                        if tenant_id == self.caller.id:
                            try:
                                residence = ObjectDB.objects.get(id=res_id)
                                residences.append((room, residence))
                            except ObjectDB.DoesNotExist:
                                continue
            
            if not residences:
                self.caller.msg("You don't own any residences.")
                return
                
            table = evtable.EvTable("|wResidence|n", "|wLocation|n", "|wType|n", border="table")
            for area, residence in residences:
                table.add_row(
                    residence.get_display_name(self.caller),
                    area.get_display_name(self.caller),
                    residence.db.roomtype.title()
                )
            self.caller.msg(table)
            return

        if "force" in self.switches:
            if not self.caller.check_permstring("builders"):
                self.caller.msg("You don't have permission to force vacate residences.")
                return
                
            if not self.args:
                self.caller.msg("Please specify a residence number to force vacate.")
                return
                
            building, residence = self.find_residence(self.args)
            if not residence:
                self.caller.msg("Residence not found.")
                return
        else:
            # Normal vacate
            if self.args:
                building, residence = self.find_residence(self.args)
                if not residence:
                    self.caller.msg("You don't own that residence.")
                    return
            else:
                # Try to vacate current location
                location = self.caller.location
                if not (location.db.roomtype and 
                        any(rtype.lower() in location.db.roomtype.lower() 
                            for rtype in ["apartment", "house", "splat_housing", "studio", "room", "encampment"]) and 
                        self.is_owner(location, self.caller)):
                    self.caller.msg("You must be in your residence to vacate it.")
                    return
                    
                # Find the building
                for exit in location.exits:
                    if exit.key == "Out":
                        building = exit.destination
                        residence = location
                        break
                else:
                    self.caller.msg("Error finding building. Please contact staff.")
                    return

        # Perform the vacate
        if residence.db.owner != self.caller and not self.caller.check_permstring("builders"):
            self.caller.msg("You don't own this residence.")
            return
            
        # Move any occupants to the building
        for obj in residence.contents:
            if obj.has_account:
                obj.msg("This residence is being vacated. You are being moved out.")
                
                # Session synchronization for vacate moves
                for session in obj.sessions.all():
                    if session:
                        session.msg(text=f"Being moved out as residence is being vacated...")
                
                if obj.move_to(building, quiet=True):
                    obj.location = building
                    obj.execute_cmd("look")
                
        # Clean up child rooms if they exist
        if hasattr(residence.db, 'child_rooms'):
            for room in residence.db.child_rooms:
                if room:
                    for obj in room.contents:
                        if obj.has_account:
                            for session in obj.sessions.all():
                                if session:
                                    session.msg(text=f"Being moved out as residence is being vacated...")
                            
                            if obj.move_to(building, quiet=True):
                                obj.location = building
                                obj.execute_cmd("look")
                    # Delete all exits in the child room
                    for exit in room.exits:
                        exit.delete()
                    room.delete()

        # Update building data
        if building and building.db.housing_data:
            if residence.id in building.db.housing_data['current_tenants']:
                del building.db.housing_data['current_tenants'][residence.id]
            # Handle apartment numbers for both numeric and string values
            try:
                number = int(residence.key.split()[-1])
                if number in building.db.housing_data['apartment_numbers']:
                    building.db.housing_data['apartment_numbers'].remove(number)
            except (ValueError, IndexError):
                # If it's not a numeric apartment number, try to remove the full name
                if residence.key in building.db.housing_data['apartment_numbers']:
                    building.db.housing_data['apartment_numbers'].remove(residence.key)
        
        # Clear home location if this was their home
        if self.caller.home == residence:
            self.caller.home = None
            self.caller.msg("Your home location has been cleared.")
            
        # Delete all exits in the main residence
        for exit in residence.exits:
            exit.delete()
            
        # Delete the entrance exit from the building
        for exit in building.contents:
            if (hasattr(exit, 'destination') and 
                exit.destination == residence):
                exit.delete()
            
        # Delete the residence
        residence.delete()
        self.caller.msg("You have vacated the residence.")
