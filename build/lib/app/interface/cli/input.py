import datetime
from enum import EnumMeta
from typing import List


def get_input_from_user_and_convert_to_type(
    prompt: str,
    type_expected=int,
    **kwargs,
):
    if type_expected is datetime.date:
        value = get_date_from_user(prompt)
    elif type(type_expected) is EnumMeta:
        value = get_enum_from_user(prompt, enum_class=type_expected)
    else:
        value = get_input_from_user_and_convert_to_type_other(
            prompt, type_expected=type_expected, **kwargs
        )

    return value


INPUT_DATE_FORMAT = "%Y-%m-%d"


def get_date_from_user(prompt: str) -> datetime.date:
    invalid = True
    while invalid:
        user_input = input(prompt + " (date format: YYYY-MM-DD eg 2008-02-08) ")
        try:
            somedatetime = datetime.datetime.strptime(user_input, INPUT_DATE_FORMAT)
            invalid = False
        except:
            print("Date %s not in format %s" % (user_input, INPUT_DATE_FORMAT))
            continue

    return somedatetime.date()


def get_enum_from_user(prompt: str, enum_class: EnumMeta):
    enum_options = [item.name for item in enum_class]
    print(prompt + " Choose option:")
    selected_name = print_menu_and_get_desired_option(enum_options)

    return enum_class[selected_name]


def get_input_from_user_and_convert_to_type_other(
    prompt: str,
    type_expected=int,
    allow_default: bool = False,
    default_value=0,
    default_str: str = None,
    check_type: bool = True,
):
    input_str = prompt + " "
    if allow_default:
        if default_str is None:
            input_str = input_str + "<RETURN for default %s> " % str(default_value)
        else:
            input_str = input_str + "<RETURN for %s> " % default_str

    result = _get_input_and_check_type(
        input_str=input_str,
        type_expected=type_expected,
        allow_default=allow_default,
        default_value=default_value,
        check_type=check_type,
    )

    return result


def _get_input_and_check_type(
    input_str: str,
    type_expected=int,
    allow_default: bool = True,
    default_value=0,
    check_type: bool = True,
):
    invalid = True
    while invalid:
        user_input = input(input_str)

        if user_input == "" and allow_default:
            return default_value
        if not check_type:
            ## not typecasting
            return user_input

        try:
            result = _convert_type_or_throw_expection(
                user_input=user_input, type_expected=type_expected
            )
            return result
        except BaseException:
            ## keep going
            continue


def _convert_type_or_throw_expection(user_input: str, type_expected=int):
    try:
        if type_expected is bool:
            result = str2Bool(user_input)
        else:
            result = type_expected(user_input)
    except:
        print("%s is not of expected type %s" % (user_input, type_expected.__name__))
        raise Exception()

    return result


def str2Bool(x: str) -> bool:
    if isinstance(x, bool):
        return x
    if x.lower() in ("t", "true"):
        return True
    if x.lower() in ("f", "false"):
        return False
    raise Exception("%s can't be resolved as a bool" % x)


def true_if_answer_is_yes(prompt: str = "") -> bool:
    invalid = True
    while invalid:
        x = input(prompt + "?")
        if len(x) == 0:
            pass
        else:
            first_character = x[0].lower()
            if first_character == "y":
                return True
            elif first_character == "n":
                return False

        print("Need one of yes/no, Yes/No, y/n, Y/N")


def print_menu_and_get_desired_option(menu_of_options: list) -> str:
    menu_of_options_with_int_index = _list_menu_to_dict_menu(menu_of_options)
    _print_options_menu(menu_of_options_with_int_index)
    list_of_menu_indices = list(menu_of_options_with_int_index.keys())

    invalid_response = True
    while invalid_response:
        option_index = get_input_from_user_and_convert_to_type(
            "Your choice?",
            type_expected=int,
            allow_default=True,
            default_value=0,
        )
        if option_index not in list_of_menu_indices:
            print("Not a valid option")
            continue
        else:
            break

    return menu_of_options_with_int_index[option_index]


def _list_menu_to_dict_menu(menu_of_options_as_list: List[str]) -> dict:
    menu_of_options = dict(
        [
            (int_key, menu_value)
            for int_key, menu_value in enumerate(menu_of_options_as_list)
        ]
    )
    return menu_of_options


def _print_options_menu(menu_of_options: dict):
    menu_options_list = sorted(menu_of_options.keys())
    for option in menu_options_list:
        print("%d: %s" % (option, str(menu_of_options[option])))
    print("\n")
