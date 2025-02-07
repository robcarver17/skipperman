from enum import Enum
from typing import List

CANCELLED = "Cancelled"
ACTIVE_PAID = "Paid"
EMPTY = "Empty"
MANUAL = "Manual"
UNPAID = "Unpaid"
PARTIAL_PAID = "PartialPaid"
DELETED = "Deleted"
POSSIBLE_STATUS_NAMES = [
    CANCELLED,
    ACTIVE_PAID,
    DELETED,
    EMPTY,
    MANUAL,
    UNPAID,
    PARTIAL_PAID,
]
ACTIVE_STATUS_NAMES = [ACTIVE_PAID, UNPAID, PARTIAL_PAID, MANUAL]


class RegistrationStatus:
    def __init__(self, name: str):
        if name == "Active":  ## Fix for old data
            name = ACTIVE_PAID
        assert name in POSSIBLE_STATUS_NAMES
        self._name = name

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return self.name

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_active(self) -> bool:
        return self.name in ACTIVE_STATUS_NAMES

    @property
    def is_cancelled_or_deleted(self):
        return self.is_cancelled or self.is_deleted

    @property
    def is_cancelled(self):
        return self.name == CANCELLED

    @property
    def is_deleted(self):
        return self.name == DELETED


cancelled_status = RegistrationStatus(CANCELLED)
active_paid_status = RegistrationStatus(ACTIVE_PAID)
active_unpaid_status = RegistrationStatus(UNPAID)
active_part_paid_status = RegistrationStatus(PARTIAL_PAID)
deleted_status = RegistrationStatus(DELETED)
empty_status = RegistrationStatus(EMPTY)
manual_status = RegistrationStatus(MANUAL)


def get_states_allowed_give_current_status(
    current_status: RegistrationStatus,
) -> List[RegistrationStatus]:
    if current_status in [
        cancelled_status,
        active_paid_status,
        active_unpaid_status,
        active_part_paid_status,
    ]:
        allowable_status = [
            cancelled_status,
            active_paid_status,
            active_unpaid_status,
            active_part_paid_status,
        ]
    elif current_status == deleted_status:
        allowable_status = [
            cancelled_status,
            active_paid_status,
            active_unpaid_status,
            active_part_paid_status,
            deleted_status,
        ]
    elif current_status == manual_status:
        allowable_status = [cancelled_status, manual_status]
    ## SHOULD NEVER BE EMPTY
    else:
        raise Exception("Status %s not recognised" % str(current_status))

    return allowable_status


all_possible_status = [
    RegistrationStatus(state_name) for state_name in POSSIBLE_STATUS_NAMES
]
RegStatusChange = Enum(
    "RegStatusChange",
    [
        "new_registration_replacing_deleted_or_cancelled",
        "existing_registration_now_deleted_or_cancelled",
        "status_unchanged",
        "status_still_active_but_has_changed",
        "error",
    ],
)
new_registration_replacing_deleted_or_cancelled = RegStatusChange[
    "new_registration_replacing_deleted_or_cancelled"
]
existing_registration_now_deleted_or_cancelled = RegStatusChange[
    "existing_registration_now_deleted_or_cancelled"
]
status_unchanged = RegStatusChange["status_unchanged"]
status_still_active_but_has_changed = RegStatusChange[
    "status_still_active_but_has_changed"
]
error = RegStatusChange["error"]
