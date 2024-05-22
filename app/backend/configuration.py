from app.objects.qualifications import ListOfQualifications

from app.backend.data.patrol_boats import PatrolBoatsData
from app.backend.data.dinghies import DinghiesData
from app.backend.data.qualification import QualificationData

from app.objects.abstract_objects.abstract_interface import abstractInterface


from app.objects.club_dinghies import ListOfClubDinghies
from app.objects.dinghies import ListOfBoatClasses
from app.objects.patrol_boats import ListOfPatrolBoats


def save_list_of_club_dinghies(interface: abstractInterface, list_of_boats: ListOfClubDinghies):
    dinghy_data = DinghiesData(interface.data)
    dinghy_data.save_list_of_club_dinghies(list_of_boats)

def load_list_of_club_dinghies(interface: abstractInterface) -> ListOfClubDinghies:
    dinghy_data = DinghiesData(interface.data)
    return dinghy_data.get_list_of_club_dinghies()


def add_new_club_dinghy_given_string_and_return_list(interface: abstractInterface, entry_to_add: str) -> ListOfClubDinghies:
    dinghy_data = DinghiesData(interface.data)
    list_of_boats = dinghy_data.get_list_of_club_dinghies()
    list_of_boats.add(entry_to_add)
    dinghy_data.save_list_of_club_dinghies(list_of_boats)

    return list_of_boats

def delete_club_dinghy_given_string_and_return_list(interface: abstractInterface, entry_to_delete: str) -> ListOfClubDinghies:
    dinghy_data = DinghiesData(interface.data)
    list_of_boats = dinghy_data.get_list_of_club_dinghies()
    list_of_boats.delete_given_name(entry_to_delete)
    dinghy_data.save_list_of_club_dinghies(list_of_boats)

    return list_of_boats


def modify_club_dinghy_given_string_and_return_list(interface: abstractInterface,
                                                    existing_value_as_str: str,
                                                    new_value_as_str: str) -> ListOfClubDinghies:
    dinghy_data = DinghiesData(interface.data)
    list_of_boats = dinghy_data.get_list_of_club_dinghies()
    list_of_boats.delete_given_name(existing_value_as_str)
    list_of_boats.add(new_value_as_str)
    dinghy_data.save_list_of_club_dinghies(list_of_boats)

    return list_of_boats


def load_list_of_boat_classes(interface: abstractInterface) -> ListOfBoatClasses:
    dinghy_data = DinghiesData(interface.data)

    return dinghy_data.get_list_of_boat_classes()


def save_list_of_boat_classes(interface: abstractInterface, list_of_boats: ListOfBoatClasses):
    dinghy_data = DinghiesData(interface.data)
    dinghy_data.save_list_of_boat_classes(list_of_boats)


def add_new_boat_class_given_string_and_return_list(interface: abstractInterface, entry_to_add: str) -> ListOfBoatClasses:
    dinghy_data = DinghiesData(interface.data)

    list_of_boats = dinghy_data.get_list_of_boat_classes()
    list_of_boats.add(entry_to_add)
    dinghy_data.save_list_of_boat_classes(list_of_boats)

    return list_of_boats


def delete_boat_class_given_string_and_return_list(interface: abstractInterface, entry_to_delete: str) -> ListOfBoatClasses:
    dinghy_data = DinghiesData(interface.data)

    list_of_boats = dinghy_data.get_list_of_boat_classes()
    list_of_boats.delete_given_name(entry_to_delete)
    dinghy_data.save_list_of_boat_classes(list_of_boats)

    return list_of_boats


def modify_boat_class_given_string_and_return_list(interface: abstractInterface, existing_value_as_str: str, new_value_as_str: str) -> ListOfBoatClasses:
    dinghy_data = DinghiesData(interface.data)

    list_of_boats = dinghy_data.get_list_of_boat_classes()
    list_of_boats.delete_given_name(existing_value_as_str)
    list_of_boats.add(new_value_as_str)
    dinghy_data.save_list_of_boat_classes(list_of_boats)

    return list_of_boats


def save_list_of_patrol_boats(interface: abstractInterface, list_of_boats: ListOfPatrolBoats):
    boat_data = PatrolBoatsData(interface.data)
    boat_data.save_list_of_patrol_boats(list_of_boats)


def add_new_patrol_boat_given_string_and_return_list(interface: abstractInterface, entry_to_add: str) -> ListOfPatrolBoats:
    boat_data = PatrolBoatsData(interface.data)
    list_of_patrol_boats = boat_data.get_list_of_patrol_boats()
    list_of_patrol_boats.add(entry_to_add)
    boat_data.save_list_of_patrol_boats(list_of_patrol_boats)

    return list_of_patrol_boats


def delete_patrol_boat_given_string_and_return_list(interface: abstractInterface, entry_to_delete: str) -> ListOfPatrolBoats:
    boat_data = PatrolBoatsData(interface.data)
    list_of_patrol_boats = boat_data.get_list_of_patrol_boats()
    list_of_patrol_boats.delete_given_name(entry_to_delete)
    boat_data.save_list_of_patrol_boats(list_of_patrol_boats)

    return list_of_patrol_boats


def modify_patrol_boat_given_string_and_return_list(interface: abstractInterface, existing_value_as_str: str, new_value_as_str: str) -> ListOfPatrolBoats:
    boat_data = PatrolBoatsData(interface.data)
    list_of_patrol_boats = boat_data.get_list_of_patrol_boats()
    list_of_patrol_boats.delete_given_name(existing_value_as_str)
    list_of_patrol_boats.add(new_value_as_str)
    boat_data.save_list_of_patrol_boats(list_of_patrol_boats)

    return list_of_patrol_boats


def load_list_of_patrol_boats(interface: abstractInterface) -> ListOfPatrolBoats:
    patrol_boat_data = PatrolBoatsData(interface.data)

    list_of_patrol_boats = patrol_boat_data.get_list_of_patrol_boats()

    return list_of_patrol_boats


def load_list_of_qualifications(interface: abstractInterface) -> ListOfQualifications:
    quali_data = QualificationData(interface.data)
    return quali_data.load_list_of_qualifications()

def save_list_of_qualifications(interface: abstractInterface, list_of_qualifications: ListOfQualifications):
    quali_data = QualificationData(interface.data)
    quali_data.save_list_of_qualifications(list_of_qualifications)


def add_new_qualification_given_string_and_return_list(interface: abstractInterface, entry_to_add: str) -> ListOfQualifications:
    quali_data = QualificationData(interface.data)
    list_of_qualifications = quali_data.load_list_of_qualifications()
    list_of_qualifications.add(entry_to_add)
    quali_data.save_list_of_qualifications(list_of_qualifications)

    return list_of_qualifications


def delete_qualification_given_string_and_return_list(interface: abstractInterface, entry_to_delete: str) -> ListOfQualifications:
    quali_data = QualificationData(interface.data)
    list_of_qualifications = quali_data.load_list_of_qualifications()
    list_of_qualifications.delete_given_name(entry_to_delete)
    quali_data.save_list_of_qualifications(list_of_qualifications)

    return list_of_qualifications


def modify_qualification_given_string_and_return_list(interface: abstractInterface, existing_value_as_str: str, new_value_as_str: str) -> ListOfQualifications:
    quali_data = QualificationData(interface.data)
    list_of_qualifications = quali_data.load_list_of_qualifications()
    list_of_qualifications.add(new_value_as_str)
    list_of_qualifications.delete_given_name(existing_value_as_str)
    quali_data.save_list_of_qualifications(list_of_qualifications)

    return list_of_qualifications
