from dataclasses import dataclass
import datetime

from objects.generic import GenericSkipperManObject, GenericListOfObjects
from objects.utils import transform_str_from_date


@dataclass
class Cadet(GenericSkipperManObject):
    first_name: str
    surname: str
    date_of_birth: datetime.date

    def __repr__(self):
        return "%s %s (%s)" % (
            self.first_name.title(),
            self.surname.title(),
            str(self.date_of_birth),
        )

    @property
    def id(self) -> str:
        return (
            self.first_name.lower()
            + "_"
            + self.surname.lower()
            + "_"
            + self._date_of_birth_as_str
        )

    @property
    def _date_of_birth_as_str(self) -> str:
        dob = self.date_of_birth
        return transform_str_from_date(dob)


class ListOfCadets(GenericListOfObjects):
    @property
    def _object_class_contained(self):
        return Cadet
