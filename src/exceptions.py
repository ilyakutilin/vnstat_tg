class InternalError(Exception):
    pass


class CommandError(InternalError):
    pass


class FetchError(InternalError):
    pass


class InternalKeyError(InternalError):
    pass


class MissingInterfacesError(InternalError):
    pass


class MissingTrafficError(InternalError):
    pass


class NoDayOrMonthError(InternalError):
    pass


class InvalidModifierError(InternalError):
    pass
