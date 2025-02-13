from enum import Enum
from typing import Union

from app.objects.cadets import Cadet, ListOfCadets

NO_PARTNER_REQUIRED_STR = "Singlehander"
NOT_ALLOCATED_STR = "Unallocated"
NO_PARTNERSHIP_LIST_OF_STR = [NOT_ALLOCATED_STR, NO_PARTNER_REQUIRED_STR]


def no_partnership_given_partner_id_or_str(partnership_str: str):
    return partnership_str in NO_PARTNERSHIP_LIST_OF_STR


def valid_partnership_given_partner_id_or_str(partnership_str: str):
    return not no_partnership_given_partner_id_or_str(partnership_str)


NoCadetPartner = Enum('NoCadetPartner', [NO_PARTNER_REQUIRED_STR, NOT_ALLOCATED_STR])
no_cadet_partner_required = NoCadetPartner.Singlehander
no_partner_allocated = NoCadetPartner.Unallocated



def from_cadet_id_to_partner_cadet(
    cadet_id: str, list_of_cadets: ListOfCadets
) -> Union[Cadet, NoCadetPartner]:
    if cadet_id == NOT_ALLOCATED_STR:
        return no_partner_allocated
    elif cadet_id == NO_PARTNER_REQUIRED_STR:
        return no_cadet_partner_required
    else:
        return list_of_cadets.cadet_with_id(cadet_id)


def from_partner_cadet_to_id_or_string(partner_cadet: Union[Cadet, NoCadetPartner]):
    if partner_cadet is no_partner_allocated:
        return NOT_ALLOCATED_STR
    elif partner_cadet is no_cadet_partner_required:
        return NO_PARTNER_REQUIRED_STR

    return partner_cadet.id


def no_partnership_given_partner_cadet_as_str(partner_as_str: str):
    return partner_as_str in [NO_PARTNER_REQUIRED_STR, NOT_ALLOCATED_STR]


def no_partnership_object_given_str(partner_as_str: str):
    if partner_as_str == NO_PARTNER_REQUIRED_STR:
        return no_cadet_partner_required
    elif partner_as_str == NOT_ALLOCATED_STR:
        return no_partner_allocated
    else:
        raise Exception("Don't know how to process %s" % partner_as_str)


def no_partnership_given_partner_cadet(partner: Union[Cadet, NoCadetPartner]):
    if partner is no_cadet_partner_required:
        return True
    elif partner is no_partner_allocated:
        return True
    else:
        return False


def valid_partnership_given_partner_cadet(partner: Union[Cadet, object]):
    return not no_partnership_given_partner_cadet(partner)
