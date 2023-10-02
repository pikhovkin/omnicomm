import sys
from importlib import import_module

from omnicomm.types import RegFwCmd


def cached_import(module_path, class_name):
    # Check whether module is loaded and fully initialized.
    if not (
        (module := sys.modules.get(module_path))
        and (spec := getattr(module, "__spec__", None))
        and getattr(spec, "_initializing", False) is False
    ):
        module = import_module(module_path)
    return getattr(module, class_name)


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    try:
        return cached_import(module_path, class_name)
    except AttributeError as err:
        msg = f'Module "{module_path}" does not define a "{class_name}" attribute/class'
        raise ImportError(msg) from err


def cast_command_proto(command_proto: dict[str, str]) -> dict[int | RegFwCmd, str]:
    """Cast a command`s map from a config with `str` keys to config with `int | tuple[int, ...]` keys.

    For example:

    ```yaml
    ---
    COMMAND_PROTO:
      (200000000, 134): omnicomm.proto.profi2_optim2_lite2_pb2.RecReg
      '134': omnicomm.proto.profi_optim_lite_pb2.RecReg
    ```

    ```python
    import settings

    command_proto = cast_command_proto(settings.COMMAND_PROTO)
    assert command_proto[134]
    assert command_proto[(200000000, 134)]
    ```
    """
    conf: dict[int | RegFwCmd, str] = {}
    for k, v in command_proto.items():
        key = tuple(map(int, k.replace(' ', '').strip('()').split(',')))
        if len(key) == 1:
            conf[key[0]] = v.strip()
        else:
            conf[key] = v.strip()
    return conf
