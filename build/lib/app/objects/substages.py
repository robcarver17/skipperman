from dataclasses import dataclass
from typing import List

from app.objects.exceptions import arg_not_passed, missing_data
from app.objects.generic_list_of_objects import GenericListOfObjectsWithIds
from app.objects.generic_objects import GenericSkipperManObjectWithIds


@dataclass
class TickSubStage(GenericSkipperManObjectWithIds):
    name: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class ListOfTickSubStages(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return TickSubStage

    def idx_given_name(self, name: str):
        id = self.id_given_name(name)
        if id is missing_data:
            return missing_data
        return self.index_of_id(id)

    def id_given_name(self, name: str):
        id = [item.id for item in self if item.name == name]

        if len(id) == 0:
            return missing_data
        elif len(id) > 1:
            raise Exception(
                "Found more than one substage with same name should be impossible"
            )

        return str(id[0])

    def add(self, name: str):
        sub_stage = TickSubStage(name=name)
        try:
            assert name not in self.list_of_names()
        except:
            raise Exception("Can't add duplicate substage %s already exists" % name)
        sub_stage.id = self.next_id()

        self.append(sub_stage)

    def modify_name_of_substage_where_new_name_also_does_not_exist(
        self, substage_id: str, new_name: str
    ):
        items = [item for item in self if item.id == substage_id]
        assert len(items) == 1

        item = items[0]
        item.name = new_name

    def list_of_names(self):
        return [sub_stage.name for sub_stage in self]


PLACEHOLDER_TICK_SHEET_ID = str(-9999)


@dataclass
class TickSheetItem(GenericSkipperManObjectWithIds):
    name: str
    stage_id: str
    substage_id: str
    id: str = arg_not_passed

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash("_".join([self.name, self.stage_id, self.substage_id]))

    @classmethod
    def create_placeholder(cls, stage_id: str, substage_id: str):
        return cls(
            name="",
            substage_id=substage_id,
            stage_id=stage_id,
            id=PLACEHOLDER_TICK_SHEET_ID,
        )

    @property
    def is_placeholder(self):
        return self.id == PLACEHOLDER_TICK_SHEET_ID


class ListOfTickSheetItems(GenericListOfObjectsWithIds):
    @property
    def _object_class_contained(self):
        return TickSheetItem

    def switch_all_instances_of_substage_for_qualification(
        self, existing_substage_id: str, stage_id: str, new_substage_id: str
    ):
        for item in self:
            if item.substage_id == existing_substage_id and item.stage_id == stage_id:
                item.substage_id = new_substage_id

    def only_this_qualification_has_this_substage(
        self, substage_id: str, stage_id: str
    ) -> bool:
        substage_exists_in_another_stage = [
            True
            for item in self
            if (not item.stage_id == stage_id) and (item.substage_id == substage_id)
        ]

        return not any(substage_exists_in_another_stage)

    def modify_ticksheet_item_name(self, tick_item_id: str, new_item_name: str):
        idx = self.index_of_id(tick_item_id)
        item = self[idx]
        item.name = new_item_name

    def add(self, name: str, stage_id: str, substage_id: str):
        ## Duplicates aren't a problem... are they?
        try:
            assert not self.name_and_id_already_exists(
                name=name, substage_id=substage_id, stage_id=stage_id
            )
        except:
            raise Exception(
                "Can't create duplicate tick sheet item name '%s' for existing substage and stage"
                % name
            )

        id = self.next_id()
        self.append(
            TickSheetItem(name=name, stage_id=stage_id, substage_id=substage_id, id=id)
        )
        self.delete_placeholder_if_only_entry(
            stage_id=stage_id, substage_id=substage_id
        )

    def name_and_id_already_exists(self, name: str, stage_id: str, substage_id: str):
        list_of_items = [
            item
            for item in self
            if item.name == name
            and item.substage_id == substage_id
            and item.stage_id == stage_id
        ]
        return len(list_of_items) > 0

    def delete_placeholder_if_only_entry(self, stage_id: str, substage_id: str):
        if self.placeholders_exist(stage_id=stage_id, substage_id=substage_id):
            self.delete_placeholder(stage_id=stage_id, substage_id=substage_id)

    def delete_placeholder(self, stage_id: str, substage_id: str):
        list_of_items = [
            item
            for item in self
            if item.stage_id == stage_id
            and item.substage_id == substage_id
            and item.is_placeholder
        ]
        assert len(list_of_items) == 1
        self.remove(list_of_items[0])

    def add_placeholder(self, stage_id: str, substage_id: str):
        try:
            assert not self.placeholders_exist(
                stage_id=stage_id, substage_id=substage_id
            )
        except:
            raise Exception("Can't add more than once placeholder for a substage")

        self.append(
            TickSheetItem.create_placeholder(stage_id=stage_id, substage_id=substage_id)
        )

    def placeholders_exist(self, stage_id: str, substage_id: str):
        return any(
            [
                True
                for item in self
                if item.stage_id == stage_id
                and item.substage_id == substage_id
                and item.is_placeholder
            ]
        )

    def subset_for_substage_id_ignoring_placeholders(self, substage_id: str):
        new_list = [
            item
            for item in self
            if item.substage_id == substage_id and not item.is_placeholder
        ]

        return ListOfTickSheetItems(new_list)

    def subset_for_qualification_stage_id(
        self, stage_id: str, ignore_placeholders: bool = True
    ) -> "ListOfTickSheetItems":
        new_list = [item for item in self if item.stage_id == stage_id]
        if ignore_placeholders:
            new_list = [item for item in new_list if not item.is_placeholder]

        return ListOfTickSheetItems(new_list)

    def list_of_substage_ids(self) -> List[str]:
        return [item.substage_id for item in self]
