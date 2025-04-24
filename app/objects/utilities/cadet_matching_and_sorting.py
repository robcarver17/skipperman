import datetime

import numpy as np

from app.data_access.configuration.configuration import SIMILARITY_LEVEL_TO_WARN_NAME, \
    SIMILARITY_LEVEL_TO_MATCH_VERY_SIMILAR_FIRST_NAMES
from app.objects.cadets import Cadet, DEFAULT_DATE_OF_BIRTH, ListOfCadets
from app.objects.utilities.exceptions import arg_not_passed
from app.objects.utilities.utils import similar

def get_list_of_cadets_with_similar_surname(list_of_cadets: ListOfCadets, surname:str, name_threshold: float = SIMILARITY_LEVEL_TO_WARN_NAME):
    new_list = [
        cadet for cadet in list_of_cadets if similar(cadet.surname, surname)>name_threshold
    ]

    return ListOfCadets(new_list)


def get_list_of_similar_cadets(list_of_cadets: ListOfCadets, other_cadet: Cadet, name_threshold: float = SIMILARITY_LEVEL_TO_WARN_NAME):
    new_list = [
        cadet for cadet in list_of_cadets if similar_cadet(cadet, other_cadet, name_threshold=name_threshold)
    ]

    return ListOfCadets(new_list)

def get_list_of_very_similar_cadets(list_of_cadets: ListOfCadets, other_cadet: Cadet, first_name_threshold=SIMILARITY_LEVEL_TO_MATCH_VERY_SIMILAR_FIRST_NAMES):
    new_list = [
        cadet for cadet in list_of_cadets if very_similar_cadet(cadet, other_cadet, first_name_threshold=first_name_threshold)
    ]

    return ListOfCadets(new_list)


def sort_list_of_cadets_by_similarity(list_of_cadets: ListOfCadets, other_cadet: Cadet):
    scores_and_cadets = [(cadet, similarity_score(cadet, other_cadet)) for cadet in list_of_cadets]
    scores_and_cadets.sort(key=lambda tup: tup[1], reverse=True)
    cadets = [score_with_cadet[0] for score_with_cadet in scores_and_cadets]

    return ListOfCadets(cadets)

def similarity_score(cadet_in_data: Cadet, other_cadet: Cadet):
    first_name_score = similar(cadet_in_data.first_name.lower(), other_cadet.first_name.lower())
    surname_score = similar(cadet_in_data.surname.lower(), other_cadet.surname.lower())
    average_name_score = np.mean([first_name_score, surname_score])
    dob_score = similarity_date_score(cadet_in_data.date_of_birth, other_cadet.date_of_birth)

    return np.mean([average_name_score, dob_score])

def very_similar_cadet(cadet_in_data: Cadet, other_cadet: Cadet, first_name_threshold=SIMILARITY_LEVEL_TO_MATCH_VERY_SIMILAR_FIRST_NAMES):
    first_name_match = similar(cadet_in_data.first_name.lower(), other_cadet.first_name.lower())
    second_name_match = cadet_in_data.surname.lower() == other_cadet.surname.lower()
    dob_match_with_codes =similar_cadet_DOB_match_returns_code(date_in_data=cadet_in_data.date_of_birth,
                                                               other_date=other_cadet.date_of_birth)

    if second_name_match==1:
        if dob_match_with_codes is not NO_MATCH:
            if first_name_match>first_name_threshold:
                return True

    return False


def similar_cadet(cadet_in_data: Cadet, other_cadet: Cadet, name_threshold: float = SIMILARITY_LEVEL_TO_WARN_NAME):
    name_match = similar(cadet_in_data.name.lower(), other_cadet.name.lower())
    dob_match_with_codes =similarity_date_score(cadet_in_data.date_of_birth, other_cadet.date_of_birth)

    if name_match>name_threshold:
        if dob_match_with_codes>0.5:
            return True

    return False

def similarity_date_score(date_in_data: datetime.date, other_date:datetime.date):
    dob_match_with_codes =similar_cadet_DOB_match_returns_code(date_in_data=date_in_data, other_date=other_date)
    if dob_match_with_codes is NO_MATCH:
        return similar(str(date_in_data), str(other_date))*0.7 ## less than values below

    result_dict = {
        EXACT: 1.0,
        WRONG_YEAR: 0.95,
        ONE_IS_DEFAULT: 0.95,
        DATE_FIELD_ERROR: 0.9,
        YEAR_AND_DATEFIELD_ERROR: 0.8,
    }

    score = result_dict.get(dob_match_with_codes, None)
    if score is None:
        raise Exception("Code %s not recognised in date match" % dob_match_with_codes)

    return score

WRONG_YEAR = "year_is_current_year_but_matches"
DATE_FIELD_ERROR = "date_field_error_but_matches"
MATCHES = "matches"
ONE_IS_DEFAULT = "default"
EXACT = "Exact"
YEAR_AND_DATEFIELD_ERROR = "year_is_current_year_and_date_field_error_but_matches"
NO_MATCH = "no match"


def similar_cadet_DOB_match_returns_code(date_in_data: datetime.date, other_date:datetime.date):
    errors = similar_cadet_DOB_matching_returns_multiple_codes(date_in_data, other_date)
    if not MATCHES in errors:
        return NO_MATCH

    if len(errors)==1:
        return EXACT

    if len(errors)==2:
        if DATE_FIELD_ERROR in errors:
            return DATE_FIELD_ERROR
        elif WRONG_YEAR in errors:
            return WRONG_YEAR
        elif ONE_IS_DEFAULT in errors:
            return ONE_IS_DEFAULT
        else:
            raise Exception()

    if len(errors)==3:
        return YEAR_AND_DATEFIELD_ERROR
    else:
        raise Exception()


def similar_cadet_DOB_matching_returns_multiple_codes(date_in_data: datetime.date, other_date:datetime.date):
    errors = []
    if date_in_data==other_date:
        return [MATCHES]

    if DEFAULT_DATE_OF_BIRTH == other_date:
        return [ONE_IS_DEFAULT, MATCHES]

    errors = check_dates_across_perms(date_in_data, other_date, errors)
    if MATCHES in errors:
        return errors

    errors = check_dates_across_perms(other_date, date_in_data, errors)
    errors = list(set(errors))

    return errors


def check_dates_across_perms(first_date: datetime.date, second_date: datetime.date, errors:list):
    for perm in range(5):
        current_year = datetime.date.today().year
        if first_date.year == current_year or second_date.year == current_year:
            errors.append(WRONG_YEAR)
            ignore_years = True
        else:
            ignore_years = False

        if check_dates(first_date, second_date, ignore_years):
            errors.append(MATCHES)
            return errors


        try:
            reorder_first = reorder_date(first_date, perm)
        except:
            continue

        matches = check_dates(reorder_first, second_date, ignore_years=ignore_years)
        if matches:
            errors.append(DATE_FIELD_ERROR)
            errors.append(MATCHES)
            return errors

    return errors


def check_dates(first_date: datetime.date, second_date: datetime.date, ignore_years: bool):
    if first_date.day!=second_date.day:
        return False
    if first_date.month!=second_date.month:
        return False
    if ignore_years:
        return True

    return first_date.year == second_date.year


def reorder_date(some_date: datetime.date, perm: int):
    if perm==0:
        return datetime.date(year=some_date.year, day=some_date.month, month=some_date.day)
    elif perm==1:
        return datetime.date(year=some_date.month, day=some_date.day, month=some_date.year)
    elif perm==2:
        return datetime.date(year=some_date.day, day=some_date.year, month=some_date.month)
    elif perm==3:
        return datetime.date(year=some_date.day,  day=some_date.month, month=some_date.year)
    elif perm==4:
        return datetime.date(year=some_date.month,  day=some_date.year, month=some_date.day)
    else:
        return "Unknown"


def sort_a_list_of_cadets(
    master_list: ListOfCadets, sort_by: str = arg_not_passed,
        similar_cadet: Cadet = arg_not_passed,
) -> ListOfCadets:
    if sort_by is arg_not_passed:
        return master_list
    if sort_by == SORT_BY_SURNAME:
        return master_list.sort_by_surname()
    elif sort_by == SORT_BY_FIRSTNAME:
        return master_list.sort_by_firstname()
    elif sort_by == SORT_BY_DOB_ASC:
        return master_list.sort_by_dob_asc()
    elif sort_by == SORT_BY_DOB_DSC:
        return master_list.sort_by_dob_desc()
    if sort_by == SORT_BY_SIMILARITY_BOTH:
        if similar_cadet is arg_not_passed:
            raise Exception("Need to pass cadet if sorting by similarity, sort order %s" % sort_by)
        return sort_list_of_cadets_by_similarity(master_list, other_cadet=similar_cadet)

    else:
        raise Exception("Sort order %s not known" % sort_by)


SORT_BY_SURNAME = "Sort by surname"
SORT_BY_FIRSTNAME = "Sort by first name"
SORT_BY_DOB_ASC = "Sort by date of birth, oldest 1st"
SORT_BY_DOB_DSC = "Sort by date of birth, youngest 1st"
SORT_BY_SIMILARITY_BOTH = "Sort by similarity"
