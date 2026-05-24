import hashlib
from core.interfaces.services import IAuthenticationService


class SimpleAuthService(IAuthenticationService):
    """Упрощенная версия для отладки"""

    def hash_password(self, password: str) -> str:
        hash_result = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return hash_result

    def verify_password(self, password: str, password_hash: str) -> bool:
        try:
            new_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            return new_hash == password_hash
        except Exception:
            return False