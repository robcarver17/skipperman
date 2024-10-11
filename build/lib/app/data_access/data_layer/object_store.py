from copy import copy
from dataclasses import dataclass
from typing import Callable, Dict, Union, List

from app.data_access.api.generic_api import GenericDataApi

from app.data_access.store.store import Store, DataAccessMethod

from app.data_access.store.data_layer import get_data_access_for_list_of_cadets_on_committee, \
    get_data_access_for_list_of_cadets, get_data_access_for_list_of_qualifications, \
    get_data_access_for_list_of_cadets_with_qualifications, get_data_access_for_cadets_with_groups, \
    get_data_access_for_cadets_at_event
from app.objects.composed.cadets_with_qualifications import create_dict_of_qualifications_for_cadets
from app.objects.composed.committee import  \
    create_list_of_cadet_committee_members_from_underlying_data
from app.objects.exceptions import arg_not_passed

NOT_IN_STORE = object()

@dataclass
class ObjectDefinition:
    @property
    def key(self):
        raise NotImplemented


@dataclass
class UnderlyingObjectDefinition(ObjectDefinition):
    data_store_method_function: Callable

    @property
    def key(self):
        return self.data_store_method_function.__name__


@dataclass
class DerivedObjectDefinition(ObjectDefinition):
    composition_function: Callable
    dict_of_arguments_and_underlying_object_definitions: Dict[str, Union['DerivedObjectDefinition', UnderlyingObjectDefinition]]
    list_of_object_definitions_to_modify_on_update: List[Union['DerivedObjectDefinition', UnderlyingObjectDefinition]] = arg_not_passed

    def object_definitions_to_modify_on_update(self) -> List[Union['DerivedObjectDefinition', UnderlyingObjectDefinition]]:
        if self.list_of_object_definitions_to_modify_on_update is arg_not_passed:
            return list(self.dict_of_arguments_and_underlying_object_definitions.values()) ## defaults to all arguments we rely on
        else:
            return self.list_of_object_definitions_to_modify_on_update

    @property
    def key(self):
        return self.composition_function.__name__

@dataclass
class ObjectInObjectStore:
    content: object
    list_of_dependents: list
    underlying: bool = False
    data_access_method: DataAccessMethod= None

    def update_with_new_content(self, content):
        self.content = content
        self.changed = True

    @classmethod
    def underlying_object(cls, content:object, data_access_method: DataAccessMethod):
        return cls(content=content, list_of_dependents=[], data_access_method=data_access_method, underlying=True)

    @classmethod
    def derived_object(cls, content:object, data_access_method: DataAccessMethod):
        return cls(content=content, list_of_dependents=[], data_access_method=data_access_method, underlying=True)

    @property
    def changed(self):
        return getattr(self, "_changed", False)

    @changed.setter
    def changed(self, changed: bool):
        self._changed = changed





class ObjectStore:
    def __init__(self, data_store: Store, data_api: GenericDataApi):
        self._data_store = data_store
        self._data_api = data_api
        self._object_store = {}

    def flush_store(self):
        self.data_store.save_stored_items()
        self.data_store.clear_stored_items()

    def update(self, new_content: object, object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition], **kwargs):
        stored_object = self._update_object_in_store(new_content=new_content, object_definition=object_definition, **kwargs)

        update_data_and_underlying_objects_in_store_with_changed_object(stored_object=stored_object,
                                                                        object_definition=object_definition,
                                                                        object_store=self,
                                                                        **kwargs)

    def get(self, object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition], **kwargs):
        stored_object = self.get_stored_object(object_definition, **kwargs)

        return stored_object.content

    def get_stored_object(self, object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition], **kwargs) -> ObjectInObjectStore:
        key = get_store_key(object_definition=object_definition, **kwargs)
        stored_object = self.object_store.get(key, NOT_IN_STORE)

        if stored_object is NOT_IN_STORE:
            stored_object = self._call_and_store(object_definition=object_definition, key=key, **kwargs)

        return stored_object

    def _update_object_in_store(self, new_content: object, object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition], **kwargs) -> ObjectInObjectStore:
        stored_object = self.get_stored_object(object_definition=object_definition, **kwargs)
        key = get_store_key(object_definition=object_definition, **kwargs)
        stored_object.update_with_new_content(content=new_content)

        self.object_store[key] = stored_object

        return stored_object

    def _call_and_store(self, object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition], key: str, **kwargs):
        stored_object = compose_object_for_object_store(object_definition=object_definition, object_store=self, **kwargs)

        self.object_store[key] = stored_object

        return stored_object

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

def update_data_and_underlying_objects_in_store_with_changed_object(stored_object: ObjectInObjectStore, object_store: ObjectStore, object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition], **kwargs):
    if type(object_definition) is UnderlyingObjectDefinition:
        update_data_store_with_changed_object(stored_object=stored_object,
                                              object_store=object_store,
                                              object_definition=object_definition,
                                              **kwargs)
    else:
        update_underlying_objects_in_store_with_changed_derived_object(
            object_store=object_store,
            object_definition=object_definition,
            **kwargs
        )

def update_data_store_with_changed_object(stored_object: ObjectInObjectStore, object_store: ObjectStore,
                                          object_definition: UnderlyingObjectDefinition, **kwargs):

    data_access_method = get_data_access_method(object_store=object_store, object_definition=object_definition, **kwargs)
    data_store = object_store.data_store

    data_store.write(stored_object.content, data_access_method=data_access_method)


def update_underlying_objects_in_store_with_changed_derived_object(object_store: ObjectStore,
                                                                   object_definition: DerivedObjectDefinition, **kwargs):

    list_of_objects_to_modify = object_definition.object_definitions_to_modify_on_update()
    for underlying_object_definition in list_of_objects_to_modify:
        ## if only one source of truth, should be fine
        stored_object = object_store.get_stored_object(underlying_object_definition, **kwargs)
        update_data_and_underlying_objects_in_store_with_changed_object(object_store=object_store,
                                                                        stored_object=stored_object,
                                                                        object_definition=underlying_object_definition, **kwargs)

def compose_object_for_object_store(object_store: ObjectStore, object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition], **kwargs) -> ObjectInObjectStore:
    if type(object_definition) is UnderlyingObjectDefinition:
        return compose_underyling_object_from_data_store(object_store=object_store, object_definition=object_definition, **kwargs)
    else:
        return compose_derived_object_from_object_store(object_store=object_store, object_definition=object_definition, **kwargs)

def compose_underyling_object_from_data_store(object_store: ObjectStore, object_definition: UnderlyingObjectDefinition, **kwargs) -> ObjectInObjectStore:
    data_access_method = get_data_access_method(object_store=object_store, object_definition=object_definition, **kwargs)
    data_store = object_store.data_store
    content = data_store.read(data_access_method)

    return ObjectInObjectStore(
        content=content,
        list_of_dependents=[],
        underlying=True,
        data_access_method=data_access_method
    )


def compose_derived_object_from_object_store(object_store: ObjectStore, object_definition: DerivedObjectDefinition, **kwargs) -> ObjectInObjectStore:
    composition_function = object_definition.composition_function
    dict_of_arguments =object_definition.dict_of_arguments_and_underlying_object_definitions
    dependent_object_definitions = list(dict_of_arguments.values())

    kwargs_to_pass = copy(kwargs)
    for keyword_name, object_definition_for_keyword in dict_of_arguments.items():
        kwargs_to_pass[keyword_name] = object_store.get(object_definition_for_keyword) ## what about keywrods eg event

    content =composition_function(**kwargs_to_pass)

    return ObjectInObjectStore(
        content=content,
        list_of_dependents=dependent_object_definitions,
        underlying=False
    )

def get_data_access_method(object_store: ObjectStore, object_definition: UnderlyingObjectDefinition, **kwargs) -> DataAccessMethod:
    data_access_callable_function = object_definition.data_store_method_function
    data_access_method = data_access_callable_function(object_store.data_api, **kwargs)

    return data_access_method


object_definition_for_list_of_cadets = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_cadets
)

object_definition_for_list_of_cadet_committee_members_with_id = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_cadets_on_committee
)

object_definition_for_list_of_cadet_committee_members = DerivedObjectDefinition(
    composition_function=create_list_of_cadet_committee_members_from_underlying_data,
    dict_of_arguments_and_underlying_object_definitions= dict(list_of_cadets=object_definition_for_list_of_cadets, list_of_cadets_with_id_on_commitee=object_definition_for_list_of_cadet_committee_members_with_id),
    list_of_object_definitions_to_modify_on_update = [object_definition_for_list_of_cadet_committee_members_with_id]
    )

object_definition_for_list_of_cadets_and_qualifications_with_ids = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_cadets_with_qualifications
)

object_definition_for_list_of_qualifications_with_ids = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_list_of_qualifications
)

object_definition_for_dict_of_qualifications_for_cadets = DerivedObjectDefinition(
    composition_function=create_dict_of_qualifications_for_cadets,
    dict_of_arguments_and_underlying_object_definitions=dict(
list_of_qualifications=object_definition_for_list_of_qualifications_with_ids,
list_of_cadets=object_definition_for_list_of_cadets,
list_of_cadets_with_ids_and_qualifications=object_definition_for_list_of_cadets_and_qualifications_with_ids
    ),
list_of_object_definitions_to_modify_on_update = [object_definition_for_list_of_cadets_and_qualifications_with_ids]
)

object_definition_for_cadets_with_ids_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_cadets_at_event,
)

object_definition_for_cadets_with_ids_and_groups_at_event = UnderlyingObjectDefinition(
    data_store_method_function=get_data_access_for_cadets_with_groups,
)

object_definition_for_cadets_with_groups_at_event = DerivedObjectDefinition(
    composition_function=0,
    dict_of_arguments_and_underlying_object_definitions=dict(

    )
)
