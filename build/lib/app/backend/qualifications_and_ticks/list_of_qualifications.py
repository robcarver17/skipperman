from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.utilities.exceptions import arg_not_passed

from app.objects.qualifications import ListOfQualifications, Qualification


def add_qualification(
    interface: abstractInterface,  name_of_entry_to_add: str
):
    interface.update(
        interface.object_store.data_api.data_list_of_qualifications.add_qualification,
        qualification_name = name_of_entry_to_add)


def modify_qualification(
   interface: abstractInterface, existing_object: Qualification, new_object: Qualification
):
    interface.update(
        interface.object_store.data_api.data_list_of_qualifications.modify_qualification,
        existing_qualification_id = existing_object.id,
        updated_qualification = new_object)



def get_qualification_given_id(
    object_store: ObjectStore, id: str, default=arg_not_passed
) -> Qualification:
    list_of_qualifications = get_list_of_qualifications(object_store)
    return list_of_qualifications.qualification_given_id(id, default=default)


def get_qualification_given_name(object_store: ObjectStore, name: str) -> Qualification:
    list_of_qualifications = get_list_of_qualifications(object_store)
    return list_of_qualifications.qualification_given_name(name)


def get_list_of_qualifications(object_store: ObjectStore) -> ListOfQualifications:
    return object_store.get(object_store.data_api.data_list_of_qualifications.read)


def update_list_of_qualifications(
    interface: abstractInterface, updated_list_of_qualifications: ListOfQualifications
):
    interface.update(
        interface.object_store.data_api.data_list_of_qualifications.write,
        list_of_qualifications=updated_list_of_qualifications
    )
