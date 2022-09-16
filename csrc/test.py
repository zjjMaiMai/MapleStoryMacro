import pydinput
import win32con

dinput = pydinput.DinputKeyboard()
while True:
    state = dinput.get_device_state()
    # keys macro define in <dinput.h>
    # #define DIK_Q               0x10
    if state[0x10] & 0x80:
        print("Q")
        