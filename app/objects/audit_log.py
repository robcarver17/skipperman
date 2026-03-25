import datetime
from dataclasses import dataclass
from typing import List

import pandas as pd

from app.objects.events import Event, ListOfEvents


@dataclass
class AuditLogUpdateWithIds:
    event_id: str
    username: str
    volunteer_name: str
    datetime_of_update: datetime.datetime


class ListOfAuditLogUpdatesWithIds(List[AuditLogUpdateWithIds]):
    def as_pd_df(self) -> pd.DataFrame:
        ### only for one event assumed
        return pd.DataFrame(
            dict(
                User=[item.username for item in self],
                Volunteer=[item.volunteer_name for item in self],
                Update=[item.datetime_of_update for item in self],
            )
        )


@dataclass
class AuditLogUpdateWithEvents:
    event: Event
    username: str
    volunteer_name: str
    datetime_of_update: datetime.datetime

    @classmethod
    def from_audit_with_id_and_list_of_events(
        cls, audit_with_id: AuditLogUpdateWithIds, list_of_events: ListOfEvents
    ):
        return cls(
            event=list_of_events.event_with_id(audit_with_id.event_id),
            username=audit_with_id.username,
            volunteer_name=audit_with_id.volunteer_name,
            datetime_of_update=audit_with_id.datetime_of_update,
        )


class ListOfAuditLogUpdatesWithEvents(List[AuditLogUpdateWithEvents]):
    def as_pd_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            dict(
                Event=[str(item.event) for item in self],
                User=[item.username for item in self],
                Volunteer=[item.volunteer_name for item in self],
                Update=[item.datetime_of_update for item in self],
            )
        )
