from typing import Callable

from app.data_access.store.data_access import DataLayer

NOT_IN_STORE = object()


class AdHocCache(DataLayer):
    def __init__(self, data_layer: DataLayer):
        super().__init__(store=data_layer.store, underlying_data=data_layer.data)
        self._adhoc_store = {}
        self._data_layer = data_layer

    def get_from_cache(self, callable_function: Callable, **kwargs):
        key = callable_function.__name__ + str(kwargs)

        result = self._adhoc_store.get(key, NOT_IN_STORE)

        if result is NOT_IN_STORE:
            result = self._call_and_store_in_adhoc(
                callable_function=callable_function, key=key, **kwargs
            )

        return result

    def _call_and_store_in_adhoc(self, callable_function: Callable, key: str, **kwargs):
        result = callable_function(data_layer=self.data_layer, **kwargs)

        self._adhoc_store[key] = result

        return result

    @property
    def data_layer(self):
        return self._data_layer
