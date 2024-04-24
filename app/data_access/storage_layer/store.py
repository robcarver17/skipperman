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

    @classmethod
    def from_individual_methods(cls, read_method:Callable, write_method: Callable, **method_kwargs):
        key = str(read_method)+str(method_kwargs)

        return cls(key=key, read_method=read_method, write_method=write_method, method_kwargs=method_kwargs)

@dataclass
class StorageItem:
    contents: object
    data_access_method: DataAccessMethod
    changed: bool = False

class Store(dict):
    def read(self, data_access_method: DataAccessMethod):
        storage_item = self.get(data_access_method.key, NO_OBJECT)
        if storage_item is NO_OBJECT:
            storage_item = self._read_from_data_and_store(data_access_method)

        return storage_item.contents

    def write(self, contents, data_access_method: DataAccessMethod):
        storage_item = StorageItem(contents=contents, data_access_method=data_access_method, changed=True)
        self[data_access_method.key] = storage_item

    def save_stored_items(self):
        ## write only changed items
        for key, storage_item in self.items():
            self._save_to_data_from_store_if_changed(key)

    def _read_from_data_and_store(self, data_access_method: DataAccessMethod):
        contents = self._read_from_data(data_access_method)
        storage_item = StorageItem(contents=contents, changed=False, data_access_method=data_access_method)
        self[data_access_method.key] = storage_item

        return storage_item


    def _save_to_data_from_store_if_changed(self, key):
        storage_item = self.get_storage_item(key)
        if not storage_item.changed:
            return
        contents = storage_item.contents
        self._write_to_data(contents, data_access_method=storage_item.data_access_method)

    def _read_from_data(self, data_access_method: DataAccessMethod):
        return data_access_method.read_method(**data_access_method.method_kwargs)

    def _write_to_data(self, contents, data_access_method: DataAccessMethod):
        data_access_write_method = data_access_method.write_method
        kwargs =data_access_method.method_kwargs
        print("Writing %s to %s with %s" % (str(contents), str(data_access_write_method), str(kwargs)))
        data_access_write_method(contents, **kwargs)

    def get_storage_item(self, key) -> StorageItem:
        return self[key]

