from dataclasses import dataclass
from typing import List

from app.objects.utilities.exceptions import (
    arg_not_passed,
    MissingData,
)
from app.objects.utilities.generic_list_of_objects import GenericListOfObjectsWithIds
from app.objects.utilities.generic_objects import GenericSkipperManObjectWithIds


@dataclass
class TickSubStage(GenericSkipperManObjectWithIds):
    name: str
    stage_id: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


from app.objects.utilities.generic_list_of_objects import (
    get_unique_object_with_attr_in_list,
    index_not_found,
)


class ListOfTickSubStages(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return TickSubStage

    def substages_for_qualification_id(self, qualification_id):
        return ListOfTickSubStages(
            [item for item in self if item.stage_id==qualification_id]
        )

    def id_given_name(self, name: str, default=arg_not_passed):
        substage = self.substage_given_name(name, default=index_not_found)
        if substage is index_not_found:
            if default is arg_not_passed:
                raise MissingData
            else:
                return default

        return substage.id

    def substage_given_name(self, name: str, default=arg_not_passed):
        return get_unique_object_with_attr_in_list(
            some_list=self, attr_name="name", attr_value=name, default=default
        )

    def substage_given_id(self, id: str, default=arg_not_passed) -> TickSubStage:
        return self.object_with_id(id, default=default)



@dataclass
class TickSheetItem(GenericSkipperManObjectWithIds):
    name: str
    substage_id: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash("_".join([self.name, self.substage_id]))



class ListOfTickSheetItems(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return TickSheetItem

    def tick_sheet_item_with_id(self, item_id: str, default=arg_not_passed):
        return self.object_with_id(item_id, default=default)



    def subset_for_substage_id(self, substage_id: str):
        new_list = [
            item
            for item in self
            if item.substage_id == substage_id
        ]

        return ListOfTickSheetItems(new_list)

    def list_of_substage_ids(self) -> List[str]:
        return [item.substage_id for item in self]
