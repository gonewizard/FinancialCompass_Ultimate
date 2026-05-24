import hashlib
import secrets
from core.interfaces.services import IAuthenticationService


class SHA256AuthService(IAuthenticationService):
    def hash_password(self, password: str) -> str:
        salt = secrets.token_hex(16)
        return self._hash_with_salt(password, salt)

    def verify_password(self, password: str, password_hash: str) -> bool:
        try:
            salt = password_hash[:32]
            expected_hash = password_hash[32:]
            actual_hash = self._hash_with_salt(password, salt)
            return secrets.compare_digest(actual_hash, expected_hash)
        except:
            return False

    def _hash_with_salt(self, password: str, salt: str) -> str:
        hash_obj = hashlib.sha256()
        hash_obj.update(f"{salt}{password}".encode('utf-8'))
        return salt + hash_obj.hexdigest()