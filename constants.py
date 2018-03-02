from enum import Enum
class OS(Enum):
    linux = 1
    mac = 2
    windows = 3
    unknown = 4

GAME_NAME = "MOONPOLY"
C_RED = 255,0,0
C_CYAN = 0,255,255
C_YELLOW = 255,255, 0
C_CORAL = 255,127, 80
C_BROWN = 139,69,19
C_LIME = 153,255,153

C_COMMS = None

SCREEN_LENGTH = 200
SCREEN_HEIGHT = 100

from sys import platform
if platform.startswith('linux'):
    platform = OS.linux
elif platform.startswith('win'):
    platform = OS.windows
elif platform.startswith("darwin"):
    platform = OS.mac
else: platform = OS.unknown

K_COLORS = [
    ('red', C_RED),
    ('cyan', C_CYAN),
    ('yellow', C_YELLOW),
    ('coral', C_CORAL),
    ('brown', C_BROWN),
    ("comms", C_COMMS),
]



K_UTILS = [
    "comms",

]

K_COLOR_SET = set(K_COLORS)
K_UTIL_SET = set(K_UTILS)
K_NON_UTILS = []
for i in K_COLORS:
    if i[0] in K_UTILS:
        K_NON_UTILS.append(i)


K_CHANCE = [
    ("GIVE", 100),
    ("GIVE", 200)
]
def ChanceApply(item,player):
    if item[0] == 'GIVE':
        player.money += item[1]

K_GO_MONEY = 2000