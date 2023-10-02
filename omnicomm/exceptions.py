class OmnicommError(Exception):
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
