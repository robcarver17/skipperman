from copy import copy
from dataclasses import dataclass
from typing import List

import pandas as pd
from app.objects.groups import Group

from app.objects.cadets import ListOfCadets

from app.objects.day_selectors import DictOfDaySelectors
from app.objects.composed.ticksheet import DictOfCadetsAndTicksWithinQualification
from app.objects.composed.ticks_for_qualification import TicksForQualification


@dataclass
class LabelledTickSheet:
    df: pd.DataFrame
    list_of_cadets: ListOfCadets
    cadets_in_columns: bool = False
    qualification_name: str = ""
    group_name: str = ""

    def from_existing_replace_df(self, new_df: pd.DataFrame):
        return LabelledTickSheet(
            df=new_df,
            list_of_cadets=self.list_of_cadets,
            cadets_in_columns=self.cadets_in_columns,
            qualification_name=self.qualification_name,
            group_name=self.group_name,
        )

    def transpose(self):
        now_cadets_in_columns = not self.cadets_in_columns
        new_version = copy(self)
        new_version.df = new_version.df.transpose()
        new_version.cadets_in_columns = now_cadets_in_columns

        return new_version

    def add_attendance_data(self, attendance_data: DictOfDaySelectors):
        attendance = attendance_data.as_pd_data_frame()
        dummy_multindex = [[""] * len(attendance.columns), attendance.columns]
        attendance.columns = dummy_multindex
        qual_multindex = pd.MultiIndex.from_tuples(
            [("%s:" % self.qualification_name.upper(), "")]
        )
        qual_row = pd.DataFrame("", index=qual_multindex, columns=self.df.columns)
        qual_column = pd.DataFrame("", index=self.df.index, columns=qual_multindex)

        if self.cadets_in_columns:
            attendance = attendance.transpose()
            attendance.columns = self.df.columns
            new_df = pd.concat([attendance, qual_row, self.df], axis=0)
        else:
            attendance.index = self.df.index
            new_df = pd.concat([attendance, qual_column, self.df], axis=1)

        return self.from_existing_replace_df(new_df)

    def add_health_notes(self, health_notes: List[str]):
        print(health_notes)
        health_multindex = pd.MultiIndex.from_tuples([("", "Medical notes")])
        if self.cadets_in_columns:
            health_row = pd.DataFrame(
                health_notes, index=health_multindex, columns=self.df.columns
            )
            print(health_row)
            new_df = pd.concat([self.df, health_row], axis=0)
        else:
            health_column = pd.DataFrame(
                health_notes, index=self.df.index, columns=health_multindex
            )
            print(health_column)
            new_df = pd.concat([self.df, health_column], axis=1)

        return self.from_existing_replace_df(new_df)

    def add_qualification_and_group_header(self):
        qual_multindex = pd.MultiIndex.from_tuples(
            [("%s:" % self.qualification_name.upper(), self.group_name)]
        )

        if self.cadets_in_columns:
            qual_row = pd.DataFrame("", index=qual_multindex, columns=self.df.columns)
            new_df = pd.concat([qual_row, self.df], axis=0)
        else:
            qual_column = pd.DataFrame("", index=self.df.index, columns=qual_multindex)
            new_df = pd.concat([qual_column, self.df], axis=1)

        return self.from_existing_replace_df(new_df)

    def add_club_boat_asterix(self, list_of_club_boat_bool: List[bool]):
        new_df = copy(self.df)
        list_of_club_boat_asterix = [
            "*" if yes else " " for yes in list_of_club_boat_bool
        ]
        if self.cadets_in_columns:
            new_df.columns = [
                column + star
                for column, star in zip(new_df.columns, list_of_club_boat_asterix)
            ]
        else:
            new_df.index = [
                column + star
                for column, star in zip(new_df.index, list_of_club_boat_asterix)
            ]

        return self.from_existing_replace_df(new_df)


def labelled_tick_sheet_from_ticksheet_data(
    ticksheet_data: DictOfCadetsAndTicksWithinQualification, group: Group
) -> LabelledTickSheet:
    df = raw_tick_sheet_from_ticksheet_data(ticksheet_data)

    list_of_cadets = ticksheet_data.list_of_cadets
    df.index = list_of_cadets.list_of_names()

    list_of_substage_names = (
        ticksheet_data.list_of_substage_names_aligned_to_tick_sheet_items
    )
    list_of_tick_item_names = (
        ticksheet_data.list_of_tick_sheet_items_for_this_qualification
    )
    df.columns = [list_of_substage_names, list_of_tick_item_names]

    return LabelledTickSheet(
        df=df,
        list_of_cadets=list_of_cadets,
        qualification_name=ticksheet_data.qualification.name,
        group_name=group.name,
        cadets_in_columns=False,
    )


def raw_tick_sheet_from_ticksheet_data(
    ticksheet_data: DictOfCadetsAndTicksWithinQualification,
) -> pd.DataFrame:
    return pd.DataFrame(
        dict(
            [
                (cadet, dict_of_itemnames_and_ticks(ticks_for_cadet))
                for cadet, ticks_for_cadet in ticksheet_data.items()
            ]
        )
    ).transpose()


def dict_of_itemnames_and_ticks(ticks_for_cadet: TicksForQualification) -> dict:
    items_and_ticks = ticks_for_cadet.all_tick_sheet_items_and_ticks()
    return items_and_ticks.as_dict_of_str()
