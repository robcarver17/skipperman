import app.frontend.utilities.notes.render_notes
from app.data_access.store.object_store import ObjectStore

from app.data_access.init_directories import temp_file_name_in_download_directory
from app.objects.composed.cadets_with_qualifications import (
    ListOfNamedCadetsWithQualifications,
)
from app.backend.qualifications_and_ticks.qualifications_for_cadet import (
    get_dict_of_qualifications_for_all_cadets,
)


def write_qualifications_to_temp_csv_file_and_return_filename(
    object_store: ObjectStore,
) -> str:
    qualification_data = get_dict_of_qualifications_for_all_cadets(object_store)

    list_of_cadet_names_with_qualifications = (
        ListOfNamedCadetsWithQualifications.from_dict_of_qualifications(
            qualification_data
        )
    )

    list_of_cadet_names_with_qualifications = (
        list_of_cadet_names_with_qualifications.sort_by_date()
    )
    df_of_qualifications = list_of_cadet_names_with_qualifications.as_df_of_str()

    filename = temp_file_name_in_download_directory()

    df_of_qualifications.to_csv(filename, index=False)

    return filename
