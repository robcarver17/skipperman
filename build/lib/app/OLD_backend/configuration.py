from app.objects.qualifications import ListOfQualifications

from app.OLD_backend.data.patrol_boats import PatrolBoatsData
from app.OLD_backend.data.dinghies import DinghiesData
from app.OLD_backend.data.qualification import QualificationData

from app.objects.abstract_objects.abstract_interface import abstractInterface


from app.objects.club_dinghies import ListOfClubDinghies
from app.objects.boat_classes import ListOfBoatClasses
from app.objects.patrol_boats import ListOfPatrolBoats



def load_list_of_club_dinghies(interface: abstractInterface) -> ListOfClubDinghies:
    dinghy_data = DinghiesData(interface.data)
    return dinghy_data.get_list_of_club_dinghies()


def load_list_of_boat_classes(interface: abstractInterface) -> ListOfBoatClasses:
    dinghy_data = DinghiesData(interface.data)

    return dinghy_data.get_list_of_boat_classes()


def load_list_of_patrol_boats(interface: abstractInterface) -> ListOfPatrolBoats:
    patrol_boat_data = PatrolBoatsData(interface.data)

    list_of_patrol_boats = patrol_boat_data.get_list_of_patrol_boats()

    return list_of_patrol_boats


def load_list_of_qualifications(interface: abstractInterface) -> ListOfQualifications:
    quali_data = QualificationData(interface.data)
    return quali_data.load_list_of_qualifications()



