from omnicomm.types import RegFwCmd

COMMAND_PROTO: dict[int | RegFwCmd, str] = {
    0x86: 'omnicomm.proto.profi_optim_lite_pb2.RecReg',
    0x95: 'omnicomm.proto.profi2_optim2_lite2_pb2.RecReg',
    # (202000013, 114, 0x86): 'omnicomm.proto.profi2_optim2_lite2_pb2.RecReg',
    # (202000013, 0x86): 'omnicomm.proto.profi2_optim2_lite2_pb2.RecReg',
}
