
from dataclasses import dataclass

from app.data_access.store.object_definitions import DerivedObjectDefinition, UnderlyingObjectDefinition, \
    IterableObjectDefinition

NO_OBJECT = object()


@dataclass
class DefinitionWithArgs:
    object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition, IterableObjectDefinition]
    kwargs: dict

    @property
    def key(self):
        return get_store_key(self.object_definition, **self.kwargs)

    def __hash__(self):
        return hash(self.key)

@dataclass
class CachedDataItem:
    contents: [object, dict] ## dict if iterated
    definition_with_args: DefinitionWithArgs
    changed: bool = False

    @property
    def object_definition(self):
        return self.definition_with_args.object_definition

    @property
    def kwargs(self):
        return self.definition_with_args.kwargs

    @property
    def key(self):
        return self.definition_with_args.key

    @property
    def is_underyling_object(self):
        return type(self.object_definition) is UnderlyingObjectDefinition


def get_store_key(
        object_definition: [DerivedObjectDefinition, UnderlyingObjectDefinition, IterableObjectDefinition],
        **kwargs
):
    key = object_definition.key + str(kwargs)

    return key
