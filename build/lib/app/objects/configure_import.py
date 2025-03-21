import datetime
from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from app.objects.exceptions import missing_data


@dataclass
class ConfigForSkillImportOneSkill:
    valid_from_column_name: str = ""
    expires_column_name: str = ""

    def all_columns_for_csv(self):
        my_columns = [self.expires_column_name, self.valid_from_column_name]
        my_columns_no_empty= [column for column in my_columns if len(column)>0]

        return my_columns_no_empty

@dataclass
class ImportSkillsconfig:
    volunteer_first_name_column: str
    volunteer_surname_column: str
    date_format: str
    dict_of_skill_names_and_configs: Dict[str, ConfigForSkillImportOneSkill]

    def all_columns_for_csv(self):
        my_columns = [self.volunteer_first_name_column, self.volunteer_surname_column]
        for skills in self.dict_of_skill_names_and_configs.values():
            my_columns+=skills.all_columns_for_csv()

        return my_columns

    @property
    def names_of_skills(self):
        return list(self.dict_of_skill_names_and_configs.keys())

def from_skills_dict_in_import_config_to_import_config(config_from_file: dict) -> ImportSkillsconfig:
    return ImportSkillsconfig(
        volunteer_first_name_column=config_from_file['first_name'],
        volunteer_surname_column = config_from_file['last_name'],
        date_format=config_from_file['date_format'],
        dict_of_skill_names_and_configs=from_skills_dict_in_import_config_to_dict_of_skills_and_config(
            config_from_file['skills']
        )
    )


def from_skills_dict_in_import_config_to_dict_of_skills_and_config(skills_config_from_file: dict) -> Dict[str, ConfigForSkillImportOneSkill]:
    return dict([
        (skill_name,
        config_for_skill_from_dict(config))
        for skill_name, config in skills_config_from_file.items()])


def config_for_skill_from_dict(some_dict: dict):
    return ConfigForSkillImportOneSkill(
        valid_from_column_name=some_dict.get('valid_from', ''),
        expires_column_name=some_dict.get('expires', '')
    )



class RowInImportedSkillsFile:
    def __init__(self, series: pd.Series, skills_config: ImportSkillsconfig):
        self.series = series
        self.skills_config = skills_config

    def volunteer_name_as_tuple(self):
        skills_config = self.skills_config
        return self.series[skills_config.volunteer_first_name_column], self.series[skills_config.volunteer_surname_column]

    def empty_name(self):
        name_as_tuple = self.volunteer_name_as_tuple()
        name = "".join(name_as_tuple)
        name=name.strip(" ")
        return len(name)==0

    def is_skill_valid(self, skill_name):
        valid_from_date, valid_to_date = self.start_and_end_dates_for_skill(skill_name, default=missing_data)

        if valid_from_date is missing_data and valid_to_date is missing_data:
            return False ## hasn't got skill

        today = datetime.date.today()

        if valid_from_date is not missing_data:
            if today < valid_from_date:
                return False

        if valid_to_date is not missing_data:
            if today>valid_to_date:
                return False

        return True

    def explain_why_skill_invalid(self, skill_name: str):
        valid_from_date, valid_to_date = self.start_and_end_dates_for_skill(skill_name, default=missing_data)
        from_column = self.skills_config.dict_of_skill_names_and_configs[skill_name].valid_from_column_name
        to_column = self.skills_config.dict_of_skill_names_and_configs[skill_name].expires_column_name

        today = datetime.date.today()

        msg = ''
        if not valid_from_date is missing_data:
            if today < valid_from_date:
                msg+="Have not yet reached start date %s (in column %s). " % (valid_from_date, from_column)

        if not valid_to_date is missing_data:
            if today>valid_to_date:
                msg+= "Passed end date %s (in column %s)" % (valid_to_date, to_column)

        if valid_from_date is missing_data and valid_to_date is missing_data:
            msg = "Neither date column %s or %s filled in so assume do not have" % (from_column, to_column)

        if len(msg)==0:
            raise Exception("%s is valid!" % skill_name)

        return msg

    def explain_why_is_valid(self, skill_name: str):
        valid_from_date, valid_to_date = self.start_and_end_dates_for_skill(skill_name, default=missing_data)
        from_column = self.skills_config.dict_of_skill_names_and_configs[skill_name].valid_from_column_name
        to_column = self.skills_config.dict_of_skill_names_and_configs[skill_name].expires_column_name

        msg = ''
        if not valid_from_date is missing_data:
            msg+= "Valid since date %s (column %s). " % (valid_from_date, from_column)

        if not valid_to_date is missing_data:
            msg+= "Valid until date %s (column %s). " % (valid_to_date, to_column)

        if len(msg)==0:
            raise Exception("%s is invalid!" % skill_name)

        return msg


    def start_and_end_dates_for_skill(self, skill_name:str, default = missing_data):
        valid_from_date = self.a_date_for_skill(skill_name, 'valid_from_column_name', default)
        valid_to_date = self.a_date_for_skill(skill_name, 'expires_column_name', default)

        return valid_from_date, valid_to_date

    def a_date_for_skill(self, skill_name:str, date_attr:str, default = missing_data):
        config = self.skills_config.dict_of_skill_names_and_configs.get(skill_name)
        valid_from_column = getattr(config, date_attr)
        if len(valid_from_column)==0:
            return default

        date_as_str = self.series[valid_from_column]
        if len(date_as_str)==0:
            return default

        date_format =  self.skills_config.date_format
        try:
            as_datetime = datetime.datetime.strptime(date_as_str,date_format)
        except:
            raise Exception("Date %s not in expected format %s eg %s" % (date_as_str, date_format, datetime.date.today().strftime(date_format)))

        as_date = as_datetime.date()

        return as_date


class ListOfRowsInSkillsFile(List[RowInImportedSkillsFile]):
    @classmethod
    def from_df(cls, some_df: pd.DataFrame, skills_config: ImportSkillsconfig):
        as_list = list(some_df.iterrows())
        return cls([RowInImportedSkillsFile(row[1], skills_config=skills_config) for row in as_list])

    def remove_empty_names(self):
        new_list = [row for row in self if not row.empty_name()]
        return ListOfRowsInSkillsFile(new_list)