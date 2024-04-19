from machine import Pin,SPI
import framebuf
import time
import BasicFont

# Pin Definitions
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

KEY0=15
KEY1=17

# Display object
display=None

class OLED_1inch3_SPI(framebuf.FrameBuffer):
    def __init__(self):
        self.is_on=0
        self.width = 128
        self.height = 64

        self.white =   0xffff
        self.black =   0x0000

        self.font=BasicFont.BasicFontCondensed

        # framebuf init
        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HMSB)

        # SPI init
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)

        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,2000_000)
        self.spi = SPI(1,20000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)

        # display init
        self.init_display()

        # Clear the screen on init - needs frambuf init, spi init and display init
        self.clear()

        # Init Keys
        self.KEY0=KEY0
        self.KEY1=KEY1
        self.key0=Pin(KEY0,Pin.IN,Pin.PULL_UP)
        self.key1=Pin(KEY1,Pin.IN,Pin.PULL_UP)

    def is_pressed(self, key):
        if key == self.KEY0:
            return not(self.key0.value())
        elif key == self.KEY1:
            return not(self.key1.value())
        else:
            return None

    def on(self):
        if not self.is_on:
            self.write_cmd(0xAF)
            self.is_on=1

    def off(self):
        if self.is_on:
            self.write_cmd(0xAE)
            self.is_on=0

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize display"""
        self.rst(1)
        time.sleep(0.001)
        self.rst(0)
        time.sleep(0.01)
        self.rst(1)

        self.off()

        self.write_cmd(0x00)   # set lower column address
        self.write_cmd(0x10)   # set higher column address

        self.write_cmd(0xB0)   # set page address

        self.write_cmd(0xdc)   # set display start line
        self.write_cmd(0x00)   # (2nd param)

        self.write_cmd(0x81)   # contract control
        self.write_cmd(0x80)   # 128

        self.write_cmd(0x21)   # Set Memory addressing mode (0x20/0x21) #
        self.write_cmd(0xa0)   # set segment remap
        self.write_cmd(0xc0)   # Com scan direction
        self.write_cmd(0xa4)   # Disable Entire Display On (0xA4/0xA5)
        self.write_cmd(0xa6)   # normal / reverse

        self.write_cmd(0xa8)   # multiplex ratio ??
        self.write_cmd(0x3f)   # duty = 1/64 ??

        self.write_cmd(0xd3)   # set display offset
        self.write_cmd(0x60)

        self.write_cmd(0xd5)   # set osc division
        self.write_cmd(0x50)

        self.write_cmd(0xd9)   # set pre-charge period
        self.write_cmd(0x22)

        self.write_cmd(0xdb)   # set vcomh
        self.write_cmd(0x35)

        self.write_cmd(0xad)   # set charge pump enable
        self.write_cmd(0x8a)   #Set DC-DC enable (a=0:disable; a=1:enable)

        self.on()


    # Shows the framebuffer contents on the display.
    # If no arguments are given, the full frame buffer is sent to the display.
    # startXPage:  The horizontal page index to start the update. The X-axis is divided in 16 8-pixel 'pages' (0 ~ 15)
    # startYLine:  The vertical line index to start the display update (0 ~ 63)
    # startYPage:  The horizontal page index to end the update (exluding that line index). (1 ~ 16)
    # endYLine:    The vertical line index to end the display update (exluding that line index) (1 ~ 64)
    def show(self, startXPage=0, startYLine=0, endXPage=16, endYLine=64):
        
        self.__validateShowArguments(startXPage, startYLine, endXPage, endYLine)
        
        doCustomPageAddressing = startXPage > 0 or endXPage < 16

        # Indicate that for every line we'll start at Xpage 0. Need to do this only once.
        if not doCustomPageAddressing:
            self.write_cmd(0xB0)      

        for yLine in range(startYLine, endYLine):
            columnSramAddress = 63 - yLine
            
            self.write_cmd(0x00 + (columnSramAddress & 0x0f))  
            self.write_cmd(0x10 + (columnSramAddress >> 4))
            
            # Only if we're writing specific Xpages, write the startPage address again for every YLine.
            # Otherwise we can rely on automatic address incrementing of the display controller
            if doCustomPageAddressing:                         
                self.write_cmd(0xB0 + (startXPage & 0x0f))
                
            # Write the bytes for this column, for the specified pages
            for num in range(startXPage, endXPage):
                self.write_data(self.buffer[yLine * 16 + num])
                

    # Validates the input parameters for the show() method.
    def __validateShowArguments(self, startXPage, startYLine, endXPage, endYLine):
        
        if not startYLine < endYLine:
            raise IndexError("show(...): The startYLine (" + str(startYLine) + ") argument should be smaller than the endYLine (" + str(endYLine) + ") argument.")
        if startYLine < 0 or startYLine > 63: 
            raise IndexError("show(...): The startYLine argument acceptable range is 0 ~ 63. Given: " + str(startYLine))
        if endYLine < 1 or endYLine > 64: 
            raise IndexError("show(...): The endYLine argument acceptable range is 1 ~ 64. Given: " + str(endYLine))
        
        if not startXPage < endXPage:
            raise IndexError("show(...): The startXPage (" + str(startXPage) + ") argument should be smaller than the endXPage (" + str(endXPage) + ") argument.")
        if startXPage < 0 or startXPage > 15:
            raise IndexError("show(...): The startXPage argument acceptable range is 0 ~ 15. Given: " + str(startXPage))
        if endXPage < 1 or endXPage > 16:
            raise IndexError("show(...): The endXPage argument acceptable range is 1 ~ 16. Given: " + str(endXPage))
        


    def clear(self):
        self.fill(self.black)
        self.show()

    def text(self,s,x0,y0,col=0xffff,wrap=1,just=0):
        if len(s)==0:
            return(x0, y0)

        x=x0
        pixels = bytearray([])
        for i in range(len(s)):
            C = ord(s[i])
            if C < 32 or C > 127:
                C = 32
            cdata = self.font[C - 32]

            # check wrap/clip at edge of screen
            if len(pixels) and \
                    ((just==0 and x+len(pixels)+len(cdata) > self.width) or \
                    (just==1 and x-len(pixels)-len(cdata) < 0) or \
                    (just==2 and x-len(pixels)/2-len(cdata) < 0) or \
                    (just==2 and x+len(pixels)/2+len(cdata) > self.width)):
                if col==0:
                    for i, v in enumerate(pixels): pixels[i] = 0xFF & ~ v
                fb = framebuf.FrameBuffer(pixels, len(pixels), 8, framebuf.MONO_VLSB)
                if just==0:
                    self.blit(fb, x, y0)
                elif just==1:
                    self.blit(fb, x-len(pixels), y0)
                else:
                    self.blit(fb, x-int(len(pixels)/2), y0)
                pixels = bytearray([])

                if wrap == 0:
                    # clip text at right of screen
                    return [x,y0+9]
                if wrap == 1:
                    # wrap to start of line
                    x=0
                else:
                    # wrap to X0 co-ordinate
                    x=x0
                y0=y0+9

                if y0 > self.height:
                    return [x,y0+9]

            pixels += bytearray(cdata)

        if col==0:
            for i, v in enumerate(pixels): pixels[i] = 0xFF & ~ v
        fb = framebuf.FrameBuffer(pixels, len(pixels), 8, framebuf.MONO_VLSB)
        if just==0:
            self.blit(fb, x, y0)
        elif just==1:
            self.blit(fb, x-len(pixels), y0)
        else:
            self.blit(fb, x-int(len(pixels)/2), y0)

        return [x,y0+9]

def get():
    global display
    if display is None:
        display=OLED_1inch3_SPI()
    return display


def test():
    display = get()
    display.clear()
    print("Running display tests")
        
    # Test sequence to validate Xpage and YLine writing to the display
    display.fill(1)
    display.show()
    display.fill(0)
    display.show()
    
    # Fill the framebuffer with white, bonly only the specifically updated regions should show up in white on the display
    display.fill(1)
    display.show(0,0, 16, 8)     # Top horizontal bar
    display.show(0,56, 16,64)    # Bottom horizontal bar
    display.show(0, 8, 1, 56)    # Vertical bar on the left, partially drawn
    display.show(7, 24, 9, 40)   # 16 x 16 pixel Square section in the middle
    
    

if __name__=='__main__':
    test()
