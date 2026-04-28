"""Error codes and messages for API responses and user feedback."""


class AuthError:
    """Authentication error codes and messages."""

    # ═══════════════════════════════════════════════════════════════
    # Validation Errors (400 Bad Request)
    # ═══════════════════════════════════════════════════════════════

    USERNAME_TOO_SHORT = {
        "code": "USERNAME_TOO_SHORT",
        "status": 400,
        "message": "Username must be at least 3 characters long",
    }

    USERNAME_INVALID_FORMAT = {
        "code": "USERNAME_INVALID_FORMAT",
        "status": 400,
        "message": "Username must contain only letters, numbers, and underscores",
    }

    INVALID_EMAIL = {
        "code": "INVALID_EMAIL",
        "status": 400,
        "message": "Valid email address is required",
    }

    PASSWORD_TOO_SHORT = {
        "code": "PASSWORD_TOO_SHORT",
        "status": 400,
        "message": "Password must be at least 6 characters long",
    }

    PASSWORDS_MISMATCH = {
        "code": "PASSWORDS_MISMATCH",
        "status": 400,
        "message": "Passwords do not match",
    }

    MISSING_CREDENTIALS = {
        "code": "MISSING_CREDENTIALS",
        "status": 400,
        "message": "Username and password are required",
    }

    MISSING_REQUIRED_FIELDS = {
        "code": "MISSING_REQUIRED_FIELDS",
        "status": 400,
        "message": "Required fields are missing",
    }

    # ═══════════════════════════════════════════════════════════════
    # Conflict Errors (409 Conflict)
    # ═══════════════════════════════════════════════════════════════

    USERNAME_EXISTS = {
        "code": "USERNAME_EXISTS",
        "status": 409,
        "message": "Username already exists",
    }

    EMAIL_EXISTS = {
        "code": "EMAIL_EXISTS",
        "status": 409,
        "message": "Email already registered",
    }

    # ═══════════════════════════════════════════════════════════════
    # Authentication Errors (401 Unauthorized)
    # ═══════════════════════════════════════════════════════════════

    INVALID_CREDENTIALS = {
        "code": "INVALID_CREDENTIALS",
        "status": 401,
        "message": "Invalid username or password",
    }

    ACCOUNT_DISABLED = {
        "code": "ACCOUNT_DISABLED",
        "status": 401,
        "message": "Account is disabled",
    }

    # ═══════════════════════════════════════════════════════════════
    # Password Change Errors (400 Bad Request)
    # ═══════════════════════════════════════════════════════════════

    WRONG_OLD_PASSWORD = {
        "code": "WRONG_OLD_PASSWORD",
        "status": 400,
        "message": "Current password is incorrect",
    }

    SAME_PASSWORD = {
        "code": "SAME_PASSWORD",
        "status": 400,
        "message": "New password must be different from current password",
    }

    PASSWORD_MUST_BE_DIFFERENT = {
        "code": "PASSWORD_MUST_BE_DIFFERENT",
        "status": 400,
        "message": "New password must be different from current password",
    }

    # ═══════════════════════════════════════════════════════════════
    # Resource Not Found Errors (404 Not Found)
    # ═══════════════════════════════════════════════════════════════

    USER_NOT_FOUND = {
        "code": "USER_NOT_FOUND",
        "status": 404,
        "message": "User not found",
    }

    ROLE_NOT_FOUND = {
        "code": "ROLE_NOT_FOUND",
        "status": 404,
        "message": "Role not found",
    }

    # ═══════════════════════════════════════════════════════════════
    # Role Assignment Errors (409 Conflict)
    # ═══════════════════════════════════════════════════════════════

    ROLE_ALREADY_ASSIGNED = {
        "code": "ROLE_ALREADY_ASSIGNED",
        "status": 409,
        "message": "User already has role",
    }

    ROLE_NOT_ASSIGNED = {
        "code": "ROLE_NOT_ASSIGNED",
        "status": 409,
        "message": "User does not have role",
    }

    # ═══════════════════════════════════════════════════════════════
    # Authorization Errors (403 Forbidden)
    # ═══════════════════════════════════════════════════════════════

    ALREADY_LOGGED_IN = {
        "code": "ALREADY_LOGGED_IN",
        "status": 403,
        "message": "Already logged in",
    }

    # ═══════════════════════════════════════════════════════════════
    # Server Errors (500 Internal Server Error)
    # ═══════════════════════════════════════════════════════════════

    REGISTRATION_FAILED = {
        "code": "REGISTRATION_FAILED",
        "status": 500,
        "message": "Registration failed. Please try again later",
    }

    PASSWORD_CHANGE_FAILED = {
        "code": "PASSWORD_CHANGE_FAILED",
        "status": 500,
        "message": "Password change failed. Please try again later",
    }

    ROLE_ASSIGNMENT_FAILED = {
        "code": "ROLE_ASSIGNMENT_FAILED",
        "status": 500,
        "message": "Failed to assign role. Please try again later",
    }

    ROLE_REVOKE_FAILED = {
        "code": "ROLE_REVOKE_FAILED",
        "status": 500,
        "message": "Failed to revoke role. Please try again later",
    }

    USER_UPDATE_FAILED = {
        "code": "USER_UPDATE_FAILED",
        "status": 500,
        "message": "Update failed. Please try again later",
    }

    USER_DELETE_FAILED = {
        "code": "USER_DELETE_FAILED",
        "status": 500,
        "message": "Delete failed. Please try again later",
    }

    @classmethod
    def get_error(cls, error_key: str) -> dict:
        """
        Get error details by key.

        Args:
            error_key: Error constant name (e.g., 'USERNAME_EXISTS')

        Returns:
            Dictionary with code, status, and message
        """
        return getattr(cls, error_key, cls.REGISTRATION_FAILED)

    @classmethod
    def find_error_by_message(cls, message: str) -> dict:
        """
        Find error details by message.

        Args:
            message: Error message to search for

        Returns:
            Dictionary with code, status, and message
        """
        for attr_name in dir(cls):
            if attr_name.startswith("_"):
                continue
            attr = getattr(cls, attr_name)
            if isinstance(attr, dict) and attr.get("message") == message:
                return attr
        return cls.REGISTRATION_FAILED
