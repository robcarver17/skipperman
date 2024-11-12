from app.data_access.data import data_api, object_store
from app.web.flask.flask_interface import flaskInterface


def make_backup_from_menu():
    object_store.backup_underlying_data()
