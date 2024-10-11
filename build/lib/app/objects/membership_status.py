import enum

MembershipStatus = enum.Enum('MembershipStatus', ['Current', 'None_Member', 'Lapsed', 'Unconfirmed', "UserUnconfirmed"])
none_member = MembershipStatus.None_Member
current_member = MembershipStatus.Current
lapsed_member = MembershipStatus.Lapsed
system_unconfirmed_member = MembershipStatus.Unconfirmed ## ONLY USED BY SYSTEM, USER SHOULD NOT SEE
user_unconfirmed_member = MembershipStatus.UserUnconfirmed


def describe_status(status: MembershipStatus):
    describe_dict = {
        current_member: "Member",
        lapsed_member: "Lapsed member",
        none_member: "None member",
        system_unconfirmed_member: "TBC",
        user_unconfirmed_member: "Unconfirmed member"
    }
    return describe_dict[status]


all_status_as_list_for_user_input = [none_member, current_member, lapsed_member, user_unconfirmed_member]
all_status_description_as_dict_for_user_input = dict([(describe_status(status), status) for status in all_status_as_list_for_user_input])
