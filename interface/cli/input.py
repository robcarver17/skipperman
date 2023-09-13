def get_input_from_user_and_convert_to_type(
    prompt: str,
    type_expected=int,
    allow_default: bool = True,
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

def true_if_answer_is_yes(
    prompt: str = "") -> bool:
    invalid = True
    while invalid:
        x = input(prompt+"?")
        if len(x)==0:
            pass
        else:
            first_character = x[0].lower()
            if first_character == "y":
                return True
            elif first_character == "n":
                return False

        print("Need one of yes/no, Yes/No, y/n, Y/N")
