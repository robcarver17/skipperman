from copy import copy

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.volunteer_skills import ListOfSkills, Skill
from app.objects.volunteers import Volunteer

from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_definitions import (
    object_definition_for_list_of_skills,
    object_definition_for_dict_of_volunteers_with_skills,
)
from app.objects.composed.volunteers_with_skills import (
    SkillsDict,
    DictOfVolunteersWithSkills,
)


def is_volunteer_qualified_as_SI(object_store: ObjectStore, volunteer: Volunteer):
    dict_of_skills = get_dict_of_existing_skills_for_volunteer(
        object_store=object_store, volunteer=volunteer
    )
    return dict_of_skills.is_SI


def add_new_volunteer_skill(object_store: ObjectStore, name_of_entry_to_add: str):
    list_of_skills = get_list_of_skills(object_store)
    list_of_skills.add(name_of_entry_to_add)
    update_list_of_skills(object_store=object_store, list_of_skills=list_of_skills)


def modify_volunteer_skill(
    object_store: ObjectStore, existing_object: Skill, new_object: Skill
):
    list_of_skills = get_list_of_skills(object_store)
    list_of_skills.modify(existing_skill=existing_object, new_skill=new_object)
    try:
        list_of_skills.check_for_duplicated_names()
    except:
        raise Exception("Duplicated names")

    update_list_of_skills(object_store=object_store, list_of_skills=list_of_skills)


def save_skills_for_volunteer(
    interface: abstractInterface, volunteer: Volunteer, dict_of_skills: SkillsDict
):
    try:
        interface.update(interface.object_store.data_api.data_list_of_volunteer_skills.save_skills_for_volunteer,
                     volunteer=volunteer, dict_of_skills=dict_of_skills)
    except Exception as e:
        interface.log_error("Error when saving skills for %s: %s" % (volunteer, str(e)))



def get_dict_of_existing_skills_for_volunteer(
    object_store: ObjectStore, volunteer: Volunteer
) -> SkillsDict:
    return object_store.get(object_store.data_api.data_list_of_volunteer_skills.get_dict_of_existing_skills_for_volunteer,
                            volunteer_id=volunteer.id)


def get_dict_of_volunteers_with_skills(
    object_store: ObjectStore,
) -> DictOfVolunteersWithSkills:
    return object_store.DEPRECATE_get(object_definition_for_dict_of_volunteers_with_skills)


def update_dict_of_volunteers_with_skills(
    object_store: ObjectStore, dict_of_volunteer_skills: DictOfVolunteersWithSkills
):
    object_store.DEPRECATE_update(
        new_object=dict_of_volunteer_skills,
        object_definition=object_definition_for_dict_of_volunteers_with_skills,
    )


def delete_volunteer_from_skills_and_return_skills(
    object_store: ObjectStore, volunteer: Volunteer, areyousure=False
) -> ListOfSkills:
    if not areyousure:
        return ListOfSkills([])
    dict_of_volunteer_skills = get_dict_of_volunteers_with_skills(object_store)
    current_skills = copy(
        dict_of_volunteer_skills.dict_of_skills_for_volunteer(
            volunteer
        ).as_list_of_skills()
    )
    dict_of_volunteer_skills.delete_all_skills_for_volunteer(volunteer)
    update_dict_of_volunteers_with_skills(
        object_store=object_store, dict_of_volunteer_skills=dict_of_volunteer_skills
    )

    return current_skills


def get_list_of_skills(object_store: ObjectStore) -> ListOfSkills:
    return object_store.DEPRECATE_get(object_definition_for_list_of_skills)


def update_list_of_skills(object_store: ObjectStore, list_of_skills: ListOfSkills):
    object_store.DEPRECATE_update(
        new_object=list_of_skills,
        object_definition=object_definition_for_list_of_skills,
    )


def add_boat_related_skill_for_volunteer(
    object_store: ObjectStore, volunteer: Volunteer
):
    dict_of_volunteer_skills = get_dict_of_volunteers_with_skills(object_store)
    dict_of_volunteer_skills.add_volunteer_driving_qualification(volunteer)
    update_dict_of_volunteers_with_skills(
        object_store=object_store, dict_of_volunteer_skills=dict_of_volunteer_skills
    )


def remove_boat_related_skill_for_volunteer(
    object_store: ObjectStore, volunteer: Volunteer
):
    dict_of_volunteer_skills = get_dict_of_volunteers_with_skills(object_store)
    dict_of_volunteer_skills.remove_volunteer_driving_qualification(volunteer)
    update_dict_of_volunteers_with_skills(
        object_store=object_store, dict_of_volunteer_skills=dict_of_volunteer_skills
    )
