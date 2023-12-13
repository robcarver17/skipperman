import pandas as pd

from app.objects.utils import in_x_not_in_y, in_both_x_and_y

SKIPPERMAN_FIELD_COLUMN_VALUE = "skipperman_field"
WA_FIELD_COLUMN_KEY = "wa_field"


class WAFieldMapping(dict):
    @classmethod
    def create_empty(cls):
        return cls()

    @classmethod
    def from_df(cls, df: pd.DataFrame):
        try:
            skipperman_field_values = list(df[SKIPPERMAN_FIELD_COLUMN_VALUE].values)
            wa_field_values = list(df[WA_FIELD_COLUMN_KEY].values)
        except KeyError:
            raise Exception(
                "WA field dataframe must contain %s and %s"
                % (SKIPPERMAN_FIELD_COLUMN_VALUE, WA_FIELD_COLUMN_KEY)
            )

        list_of_mapping = [
            (wa_field_key, skipper_man_field_value)
            for wa_field_key, skipper_man_field_value in zip(
                wa_field_values, skipperman_field_values
            )
        ]

        return cls(list_of_mapping)

    def to_df(self) -> pd.DataFrame:
        skipperman_field_values = self.list_of_skipperman_fields
        wa_field_values = self.list_of_wa_fields
        return pd.DataFrame(
            {
                WA_FIELD_COLUMN_KEY: wa_field_values,
                SKIPPERMAN_FIELD_COLUMN_VALUE: skipperman_field_values,
            }
        )

    def as_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                WA_FIELD_COLUMN_KEY: self.list_of_wa_fields,
                SKIPPERMAN_FIELD_COLUMN_VALUE: self.list_of_skipperman_fields,
            }
        )

    def matching_wa_fields(self, list_of_wa_fields: list):
        return in_both_x_and_y(list_of_wa_fields, self.list_of_wa_fields)

    def wa_fields_missing_from_list(self, list_of_wa_fields: list):
        return in_x_not_in_y(x=self.list_of_wa_fields, y=list_of_wa_fields)

    def wa_fields_missing_from_mapping(self, list_of_wa_fields: list):
        return in_x_not_in_y(x=list_of_wa_fields, y=self.list_of_wa_fields)

    def skipperman_field_given_wa_field(self, wa_field: str):
        return self[wa_field]

    @property
    def list_of_wa_fields(self):
        return list(self.keys())

    @property
    def list_of_skipperman_fields(self):
        return list(self.values())

