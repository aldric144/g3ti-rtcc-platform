"""
User management service for the G3TI RTCC-UIP Backend.

This service handles all user-related operations including creation,
updates, password management, and role assignments.

CJIS Compliance Note:
- All user operations must be audited
- Password changes must be logged
- Role changes require supervisor approval
"""

import uuid
from datetime import UTC, datetime

from app.core.exceptions import (
    DuplicateEntityError,
    EntityNotFoundError,
    ValidationError,
)
from app.core.logging import audit_logger, get_logger
from app.core.security import SecurityManager
from app.schemas.auth import (
    PasswordChange,
    Role,
    UserCreate,
    UserInDB,
    UserResponse,
    UserUpdate,
)

logger = get_logger(__name__)


class UserService:
    """
    Service for user management operations.

    This service provides methods for creating, updating, and managing
    user accounts with CJIS-compliant audit logging.

    Note: In production, this would interact with a persistent database.
    For this implementation, we use an in-memory store that can be
    replaced with Neo4j or another database.
    """

    def __init__(self) -> None:
        """Initialize the user service."""
        self._users: dict[str, UserInDB] = {}
        self._username_index: dict[str, str] = {}  # username -> user_id
        self._email_index: dict[str, str] = {}  # email -> user_id
        self._security = SecurityManager()

        # Create default admin user
        self._create_default_admin()

    def _create_default_admin(self) -> None:
        """Create a default admin user for initial setup."""
        admin_id = str(uuid.uuid4())
        admin_user = UserInDB(
            id=admin_id,
            username="admin",
            email="admin@g3ti.local",
            first_name="System",
            last_name="Administrator",
            role=Role.ADMIN,
            is_active=True,
            hashed_password=self._security.hash_password("Admin@123456!"),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self._users[admin_id] = admin_user
        self._username_index["admin"] = admin_id
        self._email_index["admin@g3ti.local"] = admin_id

        logger.info("default_admin_created", user_id=admin_id)

    async def create_user(
        self, user_data: UserCreate, created_by: str | None = None
    ) -> UserResponse:
        """
        Create a new user.

        Args:
            user_data: User creation data
            created_by: ID of user creating this account

        Returns:
            UserResponse: Created user data

        Raises:
            DuplicateEntityError: If username or email already exists
            ValidationError: If password doesn't meet requirements
        """
        # Check for duplicate username
        if user_data.username.lower() in self._username_index:
            raise DuplicateEntityError("User", user_data.username, "Username already exists")

        # Check for duplicate email
        if user_data.email.lower() in self._email_index:
            raise DuplicateEntityError("User", user_data.email, "Email already exists")

        # Validate password strength
        is_valid, errors = self._security.validate_password_strength(user_data.password)
        if not is_valid:
            raise ValidationError(
                message="Password does not meet requirements", details={"errors": errors}
            )

        # Create user
        user_id = str(uuid.uuid4())
        now = datetime.now(UTC)

        user_in_db = UserInDB(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            badge_number=user_data.badge_number,
            department=user_data.department,
            role=user_data.role,
            is_active=user_data.is_active,
            hashed_password=self._security.hash_password(user_data.password),
            created_at=now,
            updated_at=now,
            password_changed_at=now,
        )

        # Store user
        self._users[user_id] = user_in_db
        self._username_index[user_data.username.lower()] = user_id
        self._email_index[user_data.email.lower()] = user_id

        # Audit log
        audit_logger.log_data_access(
            user_id=created_by or "system",
            entity_type="User",
            entity_id=user_id,
            action="create",
            fields_accessed=["username", "email", "role"],
        )

        logger.info(
            "user_created",
            user_id=user_id,
            username=user_data.username,
            role=user_data.role.value,
            created_by=created_by,
        )

        return self._to_response(user_in_db)

    async def get_user(self, user_id: str) -> UserResponse:
        """
        Get a user by ID.

        Args:
            user_id: User identifier

        Returns:
            UserResponse: User data

        Raises:
            EntityNotFoundError: If user not found
        """
        user = self._users.get(user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)

        return self._to_response(user)

    async def get_user_by_username(self, username: str) -> UserInDB | None:
        """
        Get a user by username (internal use).

        Args:
            username: Username to look up

        Returns:
            UserInDB or None: User data with password hash if found
        """
        user_id = self._username_index.get(username.lower())
        if not user_id:
            return None
        return self._users.get(user_id)

    async def get_user_by_email(self, email: str) -> UserInDB | None:
        """
        Get a user by email (internal use).

        Args:
            email: Email to look up

        Returns:
            UserInDB or None: User data with password hash if found
        """
        user_id = self._email_index.get(email.lower())
        if not user_id:
            return None
        return self._users.get(user_id)

    async def update_user(
        self, user_id: str, user_data: UserUpdate, updated_by: str
    ) -> UserResponse:
        """
        Update a user.

        Args:
            user_id: User identifier
            user_data: Update data
            updated_by: ID of user making the update

        Returns:
            UserResponse: Updated user data

        Raises:
            EntityNotFoundError: If user not found
            DuplicateEntityError: If new email already exists
        """
        user = self._users.get(user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)

        # Check email uniqueness if changing
        if user_data.email and user_data.email.lower() != user.email.lower():
            if user_data.email.lower() in self._email_index:
                raise DuplicateEntityError("User", user_data.email, "Email already exists")

            # Update email index
            del self._email_index[user.email.lower()]
            self._email_index[user_data.email.lower()] = user_id

        # Update fields
        update_dict = user_data.model_dump(exclude_unset=True)
        updated_fields = list(update_dict.keys())

        for field, value in update_dict.items():
            if value is not None:
                setattr(user, field, value)

        user.updated_at = datetime.now(UTC)

        # Audit log
        audit_logger.log_data_access(
            user_id=updated_by,
            entity_type="User",
            entity_id=user_id,
            action="update",
            fields_accessed=updated_fields,
        )

        logger.info(
            "user_updated", user_id=user_id, updated_fields=updated_fields, updated_by=updated_by
        )

        return self._to_response(user)

    async def change_password(self, user_id: str, password_data: PasswordChange) -> bool:
        """
        Change a user's password.

        Args:
            user_id: User identifier
            password_data: Current and new password

        Returns:
            bool: True if password changed successfully

        Raises:
            EntityNotFoundError: If user not found
            ValidationError: If current password is wrong or new password invalid
        """
        user = self._users.get(user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)

        # Verify current password
        if not self._security.verify_password(password_data.current_password, user.hashed_password):
            raise ValidationError("Current password is incorrect")

        # Validate new password
        is_valid, errors = self._security.validate_password_strength(password_data.new_password)
        if not is_valid:
            raise ValidationError(
                message="New password does not meet requirements", details={"errors": errors}
            )

        # Update password
        user.hashed_password = self._security.hash_password(password_data.new_password)
        user.password_changed_at = datetime.now(UTC)
        user.updated_at = datetime.now(UTC)

        # Audit log
        audit_logger.log_data_access(
            user_id=user_id,
            entity_type="User",
            entity_id=user_id,
            action="password_change",
            fields_accessed=["password"],
        )

        logger.info("password_changed", user_id=user_id)

        return True

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        role: Role | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[UserResponse], int]:
        """
        List users with pagination and filtering.

        Args:
            page: Page number (1-indexed)
            page_size: Items per page
            role: Filter by role
            is_active: Filter by active status

        Returns:
            tuple: (list of users, total count)
        """
        # Filter users
        filtered_users = list(self._users.values())

        if role is not None:
            filtered_users = [u for u in filtered_users if u.role == role]

        if is_active is not None:
            filtered_users = [u for u in filtered_users if u.is_active == is_active]

        # Sort by created_at descending
        filtered_users.sort(key=lambda u: u.created_at, reverse=True)

        total = len(filtered_users)

        # Paginate
        start = (page - 1) * page_size
        end = start + page_size
        page_users = filtered_users[start:end]

        return [self._to_response(u) for u in page_users], total

    async def deactivate_user(self, user_id: str, deactivated_by: str) -> bool:
        """
        Deactivate a user account.

        Args:
            user_id: User identifier
            deactivated_by: ID of user performing deactivation

        Returns:
            bool: True if deactivated successfully
        """
        user = self._users.get(user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)

        user.is_active = False
        user.updated_at = datetime.now(UTC)

        audit_logger.log_data_access(
            user_id=deactivated_by,
            entity_type="User",
            entity_id=user_id,
            action="deactivate",
            fields_accessed=["is_active"],
        )

        logger.info("user_deactivated", user_id=user_id, deactivated_by=deactivated_by)

        return True

    async def record_login(self, user_id: str, success: bool, ip_address: str) -> None:
        """
        Record a login attempt.

        Args:
            user_id: User identifier
            success: Whether login was successful
            ip_address: Client IP address
        """
        user = self._users.get(user_id)
        if not user:
            return

        if success:
            user.last_login = datetime.now(UTC)
            user.failed_login_attempts = 0
            user.locked_until = None
        else:
            user.failed_login_attempts += 1

            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                from datetime import timedelta

                user.locked_until = datetime.now(UTC) + timedelta(minutes=15)
                logger.warning(
                    "account_locked", user_id=user_id, failed_attempts=user.failed_login_attempts
                )

    def _to_response(self, user: UserInDB) -> UserResponse:
        """Convert internal user model to response model."""
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            badge_number=user.badge_number,
            department=user.department,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            failed_login_attempts=user.failed_login_attempts,
            locked_until=user.locked_until,
        )


# Global user service instance
_user_service: UserService | None = None


def get_user_service() -> UserService:
    """Get the user service instance."""
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service
