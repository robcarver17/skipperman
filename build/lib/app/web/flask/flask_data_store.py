from flask_caching import Cache

from app.data_access.store.store import UnderylingDataCache, CachedUnderylingDataItem, NO_OBJECT


class FlaskStore(UnderylingDataCache):
    def __init__(self, flask_cache: Cache):
        self.flask_cache=flask_cache
        super().__init__()

    def keys(self):
        return self.flask_cache.get_dict().keys()

    def clear_stored_items(self):
        self.flask_cache.clear()

    def get_storage_item(self, key) -> CachedUnderylingDataItem:
        storage_item = self.flask_cache.get(key)
        if storage_item is None:
            return NO_OBJECT
        return storage_item

    def put_storage_item(self, storage_item: CachedUnderylingDataItem):
        key = storage_item.data_access_method.key
        self.flask_cache.set(key, storage_item)

    def delete_storage_item_with_key(self, key: str):
        self.flask_cache.delete(key)

    @property
    def flask_cache(self) -> Cache:
        return self._flask_cache

    @flask_cache.setter
    def flask_cache(self, cache:Cache):
        self._flask_cache=cache

