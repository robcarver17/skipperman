from app.data_access.init_data import object_store
from app.web.flask.flask_interface import flaskInterface


def make_backup_from_menu():
    interface = flaskInterface(object_store)
    interface.object_store.backup_underlying_data()
    interface.log_error("Data snapshot done")
