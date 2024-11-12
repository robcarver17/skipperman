from typing import Callable, Dict

import pandas as pd

from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.exceptions import arg_not_passed
from app.objects.day_selectors import DaySelector, Day
from app.objects.events import Event
