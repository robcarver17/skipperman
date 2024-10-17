from copy import copy

from app.data_access.api.generic_api import GenericDataApi
from app.data_access.store.object_definitions import UnderlyingObjectDefinition, DerivedObjectDefinition

from app.data_access.store.store import Store, DataAccessMethod

NOT_IN_STORE = object()



class ObjectStore:
    def __init__(self, data_store: Store, data_api: GenericDataApi):
        self._data_store = data_store
        self._data_api = data_api
        self._object_store = {}

    def backup_underlying_data(self):
        self.data_api.make_backup()

    def clear_store(self):
        self.data_store.clear_stored_items()
        self.clear_object_store()

    def flush_store(self):
        self.data_store.save_stored_items()
        self.data_store.clear_stored_items()
        self.clear_object_store() ## everything saved in data store

    def update(self, new_object, object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition],
               **kwargs):
        self._update_object_in_store(new_object=new_object, object_definition=object_definition, **kwargs)

        update_data_and_underlying_objects_in_store_with_changed_object(new_object=new_object,
                                                                        object_definition=object_definition,
                                                                        object_store=self,
                                                                        **kwargs)

    def get(self, object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition], **kwargs):

        key = get_store_key(object_definition=object_definition, **kwargs)
        stored_object = self.object_store.get(key, NOT_IN_STORE)

        if stored_object is NOT_IN_STORE:
            stored_object = self._call_and_store(object_definition=object_definition, key=key, **kwargs)

        return stored_object

    def _update_object_in_store(self, new_object, object_definition: [DerivedObjectDefinition,
                                                                               UnderlyingObjectDefinition], **kwargs):
        key = get_store_key(object_definition=object_definition, **kwargs)
        self.object_store[key] = new_object
        print("Updating %s in object store" % key)

    def _call_and_store(self, object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition], key: str, **kwargs):
        stored_object = compose_object_for_object_store(object_definition=object_definition, object_store=self, **kwargs)

        self.object_store[key] = stored_object

        return stored_object

    def clear_object_store(self):
        self._object_store = {}

    @property
    def data_api(self) -> GenericDataApi:
        return self._data_api

    @property
    def data_store(self) -> Store:
        return self._data_store

    @property
    def object_store(self) -> dict:
        return self._object_store

def get_store_key(object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition], **kwargs):
    key = object_definition.key + str(kwargs)

    return key

def update_data_and_underlying_objects_in_store_with_changed_object(new_object, object_store: ObjectStore, object_definition: [
    DerivedObjectDefinition, UnderlyingObjectDefinition], **kwargs):
    if type(object_definition) is UnderlyingObjectDefinition:
        update_data_store_with_changed_underlying_object(new_object=new_object,
                                              object_store=object_store,
                                              object_definition=object_definition,
                                              **kwargs)
    else:
        update_objects_in_store_with_changed_derived_object(
            new_object=new_object,
            object_store=object_store,
            object_definition=object_definition,
            **kwargs
        )

def update_data_store_with_changed_underlying_object(new_object, object_store: ObjectStore,
                                          object_definition: UnderlyingObjectDefinition, **kwargs):

    data_access_method = get_data_access_method(object_store=object_store, object_definition=object_definition, **kwargs)
    data_store = object_store.data_store

    data_store.write(new_object, data_access_method=data_access_method)
    print("updating %s in data store" % str(object_definition))

def update_objects_in_store_with_changed_derived_object(new_object, object_store: ObjectStore,
                                                                   object_definition: DerivedObjectDefinition, **kwargs):

    dict_of_objects_to_modify = object_definition.dict_of_properties_and_underlying_object_definitions_if_modified
    for property_name, underlying_object_definition in dict_of_objects_to_modify.items():
        ## if only one source of truth, should be fine
        new_underyling_object = getattr(new_object, property_name)
        object_store.update(new_object=new_underyling_object, object_definition=underlying_object_definition, **kwargs)


def compose_object_for_object_store(object_store: ObjectStore, object_definition: [DerivedObjectDefinition,
                                                                                   UnderlyingObjectDefinition], **kwargs):
    if type(object_definition) is UnderlyingObjectDefinition:
        return compose_underyling_object_from_data_store(object_store=object_store, object_definition=object_definition, **kwargs)
    else:
        return compose_derived_object_from_object_store(object_store=object_store, object_definition=object_definition, **kwargs)


def compose_derived_object_from_object_store(object_store: ObjectStore, object_definition: DerivedObjectDefinition, **kwargs):
    composition_function = object_definition.composition_function
    dict_of_arguments =object_definition.dict_of_arguments_and_underlying_object_definitions
    matching_kwargs = object_definition.matching_kwargs(**kwargs)
    kwargs_to_pass = copy(matching_kwargs)
    for keyword_name, object_definition_for_keyword in dict_of_arguments.items():
        kwargs_to_pass[keyword_name] = object_store.get(object_definition_for_keyword, **kwargs)

    return composition_function(**kwargs_to_pass)

def compose_underyling_object_from_data_store(object_store: ObjectStore, object_definition: UnderlyingObjectDefinition, **kwargs):
    data_access_method = get_data_access_method(object_store=object_store, object_definition=object_definition, **kwargs)
    data_store = object_store.data_store
    return data_store.read(data_access_method)



def get_data_access_method(object_store: ObjectStore, object_definition: UnderlyingObjectDefinition, **kwargs) -> DataAccessMethod:
    matching_kwargs = object_definition.matching_kwargs(**kwargs)
    data_access_callable_function = object_definition.data_store_method_function
    data_access_method = data_access_callable_function(object_store.data_api, **matching_kwargs)

    return data_access_method


