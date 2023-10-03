class OmnicommError(Exception):
    ...


class EmptyDataError(OmnicommError):
    ...


class CommandAlreadyExistsError(OmnicommError):
    ...


class UnpackingCRCError(OmnicommError):
    ...


class CRCDoesNotMatchError(OmnicommError):
    ...


class FrameMarkerDoesNotExistError(OmnicommError):
    ...


class ProtoDoesNotExistError(OmnicommError):
    ...
