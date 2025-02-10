def validate_password(password):
    """Validates a password based on security rules."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one digit")
    if not any(char.isupper() for char in password):
        raise ValueError("Password must contain at least one capital letter")
    if not any(char.islower() for char in password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not any(char in "!@#$%^&*()-_=+" for char in password):
        raise ValueError("Password must contain at least one special character")
    return True


def validate_email(email):
    """Validates an email address format using basic string checks."""
    
    # Check if '@' is present and not at the start or end
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise ValueError("Invalid email format: missing or misplaced '@' symbol.")
    
    local_part, domain_part = email.split("@", 1)
    
    # Ensure domain contains at least one dot and it's not at the start or end
    if "." not in domain_part or domain_part.startswith(".") or domain_part.endswith("."):
        raise ValueError("Invalid email format: domain must contain a valid '.' character.")
    
    return True


# Testing the validation functions
try:
    validate_password("WeakPass")
except ValueError as e:
    print(f"Invalid password: {e}")

try:
    validate_email("invalidemail.com")
except ValueError as e:
    print(f"Invalid email: {e}")

try:
    validate_email("test@domain")
except ValueError as e:
    print(f"Invalid email: {e}")

try:
    validate_email("@domain.com")
except ValueError as e:
    print(f"Invalid email: {e}")

try:
    validate_email("valid.email@example.com")
    print("Valid email!")
except ValueError as e:
    print(f"Invalid email: {e}")
