import os
from typing import List

DATE_STR = "%Y/%m/%d"
DATETIME_STR = "%Y/%m/%d %H:%M:%S.%f"


def files_with_extension_in_resolved_pathname(
    resolved_pathname: str, extension=".csv"
) -> List[str]:
    """
    Find all the files with a particular extension in a directory
    """

    file_list = os.listdir(resolved_pathname)
    file_list = [filename for filename in file_list if filename.endswith(extension)]
    file_list_no_extension = [filename.split(".")[0] for filename in file_list]

    return file_list_no_extension


