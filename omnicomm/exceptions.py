class OmnicommError(Exception):
    ...


class CommandAlreadyExistsError(OmnicommError):
    ...


class CRCDoesNotMatchError(OmnicommError):
    ...


class FrameMarkerDoesNotExistError(OmnicommError):
    ...


class ProtoDoesNotExistError(OmnicommError):
    ...
