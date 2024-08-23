from omnicomm.commands import Cmd9F, Cmd80, Cmd81, Cmd85, Cmd86, Cmd87, Cmd88, Cmd93, Cmd94, Cmd95, CmdA0

__all__ = (
    'CmdDeleteRecord',
    'CmdDeleteRecordAck',
    'CmdGetRecord',
    'CmdGetTime',
    'CmdRecordResponse',
    'CmdRecordResponseAck',
    'CmdRecordResponseWiFi',
    'CmdRecordResponseWiFiAck',
    'CmdRecordStream',
    'CmdRegistarIdentity',
    'CmdServerIdentity',
    'CmdTimeResponse',
)


CmdRegistarIdentity = Cmd80
CmdServerIdentity = Cmd81
CmdGetRecord = Cmd85
CmdRecordResponse = Cmd86
CmdDeleteRecord = Cmd87
CmdRecordResponseAck = Cmd87
CmdDeleteRecordAck = Cmd88
CmdGetTime = Cmd93
CmdTimeResponse = Cmd94
CmdRecordStream = Cmd95
CmdRecordResponseWiFi = Cmd9F
CmdRecordResponseWiFiAck = CmdA0
