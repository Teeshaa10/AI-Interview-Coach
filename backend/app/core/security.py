from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings


def hash_password(plain_password: str) -> str:
    """
    Hashes a plaintext password with bcrypt.

    bcrypt generates a random salt and embeds it directly in the output
    hash, so we never store or manage salts separately — the salt travels
    with the hash. bcrypt is also deliberately slow (tunable via a work
    factor baked into bcrypt.gensalt()), and that slowness is the entire
    point: it makes brute-forcing a stolen password database
    computationally expensive. Never use a fast, general-purpose hash like
    SHA-256 for passwords — speed is a liability here, not a feature.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks a plaintext password against a stored bcrypt hash.

    bcrypt.checkpw re-derives the hash using the salt already embedded in
    hashed_password and compares the result internally in constant time.
    We never compare hashes with a plain `==` — a naive comparison can
    leak timing information about how many leading characters matched,
    which is a real (if narrow) attack vector against password checks.
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str) -> str:
    """
    Issues a signed JWT for the given user id.

    The payload carries three standard claims: `sub` ("subject" — who the
    token represents), `iat` ("issued at", useful for audit logs), and
    `exp` ("expiry" — a leaked token stops being valid after this point,
    read from Settings so the lifetime is configurable per environment).
    We sign with HS256 using a secret key only the backend knows, so a
    token can't be forged without that key. Because the JWT is
    self-contained and signature-verifiable, checking it never requires a
    database round trip — that's what makes JWT auth scale horizontally
    across multiple backend instances with no shared session store.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# def decode_access_token(token: str) -> str:
#     """
#     Verifies a JWT's signature and expiry, and returns the user id (`sub`
#     claim) it was issued for.

#     Raises jwt.PyJWTError (or a subclass, e.g. jwt.ExpiredSignatureError)
#     on any failure — expired, malformed, or signed with the wrong key. The
#     caller (get_current_user in dependencies.py) is responsible for
#     catching that and turning it into a 401 response; this function stays
#     unaware of HTTP entirely, matching the same separation of concerns we
#     used for the domain exceptions in app/exceptions/.
#     """
#     settings = get_settings()
#     payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
#     return payload["sub"]
def decode_access_token(token: str) -> str:
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        print("JWT PAYLOAD:", payload)

        return payload["sub"]

    except Exception as e:
        print("JWT ERROR:", type(e).__name__)
        print("JWT ERROR MESSAGE:", e)
        raise