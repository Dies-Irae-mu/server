"""
Simple tests to verify the movement bug fix.

These tests verify that the problematic code patterns have been removed
from the movement commands without requiring full Evennia test setup.
"""

import os
import sys
import re

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_no_session_ndb_prod_location():
    """Test that session.ndb._prod_location assignments have been removed."""
    files_to_check = [
        'commands/CmdHangouts.py',
        'commands/communication.py'
    ]
    
    for file_path in files_to_check:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
                
            # Check for the problematic pattern
            pattern = r'session\.ndb\._prod_location'
            matches = re.findall(pattern, content)
            
            assert len(matches) == 0, (
                f"Found {len(matches)} instances of 'session.ndb._prod_location' "
                f"in {file_path}. These should have been removed."
            )
            print(f"✅ {file_path}: No session.ndb._prod_location found")


def test_no_manual_location_assignment_after_move_to():
    """Test that manual location assignments after move_to have been removed."""
    files_to_check = [
        'commands/CmdHangouts.py',
        'commands/communication.py'
    ]
    
    for file_path in files_to_check:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Look for move_to followed by location assignment
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'move_to(' in line and 'quiet=True' in line:
                    # Check the next few lines for manual location assignment
                    for j in range(i + 1, min(i + 5, len(lines))):
                        next_line = lines[j].strip()
                        if '.location =' in next_line and 'caller.location' in next_line:
                            assert False, (
                                f"Found manual location assignment after move_to "
                                f"in {file_path} at line {j + 1}: {next_line}"
                            )
            
            print(f"✅ {file_path}: No manual location assignments after move_to")


def test_move_to_usage_pattern():
    """Test that move_to is used with proper error handling."""
    files_to_check = [
        'commands/CmdHangouts.py',
        'commands/communication.py'
    ]
    
    move_to_found = False
    
    for file_path in files_to_check:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Look for proper move_to usage with if statement
            pattern = r'if\s+.*\.move_to\([^)]+quiet=True\)'
            matches = re.findall(pattern, content)
            
            if matches:
                move_to_found = True
                print(f"✅ {file_path}: Found {len(matches)} proper move_to usage patterns")
    
    assert move_to_found, "No proper move_to usage patterns found"


def test_hangout_jump_command_structure():
    """Test that hangout jump command has proper structure."""
    file_path = 'commands/CmdHangouts.py'
    full_path = os.path.join(project_root, file_path)
    
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Check that jump functionality exists
        assert 'def func(self):' in content, "func method not found"
        assert '"jump"' in content or "'jump'" in content, "jump switch not found"
        
        # Check for proper messaging
        assert 'msg_contents' in content, "Room messaging not found"
        
        print(f"✅ {file_path}: Hangout jump command structure looks correct")


def test_ic_command_structure():
    """Test that +ic command has proper structure."""
    file_path = 'commands/communication.py'
    full_path = os.path.join(project_root, file_path)
    
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Check for IC command class
        assert 'class CmdPlusIc' in content, "CmdPlusIc class not found"
        
        # Check for proper pre_ooc_location handling
        assert 'pre_ooc_location' in content, "pre_ooc_location handling not found"
        
        print(f"✅ {file_path}: +ic command structure looks correct")


def run_all_tests():
    """Run all tests."""
    print("Running Movement Bug Fix Verification Tests")
    print("=" * 50)
    
    tests = [
        test_no_session_ndb_prod_location,
        test_no_manual_location_assignment_after_move_to,
        test_move_to_usage_pattern,
        test_hangout_jump_command_structure,
        test_ic_command_structure,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    
    if failed == 0:
        print("🎉 All tests passed! The movement bug fix looks good.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 