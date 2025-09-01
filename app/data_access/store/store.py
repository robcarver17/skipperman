from copy import copy
from dataclasses import dataclass
from typing import Callable


NO_OBJECT = object()


@dataclass
class DataAccessMethod:
    key: str
    read_method: Callable
    write_method: Callable
    method_kwargs: dict

    def __init__(self, key, read_method: Callable, write_method: Callable, **kwargs):
        self.read_method = read_method
        self.write_method = write_method
        if len(kwargs) == 0:
            self.method_kwargs = {}
        else:
            self.method_kwargs = kwargs
            key += str(kwargs)

        self.key = key


@dataclass
class StorageItem:
    contents: object
    data_access_method: DataAccessMethod
    changed: bool = False


class Store(dict):
    def read(self, data_access_method: DataAccessMethod):
        storage_item = self.get_storage_item(data_access_method.key)
        if storage_item is NO_OBJECT:
            storage_item = self._read_from_data_and_store(data_access_method)

        return storage_item.contents

    def write(self, contents, data_access_method: DataAccessMethod):
        storage_item = StorageItem(
            contents=contents, data_access_method=data_access_method, changed=True
        )
        self.put_storage_item(storage_item)

    def clear_stored_items(self):
        list_of_keys = list(self.keys())
        for key in list_of_keys:
            self.delete_storage_item_with_key(key)

    def save_stored_items(self):
        ## write only changed items
        list_of_keys = list(self.keys())
        for key in list_of_keys:
            self._save_to_data_from_store_if_changed(key)
            self.mark_stored_item_as_unchanged(key)

    def mark_stored_item_as_unchanged(self, key):
        storage_item = self.get_storage_item(key)
        storage_item = StorageItem(
            contents=storage_item.contents,
            data_access_method=storage_item.data_access_method,
            changed=False,
        )
        self.put_storage_item(storage_item)

    def _read_from_data_and_store(self, data_access_method: DataAccessMethod):
        contents = self._read_from_data(data_access_method)
        storage_item = StorageItem(
            contents=contents, changed=False, data_access_method=data_access_method
        )
        self.put_storage_item(storage_item)

        return storage_item

    def _save_to_data_from_store_if_changed(self, key):
        storage_item = self.get_storage_item(key)
        unchanged = not storage_item.changed
        if unchanged:
            print("%s unchanged not saving")
            return
        contents = storage_item.contents
        print("%s changed to %s, writing" % (key, contents))
        self._write_to_data(
            contents, data_access_method=storage_item.data_access_method
        )

    def _read_from_data(self, data_access_method: DataAccessMethod):
        return data_access_method.read_method(**data_access_method.method_kwargs)

    def _write_to_data(self, contents, data_access_method: DataAccessMethod):
        data_access_write_method = data_access_method.write_method
        kwargs = data_access_method.method_kwargs
        data_access_write_method(contents, **kwargs)

    def get_storage_item(self, key) -> StorageItem:
        storage_item = self.get(key, NO_OBJECT)
        return storage_item

    def put_storage_item(self, storage_item: StorageItem):
        key = storage_item.data_access_method.key
        self[key] = storage_item

    def delete_storage_item_with_key(self, key: str):
        del self[key]
