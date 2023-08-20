class OmnicommException(Exception):
    ...


class CommandAlreadyExists(OmnicommException):
    ...


class CRCDoesNotMatch(OmnicommException):
    ...


class FrameMarkerDoesNotExist(OmnicommException):
    ...
