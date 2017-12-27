import numpy as np
import serial
import time

from display.abstract_display import AbstractDisplay


class SerialDisplay(AbstractDisplay):
    def __init__(self, width=16, height=16, port="/dev/ttyUSB0"):
        super(SerialDisplay, self).__init__(width, height)

        self.ser = serial.Serial(port, 115200)
        time.sleep(2)

        self.show()

    def show(self, gamma=False):

        buf = self.buffer.flatten().tolist()
        self.ser.write(buf)
        time.sleep(0.1)

if __name__ == "__main__":
    display = SerialDisplay()
   # display.run_benchmark()
    display.create_test_pattern()
    display.show()
    time.sleep(5)
