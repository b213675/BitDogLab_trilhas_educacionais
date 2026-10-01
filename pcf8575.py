class PCF8575:
    def __init__(self, i2c, address=0x20):
        self.i2c = i2c
        self.address = address
        self.state = 0xFFFF  # Inicialmente todas as portas como HIGH (entrada com pull-up)

        self.i2c.writeto(self.address, self.state.to_bytes(2, 'little'))

    def write(self, value):
        """Escreve os 16 bits de uma vez."""
        self.state = value & 0xFFFF
        self.i2c.writeto(self.address, self.state.to_bytes(2, 'little'))

    def read(self):
        """Lê os 16 bits de entrada."""
        data = self.i2c.readfrom(self.address, 2)
        return int.from_bytes(data, 'little')

    def write_pin(self, pin, value):
        """Define individualmente o estado de um pino (0-15)."""
        if pin < 0 or pin > 15:
            raise ValueError("Pino deve estar entre 0 e 15")
        if value:
            self.state |= (1 << pin)
        else:
            self.state &= ~(1 << pin)
        self.write(self.state)

    def read_pin(self, pin):
        """Lê individualmente o estado de um pino (0-15)."""
        if pin < 0 or pin > 15:
            raise ValueError("Pino deve estar entre 0 e 15")
        return (self.read() >> pin) & 1
