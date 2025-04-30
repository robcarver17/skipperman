from copy import copy

from app.data_access.api.generic_api import GenericDataApi
from app.data_access.store.object_definitions import (
    UnderlyingObjectDefinition,
    DerivedObjectDefinition,
    IterableObjectDefinition,
)

from app.data_access.store.store import Store, DataAccessMethod

NOT_IN_STORE = object()


class ObjectStore:
    def __init__(self, data_store: Store, data_api: GenericDataApi):
        self._data_store = data_store
        self._data_api = data_api
        self._object_store = {}

    def delete_all_data(self, are_you_sure: bool = False):
        ### YOU REALLY NEED TO BE SURE!
        if are_you_sure:
            ## REDUDANT CODE AS YOU CAN'T BE TOO CAREFUL
            self.data_api.delete_all_master_data(are_you_sure)

    def backup_underlying_data(self):
        self.data_api.make_backup()

    def flush_store(self, read_only: bool = False):
        self.save_store(read_only)
        self.clear_store()

    def save_store(self, read_only: bool = False):
        if read_only:
            return
        else:
            self.data_store.save_stored_items()

    def clear_store(self):
        self.data_store.clear_stored_items()  ## underlying cache
        self.clear_object_store()  ## this cache

    def update(
        self,
        new_object,
        object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition],
        **kwargs,
    ):
        self._update_object_in_store(
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
        stored_object = self.object_store.get(key, NOT_IN_STORE)

        if stored_object is NOT_IN_STORE:
            stored_object = self._call_and_store(
                object_definition=object_definition, key=key, **kwargs
            )

        return stored_object

    def _update_object_in_store(
        self,
        new_object,
        object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition],
        **kwargs,
    ):
        key = get_store_key(object_definition=object_definition, **kwargs)
        self.object_store[key] = new_object

    def _call_and_store(
        self,
        object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition],
        key: str,
        **kwargs,
    ):
        stored_object = compose_object_for_object_store(
            object_definition=object_definition, object_store=self, **kwargs
        )

        self.object_store[key] = stored_object

        return stored_object

    def clear_object_store(self):
        self._object_store = {}

    @property
    def master_data_path(self) -> str:
        return self.data_api.master_data_path

    @property
    def backup_data_path(self):
        return self.data_api.backup_data_path

    @property
    def data_api(self) -> GenericDataApi:
        return self._data_api

    @property
    def data_store(self) -> Store:
        return self._data_store

    @property
    def object_store(self) -> dict:
        return self._object_store

    @property
    def global_read_only(self):
        return self.data_api.global_read_only

    @global_read_only.setter
    def global_read_only(self, global_read_only: bool):
        self.data_api.global_read_only = global_read_only


def get_store_key(
    object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition], **kwargs
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
    data_store = object_store.data_store

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
    data_store = object_store.data_store
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
