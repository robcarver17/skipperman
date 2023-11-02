## abstract
from flask import flash, get_flashed_messages

def flash_error(my_string):
    flash(my_string, 'error')

def get_flashed_errors():
    return get_flashed_messages()

