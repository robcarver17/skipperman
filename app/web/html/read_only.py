from flask import session
from app.data_access.init_data import underling_data_api

SESSION_KEY_FOR_TOGGLE = "__read_only"

def toggle_read_only_local():
    if is_local_read_only():
        session[SESSION_KEY_FOR_TOGGLE] = False
    else:
        session[SESSION_KEY_FOR_TOGGLE] = True

def toggle_read_only_global():
    if is_global_read_only():
        underling_data_api.global_read_only = False
    else:
        underling_data_api.global_read_only = True

def is_read_only():
    return is_local_read_only() or is_global_read_only()

def is_local_read_only():
    return session.get(SESSION_KEY_FOR_TOGGLE, False)

def is_global_read_only() -> bool:
    return underling_data_api.global_read_only