from app.data_access.init_data import object_store
from app.web.flask.flask_interface import flaskInterface
from app.web.flask.security import get_access_group_for_current_user


def make_backup_from_menu():
    group = get_access_group_for_current_user()
    interface = flaskInterface(object_store, user_group=group)
    interface.object_store.backup_underlying_data()
    interface.log_error("Data snapshot done")
