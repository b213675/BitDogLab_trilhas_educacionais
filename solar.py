from machine import Pin, SoftI2C
import ssd1306
import time
import neopixel
from ahtx0 import AHT10   # sensor AHT10

# Configuração dos Botões (BitDogLab V7)
btn_a = Pin(10, Pin.IN, Pin.PULL_UP)
btn_b = Pin(5, Pin.IN, Pin.PULL_UP)
btn_c = Pin(6, Pin.IN, Pin.PULL_UP)
btn_sw = Pin(22, Pin.IN, Pin.PULL_UP) # Botão do Joystick

# Configuração da Matriz de LEDs (GPIO 7)
NUM_LEDS = 25
np = neopixel.NeoPixel(Pin(7), NUM_LEDS)

# Variáveis para o Toggle da Matriz
matriz_ligada = False
ultimo_estado_sw = 1
# Defina aqui qual potência (mW) gera brilho máximo na matriz (ajuste conforme necessário)
POTENCIA_MAX_BRILHO = 50.0 

# Área do painel em m2 (6cm x 11cm)
AREA_PAINEL = 0.06 * 0.11

# Endereços I2C
INA226_ADDR = 0x44  
BH1750_ADDR = 0x23  

# I2C1 (OLED e INA) e I2C0 (Sensores)
i2c1 = SoftI2C(scl=Pin(3), sda=Pin(2))
i2c0 = SoftI2C(scl=Pin(1), sda=Pin(0))

i2c_INA226 = i2c1
i2c_BH1750 = i2c0
i2c_AHT10 = i2c0

oled = ssd1306.SSD1306_I2C(128, 64, i2c1)

# Flags e Sensores
tem_ina226 = INA226_ADDR in i2c_INA226.scan()
tem_bh1750 = BH1750_ADDR in i2c_BH1750.scan()
tem_aht10 = 0x38 in i2c_AHT10.scan()

if tem_aht10:
    try: aht = AHT10(i2c_AHT10)
    except: tem_aht10 = False

if tem_bh1750:
    try: i2c_BH1750.writeto(BH1750_ADDR, b'\x10')
    except: tem_bh1750 = False
    
print("Dispositivos no I2C0:", i2c0.scan())
print("Dispositivos no I2C1:", i2c1.scan())

def ler_tensao_bus():
    if not tem_ina226: return None
    try:
        data = i2c_INA226.readfrom_mem(INA226_ADDR, 0x02, 2)
        return ((data[0] << 8) | data[1]) * 1.25 / 1000
    except: return None

def ler_tensao_shunt():
    if not tem_ina226: return None
    try:
        data = i2c_INA226.readfrom_mem(INA226_ADDR, 0x01, 2)
        raw = (data[0] << 8) | data[1]
        if raw > 32767: raw -= 65536
        return raw * 2.5 / 1_000_000
    except: return None

def ler_irradiancia():
    if not tem_bh1750: return None
    try:
        data = i2c_BH1750.readfrom(BH1750_ADDR, 2)
        lux = ((data[0] << 8) | data[1]) / 1.2
        return lux / 126
    except: return None
    
if tem_ina226:
    # 0x4327: Ativa média de 16 amostras por hardware no INA226
    # Isso estabiliza a leitura de Corrente e Potência
    i2c1.writeto_mem(INA226_ADDR, 0x00, bytearray([0x47, 0x27]))

# Loop Principal
while True:
    v_bus = ler_tensao_bus()
    v_shunt = ler_tensao_shunt()
    corrente = (v_shunt / 0.1) * 1000 if v_shunt is not None else None
    corrente = max(0.0001, corrente)
    potencia = v_bus * corrente if v_bus and corrente else None
    wm2 = ler_irradiancia()
    temp = aht.temperature if tem_aht10 else None

    # --- Lógica de Toggle da Matriz (Botão do Joystick) ---
    estado_sw = btn_sw.value()
    if estado_sw == 0 and ultimo_estado_sw == 1:
        matriz_ligada = not matriz_ligada
        time.sleep(0.05) # Pequeno debounce
    ultimo_estado_sw = estado_sw

    # --- Controle de Brilho da Matriz ---
    if matriz_ligada and potencia is not None and potencia > 0:
        # Mapeia a potência para o brilho (0-255)
        fator = min(potencia / POTENCIA_MAX_BRILHO, 1.0)
        brilho = int(255 * fator)
        cor = (brilho, brilho, brilho) # Branco
        for i in range(NUM_LEDS):
            np[i] = cor
        np.write()
    else:
        # Desliga a matriz
        for i in range(NUM_LEDS):
            np[i] = (0, 0, 0)
        np.write()

    # Verifica se os 3 botões estão pressionados
    if btn_a.value() == 0 and btn_b.value() == 0 and btn_c.value() == 0:
        oled.fill(0)
        oled.text("MODO SECRETO", 0, 0)
        oled.text("Area = 66 cm^2", 0, 15)
        
        if potencia and wm2 and wm2 > 0.1:
            p_solar_mw = wm2 * AREA_PAINEL * 1000
            eficiencia = (potencia / p_solar_mw) * 100
            oled.text("Efic. = {:.2f} %".format(eficiencia), 0, 40)
        else:
            oled.text("Efic. = ---", 0, 40)
        oled.show()
    else:
        # PÁGINA NORMAL 
        oled.fill(0)
        oled.text("V = {:.2f} V".format(v_bus) if v_bus is not None else "V = ---", 0, 0)
        oled.text("I = {:.3f} mA".format(corrente) if corrente is not None else "I = ---", 0, 13)
        oled.text("P = {:.3f} mW".format(potencia) if potencia is not None else "P = ---", 0, 26)
        oled.text("L = {:.2f} W/m^2".format(wm2) if wm2 is not None else "L = ---", 0, 39)
        oled.text("T = {:.1f} C".format(temp) if temp is not None else "T = ---", 0, 53)
        oled.show()

    time.sleep(0.1)