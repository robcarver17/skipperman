from os.path import join


def get_path_and_filename_for_named_csv_file(
    master_data_path: str, generic_name_of_file_required: str
):

    ## returns eg 'cadets', 'cadet_master_list.csv'
    try:
        path, filename = _dict_of_filenames_and_paths[generic_name_of_file_required]
    except KeyError:
        raise Exception(
            "generic file name '%s' not in possible set of files %s"
            % (
                generic_name_of_file_required,
                str(list(_dict_of_filenames_and_paths.keys())),
            )
        )

    resolved_path_and_filename = join(master_data_path, path, filename)

    return resolved_path_and_filename


## MODIFY THE FOLLOWING LINES TO CHANGE WHERE FILES LIVE AND THEIR
## THE FIRST ITEM IN EACH TUPLE IS THE PATH, THE SECOND IS THE FILENAME
_dict_of_filenames_and_paths = dict(
    cadet_master_list=("cadets", "cadet_master_list.csv")
)
