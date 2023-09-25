import pandas as pd

class MappedWAEvent(pd.DataFrame):
    @classmethod
    def from_df(cls, some_df: pd.DataFrame):
        ## trivial but in case change rep from df to something else and consistency
        return cls(some_df)

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame(self)