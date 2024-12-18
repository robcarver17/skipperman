from dataclasses import dataclass
from typing import List, Dict

from app.objects.cadet_volunteer_connections_with_ids import (
    ListOfCadetVolunteerAssociationsWithIds,
)
from app.objects.exceptions import MissingData, MultipleMatches
from app.objects.volunteers import Volunteer, ListOfVolunteers
from app.objects.cadets import Cadet, ListOfCadets


@dataclass
class CadetVolunteerAssociation:
    cadet: Cadet
    volunteer: Volunteer


class ListOfCadetVolunteerAssociations(List[CadetVolunteerAssociation]):
    def __init__(
        self,
        list_of_cadets: ListOfCadets,
        list_of_volunteers: ListOfVolunteers,
        list_of_cadet_volunteer_associations_with_ids: ListOfCadetVolunteerAssociationsWithIds,
    ):
        list_of_associations = create_raw_list_of_cadet_volunteer_associations_from_underlying_data(
            list_of_cadets=list_of_cadets,
            list_of_volunteers=list_of_volunteers,
            list_of_cadet_volunteer_associations_with_ids=list_of_cadet_volunteer_associations_with_ids,
        )
        self.list_of_cadet_volunteer_associations_with_ids = (
            list_of_cadet_volunteer_associations_with_ids
        )
        super().__init__(list_of_associations)

    def add_association(self, cadet: Cadet, volunteer: Volunteer):
        try:
            self.get_association(cadet=cadet, volunteer=volunteer)
        except MissingData:
            ## What we would expect
            self._add_association_without_checking(cadet=cadet, volunteer=volunteer)


    def _add_association_without_checking(self, cadet: Cadet, volunteer: Volunteer):
        self.append(CadetVolunteerAssociation(cadet=cadet, volunteer=volunteer))
        self.list_of_cadet_volunteer_associations_with_ids.add(
            cadet_id=cadet.id, volunteer_id=volunteer.id
        )

    def delete_association(self, cadet: Cadet, volunteer: Volunteer):
        association = self.get_association(cadet=cadet, volunteer=volunteer)
        self.remove(association)
        list_of_cadet_volunteer_associations_with_ids = (
            self.list_of_cadet_volunteer_associations_with_ids
        )
        list_of_cadet_volunteer_associations_with_ids.delete(
            cadet_id=cadet.id, volunteer_id=volunteer.id
        )

    def get_association(
        self, cadet: Cadet, volunteer: Volunteer
    ) -> CadetVolunteerAssociation:
        matching = [
            association
            for association in self
            if association.cadet.id == cadet.id
            and association.volunteer.id == volunteer.id
        ]
        if len(matching) == 0:
            raise MissingData("Nothing to delete")
        elif len(matching) > 1:
            raise MultipleMatches()
        else:
            return matching[0]

    def list_of_volunteers_associated_with_cadet(
        self, cadet: Cadet
    ) -> ListOfVolunteers:
        return ListOfVolunteers(
            [
                association.volunteer
                for association in self
                if association.cadet.id == cadet.id
            ]
        )

    def list_of_cadets_associated_with_volunteer(
        self, volunteer: Volunteer
    ) -> ListOfCadets:
        return ListOfCadets(
            [
                association.cadet
                for association in self
                if association.volunteer.id == volunteer.id
            ]
        )

    @property
    def list_of_volunteers(self):
        return ListOfVolunteers(list(set([item.volunteer for item in self])))

    @property
    def list_of_cadets(self):
        return ListOfCadets(list(set([item.cadet for item in self])))


    @property
    def list_of_cadet_volunteer_associations_with_ids(
        self,
    ) -> ListOfCadetVolunteerAssociationsWithIds:
        return self._list_of_cadet_volunteer_associations_with_ids

    @list_of_cadet_volunteer_associations_with_ids.setter
    def list_of_cadet_volunteer_associations_with_ids(
        self,
        list_of_cadet_volunteer_associations_with_ids: ListOfCadetVolunteerAssociationsWithIds,
    ):
        self._list_of_cadet_volunteer_associations_with_ids = (
            list_of_cadet_volunteer_associations_with_ids
        )


def create_list_of_cadet_volunteer_associations_from_underlying_data(
    list_of_cadets: ListOfCadets,
    list_of_volunteers: ListOfVolunteers,
    list_of_cadet_volunteer_associations_with_ids: ListOfCadetVolunteerAssociationsWithIds,
) -> ListOfCadetVolunteerAssociations:
    return ListOfCadetVolunteerAssociations(
        list_of_cadets=list_of_cadets,
        list_of_volunteers=list_of_volunteers,
        list_of_cadet_volunteer_associations_with_ids=list_of_cadet_volunteer_associations_with_ids,
    )


def create_raw_list_of_cadet_volunteer_associations_from_underlying_data(
    list_of_cadets: ListOfCadets,
    list_of_volunteers: ListOfVolunteers,
    list_of_cadet_volunteer_associations_with_ids: ListOfCadetVolunteerAssociationsWithIds,
) -> List[CadetVolunteerAssociation]:
    return [
        CadetVolunteerAssociation(
            cadet=list_of_cadets.cadet_with_id(association.cadet_id),
            volunteer=list_of_volunteers.volunteer_with_id(association.volunteer_id),
        )
        for association in list_of_cadet_volunteer_associations_with_ids
    ]


class DictOfCadetsAssociatedWithVolunteer(Dict[Volunteer, ListOfCadets]):
    pass

def compose_dict_of_cadets_associated_with_volunteers(list_of_cadet_volunteer_associations: ListOfCadetVolunteerAssociations) -> DictOfCadetsAssociatedWithVolunteer:
    list_of_volunteers = list_of_cadet_volunteer_associations.list_of_volunteers

    return DictOfCadetsAssociatedWithVolunteer(
        [(
            volunteer, list_of_cadet_volunteer_associations.list_of_cadets_associated_with_volunteer(volunteer)
        ) for volunteer in list_of_volunteers]
    )


class DictOfVolunteersAssociatedWithCadet(Dict[Cadet, ListOfVolunteers]):
    pass

def compose_dict_of_volunteers_associated_with_cadets(list_of_cadet_volunteer_associations: ListOfCadetVolunteerAssociations) -> DictOfVolunteersAssociatedWithCadet:
    list_of_cadets = list_of_cadet_volunteer_associations.list_of_cadets

    return DictOfVolunteersAssociatedWithCadet(
        [
            (cadet, list_of_cadet_volunteer_associations.list_of_volunteers_associated_with_cadet(cadet))
            for cadet in list_of_cadets
        ]
    )