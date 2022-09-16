#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#define DIRECTINPUT_VERSION 0x0800
#include <dinput.h>
#pragma comment(lib, "dinput8.lib")
#pragma comment(lib, "dxguid.lib")

namespace py = pybind11;

class DinputKeyboard
{
public:
    HINSTANCE hinst;
    HWND hwnd;
    LPDIRECTINPUT8 din;
    LPDIRECTINPUTDEVICE8 dinkeyboard;

public:
    DinputKeyboard()
    {
        hinst = GetModuleHandle(NULL);
        hwnd = 0;

        DirectInput8Create(hinst, DIRECTINPUT_VERSION, IID_IDirectInput8, (void **)&din, NULL);
        din->CreateDevice(GUID_SysKeyboard, &dinkeyboard, NULL);
        dinkeyboard->SetCooperativeLevel(hwnd, DISCL_NONEXCLUSIVE | DISCL_BACKGROUND);
        dinkeyboard->SetDataFormat(&c_dfDIKeyboard);
    }

    ~DinputKeyboard()
    {
    }

    std::vector<BYTE> GetDeviceState()
    {
        std::vector<BYTE> keys(256);
        dinkeyboard->Acquire();
        dinkeyboard->GetDeviceState(256, (LPVOID)keys.data());
        return keys;
    }
};

PYBIND11_MODULE(pydinput, m)
{
    py::class_<DinputKeyboard>(m, "DinputKeyboard")
        .def(py::init<>())
        .def("get_device_state", &DinputKeyboard::GetDeviceState);
}