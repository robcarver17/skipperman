from copy import copy
from typing import Dict, List, Callable

from app.data_access.sql.sql_and_csv_api import MixedSqlAndCsvDataApi
from app.data_access.store.object_definitions import (
    UnderlyingObjectDefinition,
    DerivedObjectDefinition,
    IterableObjectDefinition,
)

from app.data_access.store.object_cache import SimpleObjectCache, NOT_IN_STORE
from app.data_access.store.object_store_elements import DEPRECATE_CachedDataItem, DEPRECATE_DefinitionWithArgs, \
    DEPRECATE_get_store_key, DefinitionWithArgsAndMethod, CachedDataItem
from app.data_access.store.data_access import DataAccessMethod
from app.objects.utilities.exceptions import arg_not_passed


class ObjectStore:
    def __init__(self, data_api: MixedSqlAndCsvDataApi,
                 object_cache: SimpleObjectCache = arg_not_passed,
                 new_object_cache: SimpleObjectCache =arg_not_passed):
        if object_cache is arg_not_passed:
            object_cache = SimpleObjectCache()
        if new_object_cache is arg_not_passed:
            new_object_cache = SimpleObjectCache()

        self._object_cache = object_cache
        self._new_object_cache = new_object_cache
        self._data_api = data_api

    def delete_all_data(self, are_you_sure: bool = False):
        ### YOU REALLY NEED TO BE SURE!
        if are_you_sure:
            ## REDUDANT CODE AS YOU CAN'T BE TOO CAREFUL
            self.data_api.delete_all_master_data(are_you_sure)

    def backup_underlying_data(self):
        self.data_api.make_backup()

    def save_changed_data(self):
        self.save_underlying_data()

    def save_underlying_data(self):
        for saved_data_item in self.values():
            if saved_data_item.is_underyling_object:
                if saved_data_item.changed:
                    write_modified_underlying_object_to_data_api(
                        saved_data_item=saved_data_item,
                        object_store=self,
                    )
                    saved_data_item.flag_as_saved_to_persistent()

    def clear_memory_cache_in_store(self):
        self.object_cache.clear()
        self.new_object_cache.clear()

    def DEPRECATE_update(
        self,
        new_object,
        object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition, IterableObjectDefinition],
        **kwargs,
    ):
        definition_with_args = DEPRECATE_DefinitionWithArgs(object_definition, kwargs)
        self.DEPRECATE_update_in_cache(new_object, definition_with_args=definition_with_args)

        update_components_of_changed_object(object_store=self, new_object=new_object, definition_with_args=definition_with_args)

    def update(self, data_api_property_and_method: Callable, **kwargs):
        ### does not update cache, so after use will need to clear cache without flushing
        data_api_property_and_method(**kwargs)

    def DEPRECATE_update_in_cache(
        self,
        new_object,
        definition_with_args:DEPRECATE_DefinitionWithArgs
    ):
        cached_data_item = self.object_cache.DEPRECATE_get(definition_with_args.key, NOT_IN_STORE)
        if cached_data_item is NOT_IN_STORE:
            cached_data_item = DEPRECATE_CachedDataItem(contents=new_object,
                                                        definition_with_args=definition_with_args,
                                                        changed=True)
        else:
            cached_data_item.change_contents(contents=new_object)

        self.object_cache.DEPRECATE_update(cached_data_item)

    def get(self, data_api_property_and_method: Callable, **kwargs):
        definition_with_args = DefinitionWithArgsAndMethod(data_api_property_and_method,
                                                           kwargs=kwargs)

        cached_item = self.new_object_cache.get(definition_with_args.key, default=NOT_IN_STORE)

        if cached_item is NOT_IN_STORE:
            cached_item = self.compose_from_scratch_and_store_object_in_cache(
                definition_with_args
            )

        return cached_item.contents

    def compose_from_scratch_and_store_object_in_cache(
        self,
        definition_with_args: DefinitionWithArgsAndMethod,
    ) -> CachedDataItem:
        new_object_method = definition_with_args.data_api_property_and_method
        new_object = new_object_method(**definition_with_args.kwargs)
        cached_data_item = CachedDataItem(new_object, definition_with_args=definition_with_args)

        self.new_object_cache.update(cached_data_item
                                           )
        return cached_data_item


    def DEPRECATE_get(
        self,
        object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition, IterableObjectDefinition],
        **kwargs,
    ):
        definition_with_args = DEPRECATE_DefinitionWithArgs(object_definition, kwargs)
        cached_item = self.object_cache.DEPRECATE_get(definition_with_args.key, default =NOT_IN_STORE)

        if cached_item is NOT_IN_STORE:
            cached_item = self.DEPRECATE_compose_from_scratch_and_store_object_in_cache(
                definition_with_args
            )


        return cached_item.contents



    def DEPRECATE_compose_from_scratch_and_store_object_in_cache(
        self,
        definition_with_args: DEPRECATE_DefinitionWithArgs,
    ) -> DEPRECATE_CachedDataItem:
        new_object = compose_object_for_object_store(
             object_store=self,definition_with_args=definition_with_args
        )
        cached_data_item = DEPRECATE_CachedDataItem(new_object, definition_with_args=definition_with_args)

        self.object_cache.DEPRECATE_update(cached_data_item
                                           )

        return cached_data_item


    def values(self):
        return self.object_cache.values()

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
    def object_cache(self) -> SimpleObjectCache:
        return self._object_cache

    @property
    def new_object_cache(self) -> SimpleObjectCache:
        return self._new_object_cache



def compose_object_for_object_store(
    object_store: ObjectStore,
    definition_with_args: DEPRECATE_DefinitionWithArgs
):
    object_definition = definition_with_args.object_definition
    if type(object_definition) is UnderlyingObjectDefinition:
        return compose_underyling_object_from_data_api(
            object_store=object_store, definition_with_args=definition_with_args
        )
    elif type(object_definition) is IterableObjectDefinition:
        return compose_iterable_object_from_object_store(
            object_store=object_store, definition_with_args_of_iterated_object=definition_with_args
        )
    elif type(object_definition) is DerivedObjectDefinition:
        return compose_derived_object_from_object_store(
            object_store=object_store, definition_with_args_derived_object=definition_with_args
        )
    else:
        raise Exception(
            "Object definition type %s not recognised" % str(object_definition)
        )


def compose_underyling_object_from_data_api(
    object_store: ObjectStore,  definition_with_args: DEPRECATE_DefinitionWithArgs
):
    object_definition = definition_with_args.object_definition
    kwargs = definition_with_args.kwargs

    data_access_method = get_data_access_method(
        object_store=object_store, object_definition=object_definition, **kwargs
    )
    return data_access_method.read_method(**data_access_method.method_kwargs)


def compose_derived_object_from_object_store(
    object_store: ObjectStore, definition_with_args_derived_object: DEPRECATE_DefinitionWithArgs
):
    object_definition = definition_with_args_derived_object.object_definition
    kwargs = definition_with_args_derived_object.kwargs

    composition_function = object_definition.composition_function
    dict_of_arguments = (
        object_definition.dict_of_arguments_and_underlying_object_definitions
    )
    matching_kwargs = object_definition.matching_kwargs(**kwargs)
    kwargs_to_pass = copy(matching_kwargs)

    for keyword_name, object_definition_for_keyword in dict_of_arguments.items():
        required_kwargs = object_definition_for_keyword.matching_kwargs(**kwargs)
        underyling_data_object = object_store.DEPRECATE_get(object_definition=object_definition_for_keyword,
                                                            **required_kwargs)
        kwargs_to_pass[keyword_name] = underyling_data_object


    return composition_function(**kwargs_to_pass)


def compose_iterable_object_from_object_store(
    object_store: ObjectStore, definition_with_args_of_iterated_object: DEPRECATE_DefinitionWithArgs
):
    object_definition = definition_with_args_of_iterated_object.object_definition
    kwargs = copy(definition_with_args_of_iterated_object.kwargs)

    key_to_iterate_over = object_definition.required_key_for_iteration
    list_of_keys = kwargs.pop(key_to_iterate_over)

    underlying_object_key = object_definition.key_for_underlying_object
    underlying_object_definition = object_definition.underlying_object_definition

    dict_of_output = {}
    for key in list_of_keys:
        kwargs_this_element = {underlying_object_key: key}
        kwargs_this_element.update(kwargs)
        required_kwargs = underlying_object_definition.matching_kwargs(**kwargs_this_element)

        underyling_object_this_key = object_store.DEPRECATE_get(underlying_object_definition, **required_kwargs)

        dict_of_output[key] = underyling_object_this_key

    return dict_of_output



def update_components_of_changed_object(
        new_object,
        definition_with_args: DEPRECATE_DefinitionWithArgs,
        object_store: ObjectStore,
):

    ## save objects below
    object_definition = definition_with_args.object_definition
    if type(object_definition) is UnderlyingObjectDefinition:
        ## no objects below
        pass
    elif type(object_definition) is IterableObjectDefinition:
        update_component_objects_in_store_with_changed_iterable_object(
            new_object=new_object,
            definition_with_args=definition_with_args,
            object_store=object_store,
        )

    elif type(object_definition) is DerivedObjectDefinition:
        update_component_objects_in_store_with_changed_derived_object(
            new_object=new_object,
            definition_with_args=definition_with_args,
            object_store=object_store,
        )
    else:
        raise Exception(
            "Object definition type %s not recognised" % str(type(object_definition))
        )




def update_component_objects_in_store_with_changed_iterable_object(
    new_object: dict,
    object_store: ObjectStore,
        definition_with_args: DEPRECATE_DefinitionWithArgs,

):
    object_definition = definition_with_args.object_definition
    kwargs_to_use = copy(definition_with_args.kwargs)
    kwargs_to_use.pop(object_definition.required_key_for_iteration)

    underlying_object_key_name = object_definition.key_for_underlying_object
    underyling_object_definition = object_definition.underlying_object_definition

    list_of_keys = list(new_object.keys())

    for key in list_of_keys:
        kwargs_this_element = {underlying_object_key_name: key}
        kwargs_this_element.update(kwargs_to_use)
        required_kwargs = underyling_object_definition.matching_kwargs(**kwargs_this_element)

        new_underyling_object = new_object[key]
        object_store.DEPRECATE_update(new_object=new_underyling_object,
                                      object_definition=underyling_object_definition,
                                      **required_kwargs)


def update_component_objects_in_store_with_changed_derived_object(
    new_object,
    object_store: ObjectStore,
        definition_with_args: DEPRECATE_DefinitionWithArgs,
):
    object_definition = definition_with_args.object_definition
    kwargs = definition_with_args.kwargs

    dict_of_objects_to_modify = (
        object_definition.dict_of_properties_and_underlying_object_definitions_if_modified
    )
    for (
        property_name,
        underlying_object_definition,
    ) in dict_of_objects_to_modify.items():
        new_underyling_object = getattr(new_object, property_name)
        required_kwargs = underlying_object_definition.matching_kwargs(**kwargs)

        object_store.DEPRECATE_update(
            new_object=new_underyling_object,
            object_definition=underlying_object_definition,
            **required_kwargs,
        )


def write_modified_underlying_object_to_data_api(
    saved_data_item: DEPRECATE_CachedDataItem,
    object_store: ObjectStore,
):
    new_object = saved_data_item.contents
    object_definition = saved_data_item.object_definition
    kwargs = saved_data_item.kwargs

    try:
        data_access_method = get_data_access_method(
            object_store=object_store, object_definition=object_definition, **kwargs
        )
    except Exception as e:
        raise Exception("issues %s with %s %s" % (str(e), str(object_definition), str(kwargs)))
    data_access_write_method = data_access_method.write_method
    kwargs = data_access_method.method_kwargs
    data_access_write_method(new_object, **kwargs)



def get_data_access_method(
    object_store: ObjectStore, object_definition: UnderlyingObjectDefinition, **kwargs
) -> DataAccessMethod:
    matching_kwargs = object_definition.matching_kwargs(**kwargs)
    data_access_callable_function = object_definition.data_store_method_function
    data_access_method = data_access_callable_function(
        object_store.data_api, **matching_kwargs
    )

    return data_access_method
