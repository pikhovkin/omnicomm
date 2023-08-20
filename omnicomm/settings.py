from .types import RegFwCmd


COMMAND_PROTO: dict[RegFwCmd, str] = {
    0x86: 'omnicomm.proto.profi2_optim2_lite2_pb2.RecReg',
    0x95: 'omnicomm.proto.profi2_optim2_lite2_pb2.RecReg',
    (202000013, 114, 0x86): 'omnicomm.proto.profi2_optim2_lite2_pb2.RecReg',
    (202000013, 0x86): 'omnicomm.proto.profi2_optim2_lite2_pb2.RecReg',
}
