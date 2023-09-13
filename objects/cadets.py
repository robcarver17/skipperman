from dataclasses import dataclass
import datetime
from typing import List
import pandas as pd

from objects.utils import create_list_of_objects_from_dataframe, data_object_as_dict

CADET_DOB_FIELD = "date_of_birth"


@dataclass
class Cadet:
    first_name: str
    surname: str
    date_of_birth: datetime.date

    def __repr__(self):
        return "%s %s (%s)" % (
            self.first_name.title(),
            self.surname.title(),
            str(self.date_of_birth),
        )

    def __eq__(self, other: "Cadet"):
        return self.id == other.id

    def as_dict(self) -> dict:
        return data_object_as_dict(self)

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
        return datetime.date.strftime(dob, "%Y_%m_%d")


class ListOfCadets(list):
    def __init__(self, list_of_cadets: List[Cadet]):
        super().__init__(list_of_cadets)

    def __repr__(self):
        return self.to_df()

    @classmethod
    def from_df(cls, passed_df: pd.DataFrame):
        list_of_cadets = create_list_of_objects_from_dataframe(Cadet, passed_df)

        return ListOfCadets(list_of_cadets)

    def to_df(self) -> pd.DataFrame:
        list_of_dicts = [cadet.as_dict() for cadet in self]

        return pd.DataFrame(list_of_dicts)
