from app.backend.data.cadets import CadetData
from app.backend.data.qualification import QualificationData
from app.data_access.file_access import temp_file_name
from app.objects.abstract_objects.abstract_interface import abstractInterface
from app.objects.qualifications import ListOfNamedCadetsWithQualifications


def write_qualifications_to_temp_csv_file_and_return_filename(
    interface: abstractInterface,
) -> str:
    qualification_data = QualificationData(interface.data)
    cadet_data = CadetData(interface.data)

    list_of_cadets_with_qualification = (
        qualification_data.get_list_of_cadets_with_qualifications()
    )
    list_of_qualifications = qualification_data.load_list_of_qualifications()
    list_of_cadets = cadet_data.get_list_of_cadets()

    list_of_cadet_names_with_qualifications = (
        ListOfNamedCadetsWithQualifications.from_id_lists(
            list_of_cadets_with_qualifications=list_of_cadets_with_qualification,
            list_of_cadets=list_of_cadets,
            list_of_qualifications=list_of_qualifications,
        )
    )

    list_of_cadet_names_with_qualifications = (
        list_of_cadet_names_with_qualifications.sort_by_date()
    )
    df_of_qualifications = list_of_cadet_names_with_qualifications.as_df_of_str()

    filename = temp_file_name()

    df_of_qualifications.to_csv(filename, index=False)

    return filename
