from flask import session

from app.web.html.url import TOGGLE_READ_ONLY

SESSION_KEY_FOR_TOGGLE = "__read_only"


def toggle_read_only():
    print(session)
    if is_read_only():
        session[SESSION_KEY_FOR_TOGGLE] = False
    else:
        session[SESSION_KEY_FOR_TOGGLE] = True
    print(session)

def read_only_or_not_html():
    if is_read_only():
        inner_text = 'Read only: Click to change'
    else:
        inner_text = 'Click for read only'

    return '<a href="/%s" class="w3-bar-item w3-button w3-padding-16">%s</a>' % (TOGGLE_READ_ONLY, inner_text)


def is_read_only():
    return session.get(SESSION_KEY_FOR_TOGGLE, False)