from app.objects.cadets import ListOfCadets
from app.data_access.api.generic_api import GenericDataApi

SORT_BY_SURNAME = "Sort by surname"
SORT_BY_FIRSTNAME = "Sort by first name"
SORT_BY_DOB_ASC = "Sort by date of birth, ascending"
SORT_BY_DOB_DSC = "Sort by date of birth, descending"

def get_list_of_cadets(data: GenericDataApi, sort_by: str = "") -> ListOfCadets:
    master_list = data.data_list_of_cadets.read()
    if sort_by==SORT_BY_SURNAME:
        return master_list.sort_by_surname()
    elif sort_by==SORT_BY_FIRSTNAME:
        return master_list.sort_by_firstname()
    elif sort_by==SORT_BY_DOB_ASC:
        return master_list.sort_by_dob_asc()
    elif sort_by==SORT_BY_DOB_DSC:
        return master_list.sort_by_dob_desc()
    else:
        return master_list

