from machine import Pin, I2C, SoftI2C, ADC, PWM
import time
import ssd1306
import neopixel
from ahtx0 import AHT10
from pca9685 import PCA9685
from pcf8575 import PCF8575
from ADS1115 import ADS1115, ADS1115_RANGE_6144, ADS1115_128_SPS, ADS1115_CONTINUOUS
from ADS1115 import ADS1115_COMP_0_GND, ADS1115_COMP_1_GND

# ====================================================
# Configuração OLED
# ====================================================
i2c_oled = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = ssd1306.SSD1306_I2C(128, 64, i2c_oled)

# ====================================================
# I2C Expander (placa expansora)
# ====================================================
i2c_expander = I2C(0, scl=Pin(1), sda=Pin(0))

# Inicializa dispositivos tolerantes a erro
try:
    endereco_pcf = min(i2c_expander.scan())
    pcf = PCF8575(i2c_expander, endereco_pcf)
except:
    pcf = None

try:
    pca = PCA9685(i2c_expander)
    pca.freq(50)
except:
    pca = None

try:
    aht = AHT10(i2c_expander)
    tem_aht10 = True
except:
    aht = None
    tem_aht10 = False

# ====================================================
# INA226 no barramento separado (GP2=SDA, GP3=SCL)
# ====================================================
INA226_ADDR = 0x44
i2c_ina = SoftI2C(scl=Pin(3), sda=Pin(2))

# Scanner I2C
print("Dispositivos no I2C0:", i2c_expander.scan())
print("Dispositivos no I2C1:", i2c_ina.scan())
print("Usando endereço do PCF:", (endereco_pcf))

# Registradores INA226
CONFIG_REG = 0x00
SHUNT_VOLTAGE_REG = 0x01
BUS_VOLTAGE_REG = 0x02

# Verifica se INA226 está presente
tem_ina226 = INA226_ADDR in i2c_ina.scan()

def configurar_ina226():
    if tem_ina226:
        try:
            config = 0x4127
            i2c_ina.writeto_mem(INA226_ADDR, CONFIG_REG, bytearray([config >> 8, config & 0xFF]))
        except:
            pass

def ler_tensao_bus():
    if not tem_ina226:
        return None
    try:
        data = i2c_ina.readfrom_mem(INA226_ADDR, BUS_VOLTAGE_REG, 2)
        raw = (data[0] << 8) | data[1]
        return raw * 1.25 / 1000  # Volts
    except:
        return None

def ler_tensao_shunt():
    if not tem_ina226:
        return None
    try:
        data = i2c_ina.readfrom_mem(INA226_ADDR, SHUNT_VOLTAGE_REG, 2)
        raw = (data[0] << 8) | data[1]
        if raw > 32767:
            raw -= 65536
        return raw * 2.5 / 1_000_000  # Volts
    except:
        return None

def ler_corrente(r_shunt):
    v_shunt = ler_tensao_shunt()
    if v_shunt is None:
        return None
    return (v_shunt / r_shunt) * 1000  # mA

def calcular_potencia(v_bus, corrente):
    if v_bus is None or corrente is None:
        return None
    return v_bus * corrente  # mW

# Configura INA226
configurar_ina226()
R_SHUNT = 0.1

# ====================================================
# Outros periféricos (joystick, motor, servo, buzzer, LEDs)
# ====================================================
adc_joy = ADC(Pin(26))
botaoA = Pin(5, Pin.IN, Pin.PULL_UP)
botaoB = Pin(6, Pin.IN, Pin.PULL_UP)
np = neopixel.NeoPixel(Pin(7), 25)
led_azul = Pin(11, Pin.OUT)
buzzer = Pin(10, Pin.OUT)

PWM_MIN = 160
PWM_MAX = 558

# Motor DC via TB6612FNG
MOTORES = {
    "A1": {"pwm": 9, "in1": 10 - 2, "in2": 11 - 2, "stby": 12 - 2},
    "B1": {"pwm": 8, "in1": 13 - 2, "in2": 14 - 2, "stby": 15 - 2},
    "A2": {"pwm": 7, "in1": 16 - 2, "in2": 17 - 2, "stby": 18 - 2},
    "B2": {"pwm": 6, "in1": 19 - 2, "in2": 20 - 2, "stby": 21 - 2},
}

# --- Faixas de LED dos cômodos ---
# 4 faixas em série, cada uma com 3 LEDs → total 12 LEDs
np_comodos = neopixel.NeoPixel(Pin(8), 12)

COMODOS = {
    "sala": (0, 3),
    "cozinha": (3, 6),
    "quarto": (6, 9),
    "lavanderia": (9, 12),
}

def comodo(nome, estado):
    if nome not in COMODOS:
        print("Cômodo inválido! Use: sala, cozinha, quarto, lavanderia")
        return
    
    inicio, fim = COMODOS[nome]
    cor = (250, 250, 250) if estado else (0, 0, 0)  # branco fraco ligado, apagado se 0
    
    for i in range(inicio, fim):
        np_comodos[i] = cor
    np_comodos.write()
    print(f"{'Ligado' if estado else 'Desligado'}: {nome}")

# Funções auxiliares
def angle_to_pwm(angle):
    angle = max(0, min(180, angle))
    return int((angle / 180.0) * (PWM_MAX - PWM_MIN) + PWM_MIN)

def servo(n, angulo):
    if pca:
        pwm_val = angle_to_pwm(angulo)
        try:
            pca.duty(n, 0, pwm_val)
        except:
            pass

#Abrir/Fechar portão da garagem
def portao(s):
    if s == 0:
        servo(5, 180)
    if s ==1:
        servo(5, 90)

def motor_hora(nome, velocidade):
    if not pcf or not pca:
        return
    m = MOTORES[nome]
    pwm_duty = int((velocidade / 100.0) * 4095)
    try:
        pcf.write_pin(m["stby"], 1)
        pcf.write_pin(m["in1"], 0)
        pcf.write_pin(m["in2"], 1)
        pca.duty(m["pwm"], 0, pwm_duty)
    except:
        pass

def motor_anti(nome, velocidade):
    if not pcf or not pca:
        return
    m = MOTORES[nome]
    pwm_duty = int((velocidade / 100.0) * 4095)
    try:
        pcf.write_pin(m["stby"], 1)
        pcf.write_pin(m["in1"], 1)
        pcf.write_pin(m["in2"], 0)
        pca.duty(m["pwm"], 0, pwm_duty)
    except:
        pass

def motor_parar(nome):
    if not pcf or not pca:
        return
    m = MOTORES[nome]
    try:
        pcf.write_pin(m["in1"], 0)
        pcf.write_pin(m["in2"], 0)
        pcf.write_pin(m["stby"], 1)
        pca.duty(m["pwm"], 0, 0)
    except:
        pass

def desenhar_sorriso():
    img = [
        0, 1, 1, 1, 0,
        1, 0, 0, 0, 1,
        0, 0, 0, 0, 0,
        0, 1, 0, 1, 0,
        0, 0, 0, 0, 0,
    ]
    for i in range(25):
        np[i] = (0, 0, 50) if img[i] else (0, 0, 0)
    np.write()

def tocar_musica():
    notas = [(440, 200), (494, 200), (523, 200), (587, 200)]
    for freq, dur in notas:
        buzzer_pwm = PWM(buzzer)
        buzzer_pwm.freq(freq)
        buzzer_pwm.duty_u16(30000)
        time.sleep_ms(dur)
        buzzer_pwm.duty_u16(0)
        time.sleep_ms(50)
    buzzer.off()

# ====================================================
# Inicialização
# ====================================================
angle2 = 0
last_update = time.ticks_ms()
angle1 = 0
desenhar_sorriso()

# ====================================================
# Loop principal
# ====================================================
while True:
    try:
        v_bus = ler_tensao_bus()
        corrente = ler_corrente(R_SHUNT)
        potencia = calcular_potencia(v_bus, corrente)
        if tem_aht10:
            try:
                temperatura = aht.temperature
            except:
                temperatura = None
        else:
            temperatura = None

        # Joystick → Servo1
        joy_value = adc_joy.read_u16()
        deadzone = 2000
        center = 32768
        if abs(joy_value - center) > deadzone:
            angle1 = int((joy_value / 65535) * 180)
            servo(1, angle1)

        # Servo2 gira de 60° em 60° a cada 3s
        if time.ticks_diff(time.ticks_ms(), last_update) > 3000:
            angle2 = (angle2 + 60) % 180
            servo(2, angle2)
            last_update = time.ticks_ms()

        # Controle do motor via botões
        if not botaoA.value():
            motor_hora("A1", 100)
            led_azul.toggle()
            tocar_musica()
        elif not botaoB.value():
            motor_anti("A1", 100)
            led_azul.off()
        else:
            motor_parar("A1")
            led_azul.off()

        # Atualiza OLED (seguindo padrão do código anterior)
        oled.fill(0)
        oled.text("U = {:.2f} V".format(v_bus) if v_bus is not None else "U = ---", 0, 0)
        oled.text("I = {:.3f} mA".format(corrente) if corrente is not None else "I = ---", 0, 16)
        oled.text("P = {:.3f} mW".format(potencia) if potencia is not None else "P = ---", 0, 32)
        oled.text("T = {:.1f} C".format(temperatura) if temperatura is not None else "T = ---", 0, 56)
        oled.show()

        time.sleep(0.5)

    except Exception as e:
        oled.fill(0)
        oled.text("Erro:", 0, 0)
        oled.text(str(e), 0, 10)
        oled.show()
        time.sleep(0.5)
