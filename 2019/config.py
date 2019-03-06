#
# vision parameter groups (aka configs)
#
# given the name of a config (eg "greenled") access via:
#
#  import config
#  cfg = getattr(config, "greenled")
#
greenled = {
    "name": "greenled",
    "picam": {
        "iso": 400,  # 100-800 (higher numbers are brighter)
        "brightness": 20,
        "contrast": 100,
        "flip": True,
        "rotate": 90,
        "exposure_mode": "fireworks",
        "exposure_compensation": -25, # [-25, 25]
    },
    "algo": {
    }
}

noled = {
    "name": "noled",
    "picam": {
        "iso": 400,
        "brightness": 40,
        "contrast": 100,
        "flip": False,
        "rotate": 0,
        "exposure_mode": "off", #"fixedfps",
        "exposure_compensation": 0, # [-25, 25]
    },
    "algo": {
    }
}

default = greenled
