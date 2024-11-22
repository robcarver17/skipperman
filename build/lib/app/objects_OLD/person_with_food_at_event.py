"""
def get_cadet_food_requirements_from_row_of_mapped_wa_event_data(row_in_mapped_wa_event_with_id: RowInMappedWAEventDeltaRow) -> FoodRequirements:
    return guess_food_requirements_from_food_field(
        row_in_mapped_wa_event_with_id.data_in_row.get_item(CADET_FOOD_PREFERENCE)
    )

"""
