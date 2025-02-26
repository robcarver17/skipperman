from flask import session

from app.web.html.url_define import TOGGLE_READ_ONLY

SESSION_KEY_FOR_TOGGLE = "__read_only"


def toggle_read_only():
    if is_read_only():
        session[SESSION_KEY_FOR_TOGGLE] = False
    else:
        session[SESSION_KEY_FOR_TOGGLE] = True


def is_read_only():
    return session.get(SESSION_KEY_FOR_TOGGLE, False)
