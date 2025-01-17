from app.data_access.init_data import object_store


def make_backup_from_menu():
    object_store.backup_underlying_data()
