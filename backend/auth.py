"""
Basic Auth — Shared Password Gate

For "10 people I trust should be able to view this, strangers on the
internet shouldn't" -- this is NOT a full user-account system (no
per-person login, no roles). It's a single shared password that
issues a signed session cookie. That's the right amount of security
for a shared read-mostly dashboard; building full multi-user accounts
would be solving a problem you don't have yet.

If DASHBOARD_PASSWORD is not set in .env, auth is disabled entirely
(so local development still works with zero friction) -- but this
means the app is WIDE OPEN if deployed like that. Set the password
before deploying anywhere reachable from outside your own machine.
"""

from __future__ import annotations

import hmac
import time
import secrets

from fastapi import Request
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config import settings

SESSION_COOKIE_NAME = "ada_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 12  # 12 hours

# Paths that must remain reachable without auth (the login page/action
# itself, and static assets needed to RENDER the login page).
PUBLIC_PATHS = {"/login", "/static/css/app.css"}


def _sign_session_token(secret: str) -> str:
    """Simple signed token: random value + HMAC over it + timestamp.
    Not a JWT library dependency -- deliberately minimal for what
    this actually needs to do."""
    nonce = secrets.token_hex(16)
    issued_at = str(int(time.time()))
    payload = f"{nonce}:{issued_at}"
    signature = hmac.new(secret.encode(), payload.encode(), "sha256").hexdigest()
    return f"{payload}:{signature}"


def _verify_session_token(token: str, secret: str) -> bool:
    try:
        nonce, issued_at, signature = token.split(":")
    except ValueError:
        return False

    payload = f"{nonce}:{issued_at}"
    expected_signature = hmac.new(secret.encode(), payload.encode(), "sha256").hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        return False

    if time.time() - int(issued_at) > SESSION_MAX_AGE_SECONDS:
        return False

    return True


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        if not settings.dashboard_password:
            # Auth disabled -- local dev / no password configured.
            return await call_next(request)

        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        session_token = request.cookies.get(SESSION_COOKIE_NAME)

        if session_token and _verify_session_token(session_token, settings.dashboard_password):
            return await call_next(request)

        # Websocket connections can't be redirected -- reject cleanly.
        if request.url.path == "/ws":
            from starlette.responses import Response
            return Response(status_code=401)

        return RedirectResponse(url="/login")


LOGIN_PAGE_HTML = """
<!doctype html>
<html><head><title>Login — ADA Market Intelligence</title>
<style>
body{background:#07101c;color:#dbe7f5;font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}
form{background:#0b1625;border:1px solid #223249;border-radius:12px;padding:32px;width:280px}
h1{font-size:18px;margin:0 0 20px}
input{width:100%;padding:10px;border-radius:6px;border:1px solid #223249;background:#07101c;color:#dbe7f5;box-sizing:border-box;margin-bottom:14px}
button{width:100%;padding:10px;border-radius:6px;border:none;background:#4f8cff;color:#fff;font-weight:600;cursor:pointer}
.error{color:#ff4f5f;font-size:13px;margin-bottom:12px}
</style></head>
<body>
<form method="post" action="/login">
<h1>ADA Market Intelligence</h1>
{error_html}
<input type="password" name="password" placeholder="Password" autofocus required>
<button type="submit">Sign in</button>
</form>
</body></html>
"""


def login_page(error: bool = False) -> HTMLResponse:
    error_html = '<div class="error">Incorrect password.</div>' if error else ""
    # NOTE: deliberately NOT using str.format() here -- the CSS in
    # LOGIN_PAGE_HTML is full of literal { } characters (e.g.
    # "body{background:...}") which .format() misinterprets as
    # placeholders, causing a KeyError. Plain .replace() with a
    # unique marker sidesteps that entirely.
    html = LOGIN_PAGE_HTML.replace("{error_html}", error_html)
    return HTMLResponse(html)


def handle_login_submit(password: str) -> RedirectResponse:
    if not settings.dashboard_password:
        return RedirectResponse(url="/", status_code=303)

    if hmac.compare_digest(password, settings.dashboard_password):
        response = RedirectResponse(url="/", status_code=303)
        token = _sign_session_token(settings.dashboard_password)
        response.set_cookie(
            SESSION_COOKIE_NAME,
            token,
            max_age=SESSION_MAX_AGE_SECONDS,
            httponly=True,
            samesite="lax",
        )
        return response

    # Wrong password -- redirect back to login with an error flag.
    return RedirectResponse(url="/login?error=1", status_code=303)
