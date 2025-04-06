# coding:utf-8

import datetime

from typing import List, TypedDict, Union, Optional
import sherpa_onnx
class ServerParameters(TypedDict):
    recognizer: sherpa_onnx.OnlineRecognizer
    nn_pool_size: int
    max_wait_ms: float
    max_batch_size: int
    max_message_size: int
    max_queue_size: int
    max_active_connections: int
    doc_root: str
    certificate: Optional[str] = None
    port: int
    host: str = "localhost"



def outputWithDateTime(text:str):
    dateTime_ = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    print(f"\n=========={dateTime_}==========")
    print(f"=========={text}==========\n")

def secondsToHMS(t) -> str:
    try:
        t_f:float = float(t)
    except:
        print("time transform error")
        return

    H = int(t_f // 3600)
    M = int((t_f - H * 3600) // 60)
    S = (t_f - H * 3600 - M * 60)

    H = str(H)

    M = str(M)

    S = str(round(S,4))
    S = S.replace(".", ",")
    S = S.split(",")

    # 当只有整数秒数值的时候
    if len(S) < 2 :
        S.append("000")

    # 当整数位秒数值不够两位时，向前填充0
    S[0] = S[0].zfill(2)

    # 当小数位秒数值不够三位时，向后填充0
    S[1] = S[1].ljust(3, "0")

    S = ",".join(S)

    # H 与 M 至少有两位
    H = H.zfill(2)
    M = M.zfill(2)

    return H + ":" + M + ":" + S

# ---------------------------------------------------------------------------------------------------------------------------
def HMSToSeconds(t:str) -> float:

    hh,mm,ss = t.split(":")
    ss = ss.replace(",",".")

    return float(hh) * 3600 + float(mm) * 60 + float(ss)


def secondsToMS(t) -> str:
    try:
        t_f:float = float(t)
    except:
        print("time transform error")
        return

    M = t_f // 60
    S = t_f - M * 60

    M = str(int(M))
    if len(M)<2:
        M = "0" + M

    S = str(round(S,4))
    S = S.split(".")

    if len(S) < 2:
        S.append("00")

    if len(S[0]) < 2:
        S[0] = "0" + S[0]
    if len(S[1] ) < 2:
        S[1] =   S[1] + "0"
    if len(S[1]) >= 3:
        S[1] = S[1][:2]

    S:str = ".".join(S)

    return M + ":" + S

def MSToSeconds(t:str) -> float:

    mm,ss = t.split(":")
    ss = ss.replace(",",".")

    return float(mm) * 60 + float(ss)
