from enum import Enum

class NodeId(Enum):

    piece_WHOut_Sync = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.OPC_UA.piece_WHOut_Sync"
    piece_WHOut = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.OPC_UA.piece_WHOut"
    
    piece_WHIn_Sync = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.OPC_UA.piece_WHIn_Sync"
    piece_WHIn = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.OPC_UA.piece_WHIn"
    
    pusher1_Out_Sync = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.OPC_UA.pusher_Out_Sync[1]"
    pusher1_Out = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.OPC_UA.pusher_Out[1]"

    pusher2_Out_Sync = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.OPC_UA.pusher_Out_Sync[2]"
    pusher2_Out = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.OPC_UA.pusher_Out[2]"

    loading_Out_Sync = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.OPC_UA.loading_Out_Sync"
    loading_out_sync1 = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.OPC_UA.loading_Out_Sync[1]"
    loading_out_sync2 = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.OPC_UA.loading_Out_Sync[2]"

    m_tool = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.OPC_UA.m_tool"
    m_active_tool = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.OPC_UA.m_active_tool"