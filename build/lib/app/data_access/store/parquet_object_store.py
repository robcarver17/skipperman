from app.data_access.api.generic_api import CsvDataApi
from app.data_access.store.object_store import ObjectStore
from app.data_access.store.store import UnderylingDataCache


class ParqueStore(ObjectStore):
    def __init__(self, data_store: UnderylingDataCache, data_api: CsvDataApi):
        super().__init__(data_store, data_api)
        self._data_store = data_store
        self._data_api = data_api
        self._object_store = {}

