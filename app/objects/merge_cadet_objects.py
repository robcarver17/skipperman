from dataclasses import dataclass
from enum import Enum

ActiveStatus = Enum("ActiveStatus", ["Active","NotAttending", "InActive"])
active = ActiveStatus['Active']
inactive = ActiveStatus['InActive']
not_attending = ActiveStatus['NotAttending']


def get_active_status(not_at_event_and_active: bool, not_at_event: bool):
    if not_at_event:
        return not_attending
    if not_at_event_and_active:
        return inactive
    return active


@dataclass
class ActionToTake:
    throw_error_both_active: bool = False
    do_nothing: bool = False
    update_cadet_id_general: bool = False
    update_cadet_id_reg_id: bool = False
    remove_reg_id_for_delete_cadet: bool = False
    remove_reg_id_for_keep_cadet: bool = False


class ConstructActiveStatus:
    def __init__(self, delete_cadet_status: ActiveStatus, keep_cadet_status: ActiveStatus):
        self._delete_cadet_status = delete_cadet_status
        self._keep_cadet_status = keep_cadet_status

    @property
    def delete_cadet_status(self):
        return self._delete_cadet_status

    @property
    def keep_cadet_status(self):
        return self._keep_cadet_status

    def action_to_take(self) -> ActionToTake:

        """
        Check options:
        delete, keep

        not attending, active: do nothing A
        not attending, inactive:  do nothing A
        not attending, not_attending:  do nothing A
        active, active: break - one needs cancelling B
        active, inactive: C   replace cadet id, remove registration/identification for keep_cadet
        active, not attending: D  replace cadet_id, nothing else for keep_cadet
        inactive, active: E remove registration/identification for delete_cadet, no action keep_cadet
        inactive, inactive: F remove registration/identification for delete_cadet, no action keep_cadet
        inactive, not attending: G replace cadet_id on registration/identification only, no action keep_cadet
        """

        if self.delete_cadet_status is not_attending: #A
            return ActionToTake(do_nothing=True)

        if  (self.delete_cadet_status is active) and (self.keep_cadet_status is active): # B
            return ActionToTake(throw_error_both_active=True)

        if (self.delete_cadet_status is active) and (self.keep_cadet_status is inactive):#C
            return ActionToTake(update_cadet_id_general=True, update_cadet_id_reg_id=True, remove_reg_id_for_keep_cadet=True)

        if (self.delete_cadet_status is active) and (self.keep_cadet_status is not_attending):#D
            return ActionToTake(update_cadet_id_general=True, update_cadet_id_reg_id=True)

        if (self.delete_cadet_status is inactive) and (self.keep_cadet_status is active):#E
            return ActionToTake(remove_reg_id_for_delete_cadet=True)

        if (self.delete_cadet_status is inactive) and (self.keep_cadet_status is inactive):#F
            return ActionToTake(remove_reg_id_for_delete_cadet=True)

        if (self.delete_cadet_status is inactive) and (self.keep_cadet_status is not_attending):#G
            return ActionToTake(update_cadet_id_reg_id=True)

        raise Exception("Combo of %s %s do not know what to do" % (self.delete_cadet_status, self.keep_cadet_status))