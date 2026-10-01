# pca9685.py
import time

class PCA9685:
    def __init__(self, i2c, address=0x40):
        self.i2c = i2c
        self.address = address
        self.reset()

    def reset(self):
        self.write8(0x00, 0x00)

    def freq(self, freq_hz):
        prescale_val = int(25000000.0 / (4096 * freq_hz) - 1)
        oldmode = self.read8(0x00)
        self.write8(0x00, (oldmode & 0x7F) | 0x10)
        self.write8(0xFE, prescale_val)
        self.write8(0x00, oldmode)
        time.sleep_ms(5)
        self.write8(0x00, oldmode | 0xa1)

    def duty(self, channel, on, off):
        reg = 0x06 + 4 * channel
        self.write8(reg, on & 0xFF)
        self.write8(reg + 1, on >> 8)
        self.write8(reg + 2, off & 0xFF)
        self.write8(reg + 3, off >> 8)

    def write8(self, reg, value):
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def read8(self, reg):
        return int.from_bytes(self.i2c.readfrom_mem(self.address, reg, 1), 'little')
