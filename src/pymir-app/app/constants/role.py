from dataclasses import dataclass


@dataclass
class Role:
    name: str
    description: str


class Roles:
    NORMAL = Role("NORMA", "Normal User")
    ADMIN = Role("ADMIN", "Admin User, managing Normal User")
    SUPER_ADMIN = Role("SUPER_ADMIN", "Super Admin User, managing Admin User")
