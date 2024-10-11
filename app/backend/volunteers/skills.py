from app.objects.volunteer_skills import ListOfSkills, Skill
from app.objects.volunteers import Volunteer

from app.data_access.store.object_store import ObjectStore
from app.data_access.store.object_definitions import  \
    object_definition_for_list_of_skills, object_definition_for_volunteers_with_skills
from app.objects.composed.volunteers_with_skills import SkillsDict, ListOfVolunteersWithSkills


def add_new_volunteer_skill(object_store: ObjectStore,name_of_entry_to_add: str):
    list_of_skills = get_list_of_skills(object_store)
    list_of_skills.add(name_of_entry_to_add)
    update_list_of_skills(object_store=object_store, list_of_skills=list_of_skills)

def modify_volunteer_skill(object_store: ObjectStore, existing_object: Skill, new_object: Skill):
    list_of_skills = get_list_of_skills(object_store)
    list_of_skills.modify(existing_skill=existing_object, new_skill=new_object)
    try:
        list_of_skills.check_for_duplicated_names()
    except:
        raise Exception("Duplicated names")

    update_list_of_skills(object_store=object_store, list_of_skills=list_of_skills)

def save_skills_for_volunteer(
        object_store: ObjectStore,  volunteer: Volunteer, dict_of_skills: SkillsDict
):
    list_of_volunteer_skills = get_list_of_volunteers_with_skills(object_store)
    list_of_volunteer_skills.replace_skills_for_volunteer_with_new_skills_dict(volunteer=volunteer, dict_of_skills=dict_of_skills)
    update_list_of_volunteers_with_skills(object_store=object_store, list_of_volunteer_skills=list_of_volunteer_skills)

def get_dict_of_existing_skills_for_volunteer(object_store: ObjectStore, volunteer: Volunteer) -> SkillsDict:
    list_of_volunteer_skills = get_list_of_volunteers_with_skills(object_store)
    list_of_skills = get_list_of_skills(object_store)
    dict_of_skills = list_of_volunteer_skills.dict_of_skills_for_volunteer(volunteer)
    dict_of_skills.pad_with_missing_skills(list_of_skills)

    return dict_of_skills



def get_list_of_volunteers_with_skills(object_store: ObjectStore) -> ListOfVolunteersWithSkills:
    return object_store.get(object_definition_for_volunteers_with_skills)


def update_list_of_volunteers_with_skills(object_store: ObjectStore, list_of_volunteer_skills:  ListOfVolunteersWithSkills):
    object_store.update(new_object=list_of_volunteer_skills, object_definition=object_definition_for_volunteers_with_skills)


def get_list_of_skills(object_store: ObjectStore) -> ListOfSkills:
    return object_store.get(object_definition_for_list_of_skills)

def update_list_of_skills(object_store: ObjectStore, list_of_skills: ListOfSkills):
    object_store.update(new_object=list_of_skills, object_definition=object_definition_for_list_of_skills)

