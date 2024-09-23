# coding:utf-8
default_Huggingface_user_token = ""

Language_without_space = ["zh","en"]
Language_dict = {
                "en": "english",
                "zht": "Traditional Chinese",
                "zhs": "Simplified Chinese ",
                 "ko":"Korean",
                 "ja":"Japanese",
                 "yue":"Cantonese",
                 "auto":"auto"

            }

Preciese_list = ['16000',
            ]

Model_names = [
                "sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20",

            ]

Device_list = ["cpu", "cuda", "auto"]
Task_list = ["transcribe" , "translate"]
ip_list = ["127.0.0.1", "0.0.0.0"]
STR_BOOL = {"False" : False, "True" : True}

SUBTITLE_FORMAT = ["ASS", "JSON", "LRC", "SMI", "SRT", "TXT", "VTT"]

CAPTURE_PARA = [
    {"rate": 44100
    ,"channel": 2
    ,"dType": 16
    ,"quality": "CD Quality"
    },
    {"rate": 48000
    ,"channel": 2
    ,"dType": 16
    ,"quality": "DVD Quality"
    },
    {"rate": 44100
    ,"channel": 2
    ,"dType": 24
    ,"quality": "Studio Quality"
    },
    {"rate": 48000
    ,"channel": 2
    ,"dType": 24
    ,"quality": "Studio Quality"
    }
]

STEMS = [
            "All Stems",
            "Vocals",
            "Other",
            "Bass",
            "Drums",
            "Vocals and Others dichotomy"
        ]

ENCODING_DICT = {"UTF-8":"utf8",
                    "UTF-8 BOM":"utf_8_sig",
                    "GBK":"gbk",
                    "GB2312":"gb18030",
                    "ANSI":"ansi"
                }

THEME_COLORS = [
    "#009faa",
    "#81D8CF",
    "#ff009f",
    "#84BE84",
    "#aaff00",
    "#FF9500",
    "#00CD00",
    "#DB4437",
    "#23CD5E",
    "#E61D34",
    "#00FF00",
    "#FF00FF",
    "#1ABC9C",
    "#FF3300",
    "#FFFF00",
    "#FFC019",
    "#FF6600",
    "#00FFFF",
    "#FF7A1D",
    "#E71A1B",
    "#FF8800",
    "#3388FF",
    "#F4B400",
    "#0069B7",
    "#FFCC00",
    "#0078D4",
]

tableItem_dark_warning_BackGround_color = "#50ffff00" # QColor(255,255,0, a=80)
tableItem_light_warning_BackGround_color  = "#50ff0000" # QColor(255,0,0,a=127)
