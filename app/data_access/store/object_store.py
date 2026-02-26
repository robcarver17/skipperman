from typing import Callable

from app.data_access.sql.sql_and_csv_api import MixedSqlAndCsvDataApi

from app.data_access.store.object_cache import SimpleObjectCache, NOT_IN_STORE
from app.data_access.store.object_store_elements import (
    DefinitionWithArgsAndMethod,
    CachedDataItem,
)
from app.objects.utilities.exceptions import arg_not_passed


class ObjectStore:
    def __init__(
        self,
        data_api: MixedSqlAndCsvDataApi,
        new_object_cache: SimpleObjectCache = arg_not_passed,
    ):
        if new_object_cache is arg_not_passed:
            new_object_cache = SimpleObjectCache()

        self._new_object_cache = new_object_cache
        self._data_api = data_api

    def delete_all_data(self, are_you_sure: bool = False):
        ### YOU REALLY NEED TO BE SURE!
        if are_you_sure:
            ## REDUDANT CODE AS YOU CAN'T BE TOO CAREFUL
            self.data_api.delete_all_master_data(are_you_sure)

    def backup_underlying_data(self):
        self.data_api.make_backup()

    def clear_memory_cache_in_store(self):
        self.new_object_cache.clear()

    def update_without_checking_read_only(
        self, data_api_property_and_method: Callable, **kwargs
    ):
        ### does not update cache, so after use will need to clear cache without flushing
        data_api_property_and_method(**kwargs)

    def get(self, data_api_property_and_method: Callable, **kwargs):
        definition_with_args = DefinitionWithArgsAndMethod(
            data_api_property_and_method, kwargs=kwargs
        )

        cached_item = self.new_object_cache.get(
            definition_with_args.key, default=NOT_IN_STORE
        )

        if cached_item is NOT_IN_STORE:
            cached_item = self.compose_from_scratch_and_store_object_in_cache(
                definition_with_args
            )

        return cached_item.contents

    def clear_item(self, data_api_property_and_method: Callable, **kwargs):
        definition_with_args = DefinitionWithArgsAndMethod(
            data_api_property_and_method, kwargs=kwargs
        )

        self.new_object_cache.remove(definition_with_args.key)

    def compose_from_scratch_and_store_object_in_cache(
        self,
        definition_with_args: DefinitionWithArgsAndMethod,
    ) -> CachedDataItem:
        new_object_method = definition_with_args.data_api_property_and_method
        new_object = new_object_method(**definition_with_args.kwargs)
        cached_data_item = CachedDataItem(
            new_object, definition_with_args=definition_with_args
        )

        self.new_object_cache.update(cached_data_item)
        return cached_data_item

    ## Expose some data API stuff
    @property
    def global_read_only(self):
        return self.data_api.global_read_only

    @global_read_only.setter
    def global_read_only(self, global_read_only: bool):
        self.data_api.global_read_only = global_read_only

    @property
    def master_data_path(self) -> str:
        return self.data_api.master_data_path

    @property
    def backup_data_path(self):
        return self.data_api.backup_data_path

    ## underlying objects
    @property
    def data_api(self) -> MixedSqlAndCsvDataApi:
        return self._data_api

    @property
    def new_object_cache(self) -> SimpleObjectCache:
        return self._new_object_cache
