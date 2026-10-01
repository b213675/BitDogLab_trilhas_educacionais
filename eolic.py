# ============================================================
#  MEDIDOR DE EFICIÊNCIA EÓLICA — BitDogLab / Raspberry Pi Pico W
#  Hardware: INA226 (tensão/corrente do cooler/gerador)
#            HMC5883L (anemômetro magnético — polling via I2C)
#            OLED SSD1306, Matriz NeoPixel 5x5, Botões A/B/C + Joystick
#
#  Eficiência: η = (P / A) · (2 / (ρ · v³))
#              P  = potência elétrica medida [W]
#              A  = área varrida pelo rotor  [m²]  (π·r²)
#              ρ  = densidade do ar          [kg/m³]
#              v  = velocidade do vento      [m/s]
#
#  AUTO-CALIBRAÇÃO NO BOOT:
#  Ao iniciar, o código pede para girar o anemômetro com vento
#  normal por 8 segundos. Captura min e max da magnitude e
#  define os thresholds automaticamente:
#    THRESHOLD_HIGH = min + (max - min) * 0.75
#    THRESHOLD_LOW  = min + (max - min) * 0.25
# ============================================================

from machine import Pin, SoftI2C
import ssd1306
import neopixel
import utime
import math

# ------------------------------------------------------------
# BOTÕES (BitDogLab V7)
# ------------------------------------------------------------
btn_a  = Pin(10, Pin.IN, Pin.PULL_UP)
btn_b  = Pin(5,  Pin.IN, Pin.PULL_UP)
btn_c  = Pin(6,  Pin.IN, Pin.PULL_UP)
btn_sw = Pin(22, Pin.IN, Pin.PULL_UP)  # joystick

# ------------------------------------------------------------
# MATRIZ NEOPIXEL 5×5  (GPIO 7)
# ------------------------------------------------------------
NUM_LEDS            = 25
np                  = neopixel.NeoPixel(Pin(7), NUM_LEDS)
POTENCIA_MAX_BRILHO = 50.0   # mW para brilho máximo
matriz_ligada       = False
ultimo_estado_sw    = 1

# ------------------------------------------------------------
# PARÂMETROS DO SISTEMA EÓLICO  ← ajuste conforme seu setup
# ------------------------------------------------------------
RAIO_ROTOR     = 0.065   # raio das pás [m]
AREA_ROTOR     = math.pi * RAIO_ROTOR ** 2
RHO_AR         = 1.200   # densidade do ar [kg/m³] (~1.19 em Campinas)
SHUNT_OHM      = 0.1     # shunt do INA226 [Ω]
FATOR_CALIB    = 2.4     # fator de calibração empírico do anemômetro
JANELA_ANEM_MS = 5000    # janela de integração [ms]

# Thresholds — serão sobrescritos pela auto-calibração
THRESHOLD_HIGH = 1000
THRESHOLD_LOW  = 850

# ------------------------------------------------------------
# ENDEREÇOS I2C
# ------------------------------------------------------------
INA226_ADDR = 0x44
HMC_ADDR    = 0x1E

# ------------------------------------------------------------
# BARRAMENTOS I2C
#   i2c1 (GPIO 2/3) → OLED + INA226
#   i2c0 (GPIO 0/1) → HMC5883L
# ------------------------------------------------------------
i2c1 = SoftI2C(scl=Pin(3), sda=Pin(2))
i2c0 = SoftI2C(scl=Pin(1), sda=Pin(0))

oled = ssd1306.SSD1306_I2C(128, 64, i2c1)

tem_ina226  = INA226_ADDR in i2c1.scan()
tem_hmc5883 = HMC_ADDR    in i2c0.scan()

print("I2C0:", i2c0.scan())
print("I2C1:", i2c1.scan())
print("INA226:", tem_ina226, "| HMC5883L:", tem_hmc5883)

# ------------------------------------------------------------
# INICIALIZAÇÃO DO INA226
# ------------------------------------------------------------
if tem_ina226:
    i2c1.writeto_mem(INA226_ADDR, 0x00, bytearray([0x47, 0x27]))
    print("INA226 OK")
else:
    print("AVISO: INA226 nao encontrado - leituras eletricas desativadas")

# ------------------------------------------------------------
# INICIALIZAÇÃO DO HMC5883L
# ------------------------------------------------------------
def init_hmc5883l():
    if not tem_hmc5883:
        print("AVISO: HMC5883L nao encontrado!")
        return False
    try:
        i2c0.writeto_mem(HMC_ADDR, 0x00, b'\x78')  # 8 amostras, 75 Hz
        i2c0.writeto_mem(HMC_ADDR, 0x01, b'\x20')  # ganho padrão
        i2c0.writeto_mem(HMC_ADDR, 0x02, b'\x00')  # modo contínuo
        print("HMC5883L OK")
        return True
    except Exception as e:
        print("Erro HMC5883L:", e)
        return False

init_hmc5883l()

# ------------------------------------------------------------
# LEITURA HMC5883L
# ------------------------------------------------------------
def ler_magnitude_hmc():
    if not tem_hmc5883:
        return 0.0
    try:
        d = i2c0.readfrom_mem(HMC_ADDR, 0x03, 6)
        x = (d[0] << 8) | d[1]
        z = (d[2] << 8) | d[3]
        y = (d[4] << 8) | d[5]
        if x > 32767: x -= 65536
        if y > 32767: y -= 65536
        if z > 32767: z -= 65536
        return math.sqrt(x*x + y*y + z*z)
    except:
        return 0.0

# ------------------------------------------------------------
# LEITURA INA226
# ------------------------------------------------------------
def ler_tensao_bus():
    if not tem_ina226:
        return None
    try:
        d = i2c1.readfrom_mem(INA226_ADDR, 0x02, 2)
        return ((d[0] << 8) | d[1]) * 1.25 / 1000.0
    except:
        return None

def ler_tensao_shunt():
    if not tem_ina226:
        return None
    try:
        d   = i2c1.readfrom_mem(INA226_ADDR, 0x01, 2)
        raw = (d[0] << 8) | d[1]
        if raw > 32767:
            raw -= 65536
        return raw * 2.5 / 1_000_000.0
    except:
        return None

# ------------------------------------------------------------
# CÁLCULO DE EFICIÊNCIA EÓLICA
# ------------------------------------------------------------
def calcular_eficiencia(potencia_w, velocidade_ms):
    if potencia_w is None or velocidade_ms is None or velocidade_ms < 0.05:
        return None
    p_disp = 0.5 * RHO_AR * AREA_ROTOR * (velocidade_ms ** 3)
    if p_disp < 1e-9:
        return None
    return (potencia_w / p_disp) * 100.0

# ------------------------------------------------------------
# AUTO-CALIBRAÇÃO DO ANEMÔMETRO
# ------------------------------------------------------------
def auto_calibrar(duracao_s=8):
    """
    Coleta leituras de magnitude por duracao_s segundos com o
    anemômetro girando em velocidade nominal e calcula os
    thresholds automaticamente:
      HIGH = min + (max - min) * 0.75
      LOW  = min + (max - min) * 0.25
    Inicia automaticamente sem interação humana.
    """
    global THRESHOLD_HIGH, THRESHOLD_LOW

    mag_min =  99999.0
    mag_max = -99999.0
    amostras = 0

    # Tela inicial imediata
    oled.fill(0)
    oled.text("CALIBRANDO...", 0, 0)
    oled.text("Restam: {}s".format(duracao_s), 0, 14)
    oled.text("Min:---", 0, 30)
    oled.text("Max:---", 0, 44)
    oled.show()

    inicio           = utime.ticks_ms()
    last_oled_update = utime.ticks_ms()

    while True:
        agora   = utime.ticks_ms()
        elapsed = utime.ticks_diff(agora, inicio)
        restam  = duracao_s - int(elapsed / 1000)

        if elapsed >= duracao_s * 1000:
            break

        # Leitura rápida
        mag = ler_magnitude_hmc()
        if mag > 0:
            if mag < mag_min:
                mag_min = mag
            if mag > mag_max:
                mag_max = mag
            amostras += 1

        # Atualiza OLED a cada 500 ms por tempo
        if utime.ticks_diff(agora, last_oled_update) >= 500:
            last_oled_update = agora
            oled.fill(0)
            oled.text("CALIBRANDO...", 0, 0)
            oled.text("Restam: {}s".format(max(restam, 0)), 0, 14)
            oled.text("Min:{:.0f}".format(mag_min if mag_min < 99999 else 0), 0, 30)
            oled.text("Max:{:.0f}".format(mag_max if mag_max > -99999 else 0), 0, 44)
            oled.show()

        # Pisca matriz em ciano durante coleta
        cor = (0, 3, 3) if (elapsed // 250) % 2 == 0 else (0, 0, 0)
        for i in range(NUM_LEDS):
            np[i] = cor
        np.write()

        utime.sleep_us(500)

    # --- Verifica se a margem é suficiente ---
    margem = mag_max - mag_min

    if amostras < 10:
        oled.fill(0)
        oled.text("ERRO:", 0, 0)
        oled.text("sem leituras", 0, 16)
        oled.text("verifique HMC", 0, 32)
        oled.show()
        for i in range(NUM_LEDS):
            np[i] = (40, 0, 0)
        np.write()
        utime.sleep_ms(3000)
        return False

    if margem < 80:
        # Margem muito pequena: anemômetro pode não ter girado
        oled.fill(0)
        oled.text("AVISO:", 0, 0)
        oled.text("margem pequena", 0, 14)
        oled.text("({:.0f})".format(margem), 0, 28)
        oled.text("Verifique vento", 0, 42)
        oled.text("Usando fallback", 0, 56)
        oled.show()
        for i in range(NUM_LEDS):
            np[i] = (40, 20, 0)
        np.write()
        print("AVISO: margem={:.0f} muito pequena, usando thresholds de fallback".format(margem))
        utime.sleep_ms(3000)
        return False

    # --- Calcula thresholds ---
    THRESHOLD_HIGH = mag_min + margem * 0.75
    THRESHOLD_LOW  = mag_min + margem * 0.25

    # --- Tela de resultado ---
    oled.fill(0)
    oled.text("CALIBRADO!", 0, 0)
    oled.text("Min:{:.0f} Max:{:.0f}".format(mag_min, mag_max), 0, 14)
    oled.text("HIGH:{:.0f}".format(THRESHOLD_HIGH), 0, 30)
    oled.text("LOW: {:.0f}".format(THRESHOLD_LOW), 0, 44)
    oled.show()

    # Matriz verde por 2 s
    for i in range(NUM_LEDS):
        np[i] = (0, 40, 0)
    np.write()

    print("Calibrado: min={:.0f} max={:.0f} margem={:.0f}".format(mag_min, mag_max, margem))
    print("THRESHOLD_HIGH={:.0f} THRESHOLD_LOW={:.0f}".format(THRESHOLD_HIGH, THRESHOLD_LOW))

    utime.sleep_ms(2000)

    # Apaga matriz
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()

    return True

# ------------------------------------------------------------
# EXECUTA AUTO-CALIBRAÇÃO
# ------------------------------------------------------------
calibrado = auto_calibrar(duracao_s=8)

if not calibrado:
    print("Usando thresholds de fallback: HIGH={} LOW={}".format(THRESHOLD_HIGH, THRESHOLD_LOW))

# ------------------------------------------------------------
# VARIÁVEIS DO ANEMÔMETRO
# ------------------------------------------------------------
rotacoes        = 0
passou_por_zero = True
velocidade_ms   = 0.0
velocidade_kmh  = 0.0
rps_atual       = 0.0
last_time_anem  = utime.ticks_ms()

# Controle de atualização do display (500 ms)
last_time_display = utime.ticks_ms()
JANELA_DISPLAY_MS = 500

# Caches para o display
v_bus_cache       = None
corrente_ma_cache = None
potencia_mw_cache = None
eficiencia_cache  = None

# ------------------------------------------------------------
# LOOP PRINCIPAL
# ------------------------------------------------------------
while True:

    # ==========================================================
    # 1. POLLING DO HMC5883L — sem sleep para não perder pulsos
    # ==========================================================
    mag_val = ler_magnitude_hmc()

    if mag_val > THRESHOLD_HIGH and passou_por_zero:
        rotacoes       += 1
        passou_por_zero = False
    elif mag_val < THRESHOLD_LOW:
        passou_por_zero = True

    # ==========================================================
    # 2. JANELA DO ANEMÔMETRO
    # ==========================================================
    now        = utime.ticks_ms()
    delta_anem = utime.ticks_diff(now, last_time_anem)

    if delta_anem >= JANELA_ANEM_MS:
        seg            = delta_anem / 1000.0
        rps_atual      = rotacoes / seg
        velocidade_ms  = 2.0 * math.pi * RAIO_ROTOR * rps_atual * FATOR_CALIB
        velocidade_kmh = velocidade_ms * 3.6
        rotacoes       = 0
        last_time_anem = now
        if rps_atual == 0:
            velocidade_ms  = 0.0
            velocidade_kmh = 0.0

    # ==========================================================
    # 3. DISPLAY + ELÉTRICA (a cada 500 ms)
    # ==========================================================
    if utime.ticks_diff(utime.ticks_ms(), last_time_display) >= JANELA_DISPLAY_MS:
        last_time_display = utime.ticks_ms()

        # Leitura elétrica
        v_bus   = ler_tensao_bus()
        v_shunt = ler_tensao_shunt()

        if v_shunt is not None:
            corrente_ma = max(0.0, (v_shunt / SHUNT_OHM) * 1000.0)
        else:
            corrente_ma = None

        if v_bus is not None and corrente_ma is not None:
            potencia_mw = v_bus * corrente_ma
            potencia_w  = potencia_mw / 1000.0
        else:
            potencia_mw = None
            potencia_w  = None

        eficiencia = calcular_eficiencia(potencia_w, velocidade_ms)

        v_bus_cache       = v_bus
        corrente_ma_cache = corrente_ma
        potencia_mw_cache = potencia_mw
        eficiencia_cache  = eficiencia

        # Toggle da matriz (joystick)
        estado_sw = btn_sw.value()
        if estado_sw == 0 and ultimo_estado_sw == 1:
            matriz_ligada = not matriz_ligada
            utime.sleep_ms(50)
        ultimo_estado_sw = estado_sw

        # Brilho da matriz
        if matriz_ligada and potencia_mw is not None and potencia_mw > 0:
            fator  = min(potencia_mw / POTENCIA_MAX_BRILHO, 1.0)
            brilho = int(255 * fator)
            for i in range(NUM_LEDS):
                np[i] = (0, brilho, brilho)
            np.write()
        else:
            for i in range(NUM_LEDS):
                np[i] = (0, 0, 0)
            np.write()

        # MODO SECRETO (A + B + C)
        if btn_a.value() == 0 and btn_b.value() == 0 and btn_c.value() == 0:
            oled.fill(0)
            oled.text("MODO SECRETO", 0, 0)
            oled.text("A={:.5f}m2".format(AREA_ROTOR), 0, 13)
            oled.text("H:{:.0f} L:{:.0f}".format(THRESHOLD_HIGH, THRESHOLD_LOW), 0, 26)
            if eficiencia is not None:
                oled.text("Ef={:.2f}%".format(min(eficiencia, 999.9)), 0, 39)
                oled.text("Betz max=59.3%", 0, 52)
            else:
                oled.text("Ef=---", 0, 39)
                oled.text("sem vento ou INA", 0, 52)
            oled.show()

        else:
            # TELA NORMAL
            oled.fill(0)
            oled.text(
                "V={:.2f}V".format(v_bus_cache)
                if v_bus_cache is not None else "V=---", 0, 0)
            oled.text(
                "I={:.2f}mA".format(corrente_ma_cache)
                if corrente_ma_cache is not None else "I=---", 0, 13)
            oled.text(
                "P={:.2f}mW".format(potencia_mw_cache)
                if potencia_mw_cache is not None else "P=---", 0, 26)
            oled.text("v={:.1f}km/h".format(velocidade_kmh), 0, 39)
            oled.text("R={:.1f}".format(rps_atual), 80, 39)
            if eficiencia_cache is not None:
                oled.text("Ef={:.2f}%".format(min(eficiencia_cache, 999.9)), 0, 52)
            else:
                oled.text("Ef=---", 0, 52)
            oled.show()

        # Log serial
        print("Mag:{:.0f} | H:{:.0f} L:{:.0f} | RPS:{:.2f} | v:{:.2f}km/h | V:{} | I:{} | P:{} | Ef:{}".format(
            mag_val,
            THRESHOLD_HIGH, THRESHOLD_LOW,
            rps_atual,
            velocidade_kmh,
            "{:.3f}V".format(v_bus_cache)        if v_bus_cache       is not None else "---",
            "{:.2f}mA".format(corrente_ma_cache)  if corrente_ma_cache is not None else "---",
            "{:.3f}mW".format(potencia_mw_cache)  if potencia_mw_cache is not None else "---",
            "{:.2f}%".format(eficiencia_cache)    if eficiencia_cache  is not None else "---",
        ))

    utime.sleep_us(500)