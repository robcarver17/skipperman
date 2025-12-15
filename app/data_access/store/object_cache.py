from typing import Dict, List

from app.data_access.store.object_store_elements import DEPRECATE_CachedDataItem, CachedDataItem

NOT_IN_STORE = object()

class SimpleObjectCache():
    def __init__(self):
        self._cache = {}

    def get(self, key, default = NOT_IN_STORE) -> CachedDataItem:
        return self.cache.get(key, default)

    def DEPRECATE_get(self, key, default = NOT_IN_STORE) -> DEPRECATE_CachedDataItem:
        return self.cache.get(key, default)

    def DEPRECATE_update(self, new_object: DEPRECATE_CachedDataItem):
        self.cache[new_object.key] = new_object

    def update(self, new_object: CachedDataItem):
        self.cache[new_object.key] = new_object

    def remove(self, key):
        self.cache.pop(key)

    def clear(self):
        self._cache = {}

    def keys(self) -> List[DEPRECATE_CachedDataItem]:
        return list(self.cache.keys())

    def values(self) -> List[DEPRECATE_CachedDataItem]:
        return list(self.cache.values())

    @property
    def cache(self) -> dict:
        return self._cache

