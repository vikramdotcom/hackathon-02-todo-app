#!/usr/bin/env python3
"""
Test email validation to ensure it works correctly at the application layer.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.user import User
from pydantic import ValidationError


def test_email_validation():
    """Test email validation with various inputs."""
    print("[*] Testing email validation...")
    print()

    test_cases = [
        ("valid@email.com", True, "Valid standard email"),
        ("user@domain.co.uk", True, "Valid email with country TLD"),
        ("test.user+tag@example.com", True, "Valid email with plus and dot"),
        ("invalid-email", False, "Missing @ symbol"),
        ("test@", False, "Missing domain"),
        ("@domain.com", False, "Missing local part"),
        ("test@test", False, "Missing TLD"),
        ("", False, "Empty email"),
        ("spaces in@email.com", False, "Spaces in email"),
    ]

    passed = 0
    failed = 0

    for email, should_pass, description in test_cases:
        try:
            result = User.validate_email(email)
            if should_pass:
                print(f"[+] PASS: {description}")
                print(f"    Input: '{email}' -> Output: '{result}'")
                passed += 1
            else:
                print(f"[-] FAIL: {description}")
                print(f"    Expected validation error but got: '{result}'")
                failed += 1
        except (ValueError, ValidationError) as e:
            if not should_pass:
                print(f"[+] PASS: {description}")
                print(f"    Input: '{email}' -> Error: {str(e)}")
                passed += 1
            else:
                print(f"[-] FAIL: {description}")
                print(f"    Expected valid but got error: {str(e)}")
                failed += 1
        print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = test_email_validation()
    sys.exit(0 if success else 1)
