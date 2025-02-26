import pandas as pd
from app.data_access.store.object_store import ObjectStore

from app.backend.clothing.active_cadets_with_clothing import (
    get_dict_of_active_cadets_with_clothing_at_event,
)
from app.objects.abstract_objects.abstract_tables import PandasDFTable
from app.objects.events import Event


def summarise_clothing(object_store: ObjectStore, event: Event) -> PandasDFTable:
    list_of_cadets_with_clothing = get_dict_of_active_cadets_with_clothing_at_event(
        object_store=object_store, event=event, only_committee=False
    )

    sizes = list_of_cadets_with_clothing.get_clothing_size_options()
    colours = list_of_cadets_with_clothing.get_colour_options()

    all_clothing = {}
    for size in sizes:
        clothing_for_size = {}
        for colour in colours:
            clothing_for_size[colour] = (
                list_of_cadets_with_clothing.count_of_size_and_colour(
                    size=size, colour=colour
                )
            )

        all_clothing[size] = clothing_for_size

    if len(all_clothing)==0:
        return PandasDFTable(pd.DataFrame())

    df = pd.DataFrame(all_clothing)
    df.loc["Total"] = df.sum(numeric_only=True, axis=0)
    df.loc[:, "Total"] = df.sum(numeric_only=True, axis=1)

    return PandasDFTable(df)
