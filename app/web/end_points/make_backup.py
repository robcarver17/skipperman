

from app.data_access.init_data import  underling_data_api
from app.data_access.store.object_store import ObjectStore
from app.data_access.store.store import Store
from app.web.flask.flask_interface import flaskInterface
from app.web.flask.security import get_access_group_for_current_user


def make_backup_from_menu():
    group = get_access_group_for_current_user()
    store = Store()
    object_store = ObjectStore(data_store=store, data_api=underling_data_api)

    interface = flaskInterface(object_store, user_group=group)
    interface.object_store.backup_underlying_data()
    interface.log_error("Data snapshot done")
