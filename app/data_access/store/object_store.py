from copy import copy

from app.data_access.csv.csv_api import CsvDataApi
from app.data_access.store.object_definitions import (
    UnderlyingObjectDefinition,
    DerivedObjectDefinition,
    IterableObjectDefinition,
)

from app.data_access.store.underyling_data_cache import UnderylingDataCache, DataAccessMethod
from app.data_access.store.object_cache import SimpleObjectCache, NOT_IN_STORE
from app.objects.utilities.exceptions import arg_not_passed, CacheIsLocked


class ObjectStore:
    def __init__(self, underlying_data_cache: UnderylingDataCache, data_api: CsvDataApi,
                 object_cache: SimpleObjectCache = arg_not_passed):
        if object_cache is arg_not_passed:
            object_cache = SimpleObjectCache()

        self._object_cache = object_cache
        self._underlying_data_cache = underlying_data_cache
        self._data_api = data_api

    def delete_all_data(self, are_you_sure: bool = False):
        ### YOU REALLY NEED TO BE SURE!
        if are_you_sure:
            ## REDUDANT CODE AS YOU CAN'T BE TOO CAREFUL
            self.data_api.delete_all_master_data(are_you_sure)
            self.object_cache.clear_persistent_and_in_memory()


    def backup_underlying_data(self):
        self.data_api.make_backup()

    def flush_store_and_unlock_cache(self):
        self.save_cache()
        self.clear_cache_in_memory()
        self.unlock_store()

    def lock_store(self):
        ### locks occur on a post when data could be modified
        ### We only need to lock the object cache, implicit this locks the data cache as well
        if self.store_is_locked_by_another_thread:
            raise CacheIsLocked("Can't lock cache, someone else is trying to save")

        self.object_cache.lock()

    def force_cache_unlock(self):
        ## allows anyone to clear the cache lock
        self.object_cache.force_cache_unlock()

    def unlock_store(self):
        ## will raise error if not us who has locked it
        self.object_cache.unlock()

    @property
    def store_is_locked_by_another_thread(self):
        return self.object_cache.is_locked_by_another_thread

    def save_cache(self):
        if self.store_is_locked_by_another_thread:
            raise CacheIsLocked("Can't save changes, someone else is trying to save")

        self.object_cache.save_cache() ## save object first, as this will also throw a lock error, just in case
        self.underlying_data_cache.save_cache()

    def clear_cache_in_memory(self):
        self.underlying_data_cache.clear_stored_items()
        ### Does not clear persistent object cache on disk
        self.object_cache.clear_in_memory_only()

    def clear_store_including_persistent_cache(self):
        self.underlying_data_cache.clear_stored_items()
        self.object_cache.clear_persistent_and_in_memory()

    def update(
        self,
        new_object,
        object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition],
        **kwargs,
    ):
        self._update_object_in_cache(
            new_object=new_object, object_definition=object_definition, **kwargs
        )

        update_data_and_underlying_objects_in_store_with_changed_object(
            new_object=new_object,
            object_definition=object_definition,
            object_store=self,
            **kwargs,
        )

    def get(
        self,
        object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition],
        **kwargs,
    ):
        key = get_store_key(object_definition=object_definition, **kwargs)
        stored_object = self.object_cache.get(key, default =NOT_IN_STORE)

        if stored_object is NOT_IN_STORE:
            stored_object = self._call_and_store_object_in_cache(
                object_definition=object_definition, key=key, **kwargs
            )

        return stored_object

    def _update_object_in_cache(
        self,
        new_object,
        object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition],
        **kwargs,
    ):
        key = get_store_key(object_definition=object_definition, **kwargs)
        self.object_cache.update(key=key, new_object=new_object)

    def _call_and_store_object_in_cache(
        self,
        object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition],
        key: str,
        **kwargs,
    ):
        stored_object = compose_object_for_object_store(
            object_definition=object_definition, object_store=self, **kwargs
        )

        self.object_cache.update(key=key, new_object=stored_object)

        return stored_object


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
    def data_api(self) -> CsvDataApi:
        return self._data_api

    @property
    def underlying_data_cache(self) -> UnderylingDataCache:
        return self._underlying_data_cache

    @property
    def object_cache(self) -> SimpleObjectCache:
        return self._object_cache


def get_store_key(
    object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition, IterableObjectDefinition], **kwargs
):
    key = object_definition.key + str(kwargs)

    return key


def update_data_and_underlying_objects_in_store_with_changed_object(
    new_object,
    object_store: ObjectStore,
    object_definition: [
        DerivedObjectDefinition,
        UnderlyingObjectDefinition,
        IterableObjectDefinition,
    ],
    **kwargs,
):
    if type(object_definition) is UnderlyingObjectDefinition:
        update_data_store_with_changed_underlying_object(
            new_object=new_object,
            object_store=object_store,
            object_definition=object_definition,
            **kwargs,
        )
    elif type(object_definition) is IterableObjectDefinition:
        update_objects_in_store_with_changed_iterable_object(
            new_object=new_object,
            object_store=object_store,
            object_definition=object_definition,
            **kwargs,
        )

    elif type(object_definition) is DerivedObjectDefinition:
        update_objects_in_store_with_changed_derived_object(
            new_object=new_object,
            object_store=object_store,
            object_definition=object_definition,
            **kwargs,
        )
    else:
        raise Exception(
            "Object definition type %s not recognised" % str(type(object_definition))
        )


def update_data_store_with_changed_underlying_object(
    new_object,
    object_store: ObjectStore,
    object_definition: UnderlyingObjectDefinition,
    **kwargs,
):
    data_access_method = get_data_access_method(
        object_store=object_store, object_definition=object_definition, **kwargs
    )
    data_store = object_store.underlying_data_cache

    data_store.write(new_object, data_access_method=data_access_method)


def update_objects_in_store_with_changed_iterable_object(
    new_object,
    object_store: ObjectStore,
    object_definition: IterableObjectDefinition,
    **kwargs,
):
    list_of_keys = list(new_object.keys())
    underlying_object_key = object_definition.key_for_underlying_object

    for key in list_of_keys:
        kwargs_this_element = {underlying_object_key: key}
        kwargs_this_element.update(kwargs)
        update_data_store_with_changed_underlying_object(
            new_object=new_object[key],
            object_store=object_store,
            object_definition=object_definition.underlying_object_definition,
            **kwargs_this_element,
        )


def update_objects_in_store_with_changed_derived_object(
    new_object,
    object_store: ObjectStore,
    object_definition: DerivedObjectDefinition,
    **kwargs,
):
    dict_of_objects_to_modify = (
        object_definition.dict_of_properties_and_underlying_object_definitions_if_modified
    )
    for (
        property_name,
        underlying_object_definition,
    ) in dict_of_objects_to_modify.items():
        ## if only one source of truth, should be fine
        new_underyling_object = getattr(new_object, property_name)
        object_store.update(
            new_object=new_underyling_object,
            object_definition=underlying_object_definition,
            **kwargs,
        )


def compose_object_for_object_store(
    object_store: ObjectStore,
    object_definition: [
        DerivedObjectDefinition,
        IterableObjectDefinition,
        UnderlyingObjectDefinition,
    ],
    **kwargs,
):
    if type(object_definition) is UnderlyingObjectDefinition:
        return compose_underyling_object_from_data_store(
            object_store=object_store, object_definition=object_definition, **kwargs
        )
    elif type(object_definition) is IterableObjectDefinition:
        return compose_iterable_object_from_object_store(
            object_store=object_store, object_definition=object_definition, **kwargs
        )
    elif type(object_definition) is DerivedObjectDefinition:
        return compose_derived_object_from_object_store(
            object_store=object_store, object_definition=object_definition, **kwargs
        )
    else:
        raise Exception(
            "Object definition type %s not recognised" % str(object_definition)
        )


def compose_derived_object_from_object_store(
    object_store: ObjectStore, object_definition: DerivedObjectDefinition, **kwargs
):
    composition_function = object_definition.composition_function
    dict_of_arguments = (
        object_definition.dict_of_arguments_and_underlying_object_definitions
    )
    matching_kwargs = object_definition.matching_kwargs(**kwargs)
    kwargs_to_pass = copy(matching_kwargs)
    for keyword_name, object_definition_for_keyword in dict_of_arguments.items():
        kwargs_to_pass[keyword_name] = object_store.get(
            object_definition_for_keyword, **kwargs
        )

    return composition_function(**kwargs_to_pass)


def compose_iterable_object_from_object_store(
    object_store: ObjectStore, object_definition: IterableObjectDefinition, **kwargs
):
    key_to_iterate_over = object_definition.required_key_for_iteration
    list_of_keys = kwargs.pop(key_to_iterate_over)

    underlying_object_key = object_definition.key_for_underlying_object
    dict_of_output = {}
    for key in list_of_keys:
        kwargs_this_element = {underlying_object_key: key}
        kwargs_this_element.update(kwargs)
        underyling_data_this_key = compose_underyling_object_from_data_store(
            object_store=object_store,
            object_definition=object_definition.underlying_object_definition,
            **kwargs_this_element,
        )
        dict_of_output[key] = underyling_data_this_key

    return dict_of_output


def compose_underyling_object_from_data_store(
    object_store: ObjectStore, object_definition: UnderlyingObjectDefinition, **kwargs
):
    data_access_method = get_data_access_method(
        object_store=object_store, object_definition=object_definition, **kwargs
    )
    data_store = object_store.underlying_data_cache
    return data_store.read(data_access_method)


def get_data_access_method(
    object_store: ObjectStore, object_definition: UnderlyingObjectDefinition, **kwargs
) -> DataAccessMethod:
    matching_kwargs = object_definition.matching_kwargs(**kwargs)
    data_access_callable_function = object_definition.data_store_method_function
    data_access_method = data_access_callable_function(
        object_store.data_api, **matching_kwargs
    )

    return data_access_method
