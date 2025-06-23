import os
from typing import List

from app.backend.file_handling import (
    create_local_file_from_uploaded_and_return_filename,
)
from app.data_access.file_access import get_staged_adhoc_filename
from app.data_access.xls_and_csv import load_spreadsheet_file_and_clear_nans
from app.backend.volunteers.skills import (
    get_list_of_skills,
    get_dict_of_existing_skills_for_volunteer,
)
from app.data_access.store.object_store import ObjectStore
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.skill_import import ListOfRowsInSkillsFile, RowInImportedSkillsFile
from app.objects.utilities.exceptions import missing_data
from app.objects.volunteer_skills import Skill
from app.objects.volunteers import Volunteer
from app.data_access.configuration.configuration import IMPORT_SKILLS_CONFIG
from app.objects.composed.volunteers_with_skills import SkillsDict

skills_temporary_file = get_staged_adhoc_filename("skills_import_temporary_File.csv")


def create_skills_refresh_file(interface: abstractInterface, file_marker_name: str):
    create_local_file_from_uploaded_and_return_filename(
        interface=interface,
        file_marker_name=file_marker_name,
        new_filename=skills_temporary_file,
    )


def delete_skills_refresh_file():
    os.remove(skills_temporary_file)


def load_skills_refresh_file() -> ListOfRowsInSkillsFile:
    df = load_spreadsheet_file_and_clear_nans(skills_temporary_file)
    rows_in_skills_file = ListOfRowsInSkillsFile.from_df(
        df, skills_config=IMPORT_SKILLS_CONFIG
    )

    rows_in_skills_file = rows_in_skills_file.remove_empty_names()

    return rows_in_skills_file


def get_volunteer_from_row(current_row: RowInImportedSkillsFile):
    volunteer_firstname, volunter_surname = current_row.volunteer_name_as_tuple()
    volunteer = Volunteer(first_name=volunteer_firstname, surname=volunter_surname)

    return volunteer


def get_skills_dict_from_row_in_form(
    object_store: ObjectStore, current_row: RowInImportedSkillsFile
) -> SkillsDict:
    list_of_skills = get_list_of_skills(object_store)

    skills_config = current_row.skills_config
    list_of_skill_names = skills_config.names_of_skills
    skills_dict = SkillsDict()
    for skill_name in list_of_skill_names:
        skill = list_of_skills.skill_with_name(skill_name, missing_data)
        if skill is missing_data:
            raise Exception(
                "Skill %s in import configuration is not a named skill in Skipperman, must be one of %s"
                % (skill_name, str(list_of_skills.list_of_names()))
            )

        is_valid = current_row.is_skill_valid(skill_name)

        skills_dict[skill] = is_valid

    return skills_dict


def compare_skills_for_volunteer_with_passed_and_return_warning(
    object_store: ObjectStore,
    volunteer: Volunteer,
    current_row: RowInImportedSkillsFile,
) -> List[str]:
    existing_skills = get_dict_of_existing_skills_for_volunteer(
        object_store=object_store, volunteer=volunteer
    )
    passed_skills_dict = get_skills_dict_from_row_in_form(object_store, current_row)

    msgs = []
    for skill in existing_skills:
        add_messages_for_skill(
            skill=skill,
            existing_skills=existing_skills,
            passed_skills_dict=passed_skills_dict,
            current_row=current_row,
            msgs=msgs,
        )

    if len(msgs) > 0:
        if len(passed_skills_dict) > 0:
            msgs.append("Identified skills in import file %s" % str(passed_skills_dict))
        if len(existing_skills.list_of_held_skill_names()) > 0:
            msgs.append("Current skills in skipperman %s" % str(existing_skills))
        msgs.append(
            "Note: Import file may not contain PB2 information. Someone who is qualified as an RCL2, DI or SI will definitely have PB2. An SI is also a DI. To reduce warning messages, for consistency add AI to any DI that used to be an AI."
        )

    return msgs


def add_messages_for_skill(
    skill: Skill,
    existing_skills: SkillsDict,
    passed_skills_dict: SkillsDict,
    current_row: RowInImportedSkillsFile,
    msgs: List[str],
):
    existing_has = existing_skills.has_skill(skill)
    new_has = passed_skills_dict.get(skill, missing_data)
    if new_has is missing_data:
        return

    if existing_has == new_has:
        return

    elif existing_has and not new_has:
        more = current_row.explain_why_skill_invalid(skill.name)
        msgs.append(
            "%s has skill %s in current skipperman data but not imported file: %s"
            % (current_row.volunteer_name(), skill.name, more)
        )
    elif not existing_has and new_has:
        more = current_row.explain_why_is_valid(skill.name)
        msgs.append(
            "%s does not currently have skill %s in current skipperman data but does in imported file: %s"
            % (current_row.volunteer_name(), skill.name, more)
        )

    return
