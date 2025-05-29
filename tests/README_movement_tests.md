# Movement Bug Fix Tests

This directory contains tests for the movement command bug fix that resolved visibility/ghosting issues with the `+ic` and `+hangout/jump` commands.

## Bug Description

The original bug occurred when players used the sequence:
1. `+ic` (to return from OOC to IC areas)
2. `+hangout/jump <number>` (to teleport to a hangout)

This would cause players to become invisible or "ghosted" - they would appear to be in multiple locations or not visible to other players.

## Root Cause

The bug was caused by manual manipulation of session location data after `move_to()` calls:
- Commands were calling `move_to(location, quiet=True)`
- Then manually setting `caller.location = location` (redundant)
- Then setting `session.ndb._prod_location = location` (causing desync)

## Fix

The fix removes all manual location assignments and session manipulation, letting Evennia's built-in `move_to()` method handle all location updates properly.

## Test Files

### test_movement_simple.py ✅ WORKING
Simple verification tests that check the code changes without requiring full Evennia setup:

- **test_no_session_ndb_prod_location**: Verifies all `session.ndb._prod_location` assignments removed
- **test_no_manual_location_assignment_after_move_to**: Verifies no manual location assignments after `move_to()`
- **test_move_to_usage_pattern**: Verifies proper `move_to()` usage with error handling
- **test_hangout_jump_command_structure**: Verifies hangout command structure
- **test_ic_command_structure**: Verifies +ic command structure

### test_movement_bug_fix.py ⚠️ COMPLEX
Comprehensive Evennia integration tests (requires complex setup):
- Full character and room object testing
- Session handling verification
- Complete movement flow testing
- *Note: Requires proper Evennia test environment setup*

## Running the Tests

### Option 1: Using the test runner (Recommended)
```bash
python run_movement_tests.py
```

### Option 2: Using pytest directly on simple tests
```bash
pytest tests/test_movement_simple.py -v
```

### Option 3: Running simple tests directly
```bash
python tests/test_movement_simple.py
```

## Test Results

The simple verification tests confirm:
- ✅ No `session.ndb._prod_location` assignments found
- ✅ No manual location assignments after `move_to()` calls
- ✅ Proper `move_to()` usage patterns implemented
- ✅ Command structure integrity maintained

## Commands Fixed

The following commands were fixed and are verified:
- `+ic` - Return to IC from OOC
- `+ooc` - Move to OOC area  
- `+hangout/jump` - Teleport to hangout
- `+meet/accept` - Accept meet request and teleport
- `+summon` - Admin command to summon players
- `+join` - Admin command to join players

## Key Verification Points

1. **No Session Artifacts**: All `session.ndb._prod_location` manipulation removed
2. **Proper move_to Usage**: All movement uses `if caller.move_to(location, quiet=True):`
3. **No Manual Location Assignment**: No redundant `caller.location = location` after `move_to()`
4. **Error Handling**: Failed moves are handled gracefully
5. **Command Structure**: All commands maintain their expected functionality

## Expected Results

All simple tests should pass, indicating:
- 🎉 The specific bug sequence is fixed
- 🎉 No problematic code patterns remain
- 🎉 Commands follow proper Evennia movement patterns
- 🎉 The fix is implemented correctly 