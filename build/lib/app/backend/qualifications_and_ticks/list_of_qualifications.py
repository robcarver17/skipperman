from app.data_access.store.object_store import ObjectStore

from app.objects.qualifications import ListOfQualifications, Qualification
from app.data_access.store.object_definitions import object_definition_for_list_of_qualifications


def add_new_qualification(
    object_store: ObjectStore, name_of_entry_to_add: str
) -> ListOfQualifications:
    list_of_qualifications = get_list_of_qualifications(object_store)
    list_of_qualifications.add(name_of_entry_to_add)
    update_list_of_qualifications(object_store=object_store, updated_list_of_qualifications=list_of_qualifications)

    return list_of_qualifications




def modify_qualification(
    object_store: ObjectStore, existing_object: Qualification, new_object: Qualification
):
    list_of_qualifications = get_list_of_qualifications(object_store)
    list_of_qualifications.replace(existing_qualification=existing_object, new_qualification = new_object)
    try:
        list_of_qualifications.check_for_duplicated_names()
    except:
        raise Exception("Duplicate names")

    update_list_of_qualifications(object_store=object_store, updated_list_of_qualifications=list_of_qualifications)


def get_qualification_given_id(object_store: ObjectStore, id: str) -> Qualification:
    list_of_qualifications = get_list_of_qualifications(object_store)
    return list_of_qualifications.object_with_id(id)


def get_qualification_given_name(object_store: ObjectStore, name: str) -> Qualification:
    list_of_qualifications = get_list_of_qualifications(object_store)
    return list_of_qualifications.qualification_given_name(name)

def get_list_of_qualifications(object_store: ObjectStore) -> ListOfQualifications:
    return object_store.get(object_definition_for_list_of_qualifications)

def update_list_of_qualifications(object_store: ObjectStore, updated_list_of_qualifications:ListOfQualifications):
    object_store.update(new_object=updated_list_of_qualifications, object_definition=object_definition_for_list_of_qualifications)

