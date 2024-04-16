# MicroPython  Driver for the Waveshare Pico OLED 1.3

This is (hopefully) an improved MicroPython driver for the [Waveshare Pico-Oled-1.3](https://www.waveshare.com/product/pico-oled-1.3.htm) derived from the one provided by Waveshare.

<img src="example.gif" />

## Features

- Derived from the MicroPython Driver for the pico OLED 1.3 by Waveshare.
- Initialization and access to the state of `key0` and `key1` via the display object.
- Better character display capabilities:
  - Better fixed and variable width fonts than the build-in font provided by `framebuf`.
  - Better `text` function:
    - Automatic wrapping of text.
    - Returns endpoint coordinates of last written character.

## Usage

- Connect the display to the Raspberry Pi Pico W.
- Flash the Pico W with the latest [MicroPython](https://micropython.org/download/rp2-pico-w/).
- Copy the codebase to the Raspberry Pi Pico or (Pico W).
- Use as below:
```
>>> import PicoOled13
>>> display=PicoOled13.get()
>>> display.clear()
>>> if display.is_pressed(display.KEY0):
>>>     loc=display.text("Key0 pressed",0,0,0xffff):
>>> if display.is_pressed(display.KEY1):
>>>     loc=display.text("Key1 pressed too",0,loc[1],0xffff):
>>> display.show()
```

## Acknowledgements

- The [pico-2fa-totp](https://github.com/eddmann/pico-2fa-totp) created by [Edd Mann](https://github.com/eddmann), and my derivative [fork ](https://github.com/samveen/pico-mpy-2fa-totp) which created the use-case for writing this driver

- Pico-oled-1.3 driver by [Waveshare](https://www.waveshare.com/wiki/Pico-OLED-1.3#Examples)

- [Much nicer fonts](https://github.com/markwinap/Pycom-SH1107-I2C/blob/master/lib/SH1107.py) as compared to the [blox](https://github.com/micropython/micropython/blob/master/extmod/font_petme128_8x8.h) provided by framebuf.
