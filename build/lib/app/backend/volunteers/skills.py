from copy import copy

from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.volunteer_skills import ListOfSkills, Skill
from app.objects.volunteers import Volunteer

from app.data_access.store.object_store import ObjectStore
from app.objects.composed.volunteers_with_skills import (
    SkillsDict,
    DictOfVolunteersWithSkills,
)

def is_volunteer_qualified_as_SI(object_store: ObjectStore, volunteer: Volunteer):
    dict_of_skills = get_dict_of_existing_skills_for_volunteer(
        object_store=object_store, volunteer=volunteer
    )
    return dict_of_skills.is_SI


def add_new_volunteer_skill(interface: abstractInterface,  name_of_entry_to_add: str):
    skill = Skill(name_of_entry_to_add)
    try:

        interface.update(
            interface.object_store.data_api.data_list_of_skills.add_new_skill,
            new_skill = skill
        )
    except Exception as e:
        interface.log_error("Can't add %s as %s" % (name_of_entry_to_add, str(e)))


def modify_volunteer_skill(
        interface: abstractInterface, existing_object: Skill, new_object: Skill
):
    try:
        interface.update(
            interface.object_store.data_api.data_list_of_skills.modify_skill,
            original_skill = existing_object,
            new_skill = new_object
        )
    except Exception as e:
        interface.log_error("Can't modify %s to %s error: %s" % (existing_object, new_object, str(e)))


def save_skills_for_volunteer(
    interface: abstractInterface, volunteer: Volunteer, dict_of_skills: SkillsDict
):
    try:
        interface.update(interface.object_store.data_api.data_list_of_volunteer_skills.update_skills_for_volunteer,
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
    return object_store.get(
        object_store.data_api.data_list_of_volunteer_skills.get_dict_of_volunteers_with_skills
    )



def delete_volunteer_from_skills_and_return_skills(
    interface: abstractInterface, volunteer: Volunteer, areyousure=False
) -> ListOfSkills:
    object_store = interface.object_store
    if not areyousure:
        return ListOfSkills([])
    dict_of_volunteer_skills = get_dict_of_volunteers_with_skills(object_store)
    current_skills = copy(
        dict_of_volunteer_skills.dict_of_skills_for_volunteer(
            volunteer
        ).as_list_of_skills()
    )
    delete_volunteer_skills(interface=interface, volunteer=volunteer, areyousure=areyousure)

    return current_skills


def delete_volunteer_skills(
    interface: abstractInterface, volunteer: Volunteer, areyousure=False
) :
    if not areyousure:
        return
    interface.update(
        interface.object_store.data_api.data_list_of_volunteer_skills.delete_volunteer_skills,
        volunteer_id=volunteer.id
    )

def get_list_of_skills(object_store: ObjectStore) -> ListOfSkills:
    return object_store.get(object_store.data_api.data_list_of_skills.read)


def update_list_of_skills(interface: abstractInterface, list_of_skills: ListOfSkills):
    interface.update(
        interface.object_store.data_api.data_list_of_skills.write,
        list_of_skills=list_of_skills
    )


def add_boat_related_skill_for_volunteer(
    interface: abstractInterface, volunteer: Volunteer
):
    list_of_skills = get_list_of_skills(interface.object_store)
    PB2_skill = list_of_skills.PB2_skill
    add_skill_for_volunteer(interface=interface, volunteer=volunteer, skill=PB2_skill)

def remove_boat_related_skill_for_volunteer(
        interface: abstractInterface, volunteer: Volunteer
):
    list_of_skills = get_list_of_skills(interface.object_store)
    PB2_skill = list_of_skills.PB2_skill
    remove_skill_for_volunteer(interface=interface, volunteer=volunteer, skill=PB2_skill)


def remove_skill_for_volunteer(
        interface: abstractInterface, volunteer: Volunteer, skill: Skill
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteer_skills.remove_skill_for_volunteer,
        volunteer_id=volunteer.id,
        skill_id=skill.id
    )


def add_skill_for_volunteer(
    interface: abstractInterface, volunteer: Volunteer, skill: Skill
):
    interface.update(
        interface.object_store.data_api.data_list_of_volunteer_skills.add_skill_for_volunteer,
        volunteer_id=volunteer.id,
        skill_id=skill.id
    )
