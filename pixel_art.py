# Este programa permite acender qualquer LED da matrix na cor definida pelo o usuário e também apagar todos os LEDs da matriz,
# usando duas funções para serem escritas diretamento no shell

# Função que define o controle de acendimento da posição e da cor de cada LED da Matriz
# Uso: leds(x, y, r, g, b)
# x, y: Coordenadas do LED na matriz, variando de 0 a 4
# r, g, b: Valores das cores Vermelho, Verde e Azul (0 a 225)
# Exemplo de uso:
# Acende o LED na posição central (2,2) da matriz na cor amarela (50 de vermelho, 50 de verde, 0 de azul).

# Função para desligar todos os LEDs
# Exemplo de uso: apagar()
# Esta função passa por todas as coordenadas da matriz e define todos os LEDs para preto (desligados)

# Exemplo de uso:
# Acende o LED na posição central (2,2) da matriz na cor amarela (50 de vermelho, 50 de verde, 0 de azul).
#Digite no shell: leds(2, 2, 50, 50, 0)

# Apaga todos os LEDs da matriz
#Digite no shell: apagar()

# Função para gravar bitmap na memória
# gravar(id), onde id deve ser um inteiro de 0 a 24, caso não passe nenhum argumento na função id=0
# Exemplo de uso: gravar(4)

#Função para carregar bitmap gravado na memória
"""
carregar(id)
"""
# onde id deve ser um inteiro de 0 a 24, caso não passe nenhum argumento na função id=0
# Exemplo de uso: carregar(22)

#Função bitmaps facilita colorir a matriz de leds usando letras para aas cores de cada posição:
"""
bitmaps = [
[ g, g, g, g, g ],
[ m, m, r, m, m ],
[ m, m, m, m, m ],
[ g, m, m, m, g ],
[ g, g, m, g, g ]
]
"""
# onde as cores são defininas com os argumentos:
"""
b = (0, 0, 1*it) # BLUE
g = (0, 1*it, 0) # GREEN
r = (1*it, 0, 0) # RED
y = (1*it, 1*it, 0) # YELLOW
m = (1*it, 0, 1*it) # MAGENTA
c = (0, 1*it, 1*it) # CYAN
w = (1*it, 1*it, 1*it) # WHITE
o = (0, 0, 0) # BLACK
"""

#Função para mostrar na matriz de leds o bitmaps desenhado
"""
matriz(bitmaps)
"""

#PROGRAMA PRINCIPAL
'''from machine import Pin, PWM
import neopixel
from utime import sleep  # Apenas utime.sleep para pausar

# Configuração do Buzzer A no GPIO21
buzzer = PWM(Pin(21))  # Configura o PWM no GPIO21

# Função para gerar um beep com volume ainda mais reduzido
def beep(frequency, duration, volume=5000):  # Volume mais baixo ainda
    buzzer.freq(frequency)  # Define a frequência do beep
    buzzer.duty_u16(volume)  # Define o duty cycle (controla o volume)
    sleep(duration)   # Mantém o beep por um tempo
    buzzer.duty_u16(0)      # Para o som ao final

# Função para simular o som do R2D2 com variações de beep
def r2d2_sound():
    beep(1000, 0.1)  # Beep curto, frequência média
    beep(1200, 0.1)  # Frequência um pouco mais alta
    beep(1500, 0.08)  # Frequência mais alta e duração mais curta
    beep(900, 0.12)  # Frequência baixa
    beep(1700, 0.05)  # Frequência alta e curta
    beep(1300, 0.1)  # Frequência intermediária
    beep(1100, 0.09)  # Frequência média
    beep(1600, 0.07)  # Frequência alta e curta
    beep(1400, 0.08)  # Frequência intermediária
    sleep(0.3)  # Pequena pausa entre os sons

# Toca o som no estilo R2D2 com volume ainda mais reduzido
r2d2_sound()
'''
import utime
from machine import I2C, Pin, PWM
from ssd1306 import SSD1306_I2C
import neopixel
from math import sin, cos, pi
from utime import sleep  # Apenas utime.sleep para pausar

# Configuração do Buzzer A no GPIO21
buzzer = PWM(Pin(21))  # Configura o PWM no GPIO21

# Função para gerar um beep com volume ainda mais reduzido
def beep(frequency, duration, volume=5000):  # Volume mais baixo ainda
    buzzer.freq(frequency)  # Define a frequência do beep
    buzzer.duty_u16(volume)  # Define o duty cycle (controla o volume)
    utime.sleep(duration)   # Mantém o beep por um tempo
    buzzer.duty_u16(0)      # Para o som ao final

# Função para simular o som do R2D2 com variações de beep
def r2d2_sound():
    beep(1000, 0.1)  # Beep curto, frequência média
    beep(1200, 0.1)  # Frequência um pouco mais alta
    beep(1500, 0.08)  # Frequência mais alta e duração mais curta
    beep(900, 0.12)  # Frequência baixa
    beep(1700, 0.05)  # Frequência alta e curta
    beep(1300, 0.1)  # Frequência intermediária
    beep(1100, 0.09)  # Frequência média
    beep(1600, 0.07)  # Frequência alta e curta
    beep(1400, 0.08)  # Frequência intermediária
    utime.sleep(0.3)  # Pequena pausa entre os sons

# Configuração do display OLED
WIDTH = 128  # Largura do display
HEIGHT = 64  # Altura do display
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Função para desenhar um círculo na tela
def draw_circle(x_center, y_center, radius):
    for angle in range(0, 360, 10):  # Percorre ângulos de 0 a 360 graus
        rad = angle * pi / 180  # Converte o ângulo para radianos
        x = int(x_center + radius * cos(rad))  # Calcula a coordenada x
        y = int(y_center + radius * sin(rad))  # Calcula a coordenada y
        oled.pixel(x, y, 1)  # Desenha o ponto na tela

# Função para criar o efeito de círculo crescente (3D)
def circle_3d_effect():
    x_center = WIDTH // 2  # Centro do círculo no eixo X
    y_center = HEIGHT // 2  # Centro do círculo no eixo Y

    for radius in range(5, min(WIDTH, HEIGHT)//2, 5):  # Círculos de tamanho crescente
        oled.fill(0)  # Limpa a tela
        draw_circle(x_center, y_center, radius)  # Desenha o círculo com o raio atual
        oled.show()  # Atualiza a tela
        utime.sleep(0.2)  # Pausa para criar o efeito de animação
    
    # Após o círculo grande, exibir o texto "Olá!"
    oled.fill(0)  # Limpa a tela
    oled.text("Ola!", (WIDTH // 2) - 10, (HEIGHT // 2) - 5)  # Centraliza o texto "Ola!"
    oled.text("Pessoal", 41, 40)  # Texto adicional
    oled.show()  # Exibe o texto na tela

# Função para repetir o efeito 3 vezes
def repeat_effect():
    for _ in range(3):
        #r2d2_sound()  # Toca o som R2D2
        circle_3d_effect()  # Exibe o efeito no OLED
        utime.sleep(1)  # Pausa de 1 segundo entre repetições

# Loop principal
repeat_effect()  # Chama a função para repetir o efeito 3 vezes
################################################################################
r2d2_sound()  # Toca o som R2D2

# Configurações iniciais
NUM_LEDS = 25  # Número total de LEDs na matriz 5x5
PIN = 7  # Pino onde a matriz Neopixel está conectada
np = neopixel.NeoPixel(Pin(PIN), NUM_LEDS)
desenhos = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]

# define cores para os LEDs
it = 1
b = (0, 0, 1*it)  # BLUE
g = (0, 1*it, 0)  # GREEN
r = (1*it, 0, 0)  # RED
y = (1*it, 1*it, 0)  # YELLOW
m = (1*it, 0, 1*it)  # MAGENTA
c = (0, 1*it, 1*it)  # CYAN
w = (1*it, 1*it, 1*it)  # WHITE
o = (0, 0, 0)  # BLACK

# Mapeamento da matriz de LEDs com a origem no canto inferior direito
LED_MATRIX = [
    [24, 23, 22, 21, 20],    
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5, 6, 7, 8, 9],
    [4, 3, 2, 1, 0]
]

# Botões
botao_a = Pin(5, Pin.IN, Pin.PULL_UP)
botao_b = Pin(6, Pin.IN, Pin.PULL_UP)

# Configuração do LED RGB (cátodo comum)
vermelho = Pin(13, Pin.OUT)
verde = Pin(11, Pin.OUT)
azul = Pin(12, Pin.OUT)

# Função para acender o LED Azul
def acender_azul():
    vermelho.value(0)  # Desliga o vermelho
    verde.value(0)     # Desliga o verde
    azul.value(1)      # Liga o azul

# Função para acender o LED Azul
def acender_vermelho():
    vermelho.value(1)  # Desliga o vermelho
    verde.value(0)     # Desliga o verde
    azul.value(0)      # Liga o azul
    
# Função para acender o LED Azul
def acender_verde():
    vermelho.value(0)  # Desliga o vermelho
    verde.value(1)     # Desliga o verde
    azul.value(0)      # Liga o azul

# Função para apagar o LED RGB
def apagar_rgb():
    vermelho.value(0)
    verde.value(0)
    azul.value(0)

# Função que define o controle de acendimento da posição e da dor de cada LED da Matriz do BitDogLab
def leds(x, y, r=25, g=25, b=25):
    if 0 <= x <= 4 and 0 <= y <= 4 and r <= 255 and g <= 255 and b <= 255:
        led_index = LED_MATRIX[4-y][x]
        np[led_index] = (r, g, b)
        np.write()
        acender_azul()
        sleep(.01)
        apagar_rgb()
        return f'Posicao: (x={x},y={y}) na cor: ({r},{g},{b})'

    elif x > 4:
        acender_vermelho()
        sleep(.2)
        apagar_rgb()
        return f'Valor escolhido x={x} invalido, escolha um valor entre 0 e 4'
    elif y > 4:
        acender_vermelho()
        sleep(.2)
        apagar_rgb()
        return f'Valor escolhido y={y} invalido, escolha um valor entre 0 e 4'
    elif r > 255 or g > 255 or b > 255:
        acender_vermelho()
        sleep(.2)
        apagar_rgb()
        return f'Valor escolhido de cor ({r},{g},{b}) inválido, escolha um valor entre 0 e 255 para cada cor'
    else:
        return f'Coordenadas invalidas, escolha um valor x<=4 e y<=4 e valores para R G B <= 255.'


def apagar():
    """
    Função apagar, digite apagar() parar apagar todos os bitmaps da matriz 5x5
    """
    np.fill((0,0,0))
    np.write()
    acender_azul()
    sleep(.2)
    apagar_rgb()


def gravar(id=0):
    if(id <= 24):        
        for y in range(5):
            for x in range(5):
                led_index = LED_MATRIX[4-y][x]
                valor = np.__getitem__(led_index)
                desenhos[id].update({led_index : valor})
        apagar()
        acender_azul()
        sleep(.2)
        apagar_rgb()
        return f'Bitmap gravado na posicao: {id}'
    else:
        acender_vermelho()
        sleep(.2)
        apagar_rgb()
        return f'Escolha um valor entre 0 e 24'


def matriz(LED_MATRIX = LED_MATRIX, it=20):
    acender_verde()
    sleep(.1)
    apagar_rgb()
    

    apagar()

    for Y in range(5):
        for X in range(5):
            #print(LED_MATRIX)
            led_index = LED_MATRIX[4-Y][X]
            if led_index == r:
                leds(X, Y, r[0]*it, r[1]*it, r[2]*it)
            elif led_index == g:
                leds(X, Y, g[0]*it, g[1]*it, g[2]*it)
            elif led_index == b:
                leds(X, Y, b[0]*it, b[1]*it, b[2]*it)
            elif led_index == y:
                leds(X, Y, y[0]*it, y[1]*it, y[2]*it)
            elif led_index == m:
                leds(X, Y, m[0]*it, m[1]*it, m[2]*it)
            elif led_index == c:
                leds(X, Y, c[0]*it, c[1]*it, c[2]*it)
            elif led_index == w:
                leds(X, Y, w[0]*it, w[1]*it, w[2]*it)
            elif led_index == o:
                leds(X, Y, o[0]*it, o[1]*it, o[2]*it)
            else:
                leds(X, Y, 0, 0, 0)

def carregar(id=0):
    if(id <= 24):
        if bool(desenhos[id]):
            
            for teste in range(25):
                np[teste] = desenhos[id].get(teste)
            np.write()
            acender_verde()
            sleep(.2)
            apagar_rgb()
            return f'Bitmap carregado da posicao: {id}'
            
        else:
            acender_vermelho()
            sleep(.2)
            apagar_rgb()
            return f'Nao existe desenho gravado na posicao: {id}'
    else:
            acender_vermelho()
            sleep(.2)
            apagar_rgb()
            return f'Escolha um valor entre 0 e 24'


def loop(tempo=1):
    while True:
        for id in range(len(desenhos)):
            if bool(desenhos[id]):
                carregar(id)
                sleep(tempo)
                acender_verde()
                sleep(.2)
                apagar_rgb()


def jogo_da_velha():
    apagar()  # Garante que todos os LEDs estão apagados inicialmente
    coordenadas = [(1,0), (1,1), (1,2), (1,3), (1,4),
                   (3,0), (3,1), (3,2), (3,3), (3,4),
                   (0,1), (1,1), (2,1), (4,1), (0,3),
                   (1,3), (2,3), (4,3) ]
    for cor in coordenadas:
        print(f'Acendendo LED em cor')
        leds(cor[0], cor[1], 15, 15, 15)
        sleep(0.5)

    
# Exemplos de uso
leds(2, 2, 30, 0, 30)  # Acende o LED central em vermelho


