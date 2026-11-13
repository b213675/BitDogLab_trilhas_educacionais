# BitDogLab: trilhas educacionais de energias renováveis e automação

Material da dissertação de mestrado "Trilhas educacionais para Ciências e Energias
Renováveis baseadas em experimentação com tecnologias abertas", de Bernardo Salvador
Grael, desenvolvida na Faculdade de Engenharia Elétrica e de Computação da UNICAMP,
com orientação do Prof. Dr. Hugo E. Hernández Figueroa e coorientação do Prof. Dr.
Fabiano Fruett.

O conjunto usa a placa [BitDogLab](https://github.com/BitDogLab/BitDogLab) V7,
programada em MicroPython, e tem quatro partes:

- uma placa expansora para a BitDogLab, com entradas analógicas, portas digitais,
  16 canais PWM e acionamento de até quatro motores
- uma maquete de casa automatizada, com geração solar e eólica em miniatura
- os programas das trilhas
- o material didático, com um manual de montagem e um caderno de roteiros

As cinco trilhas são energia solar, energia eólica, maquete de casa automatizada,
PixelArt na matriz de LEDs e programação assistida por inteligência artificial.

## O que há no repositório

| Pasta ou arquivo | Conteúdo |
|---|---|
| `solar.py`, `eolic.py`, `maquete.py`, `pixel_art.py`, `motor_gerador.py` | Programas das trilhas |
| `ssd1306.py`, `ahtx0.py`, `pca9685.py`, `pcf8575.py`, `ADS1115.py` | Bibliotecas dos componentes |
| `hardware/` | Arquivos de fabricação, esquemático, ligações e lista de materiais |
| `documentos/` | Manual de montagem e utilização e caderno de roteiros experimentais |
| `dados/` | Dados anonimizados das oficinas e programa que refaz a análise |

Os programas ficam na pasta principal para que o botão **Code**, seguido de
**Download ZIP**, entregue tudo o que precisa ser gravado na placa.

## Programas

| Programa | O que faz | Bibliotecas que precisam estar na placa |
|---|---|---|
| `solar.py` | Trilha de energia solar. Mostra tensão, corrente e potência do painel (INA226), irradiância estimada (BH1750) e temperatura (AHT10). Com os botões A, B e C pressionados juntos, mostra a eficiência. | `ssd1306.py`, `ahtx0.py` |
| `eolic.py` | Trilha de energia eólica. Mostra tensão, corrente e potência do gerador (INA226), velocidade do vento medida pelo anemômetro (HMC5883L) e eficiência. | `ssd1306.py` |
| `maquete.py` | Maquete de casa automatizada. Mostra as grandezas da geração e oferece funções para digitar no terminal: `comodo`, `portao`, `servo`, `motor_hora`, `motor_anti`, `motor_parar`, `tocar_musica` e `desenhar_sorriso`. | `ssd1306.py`, `ahtx0.py`, `pca9685.py`, `pcf8575.py`, `ADS1115.py` |
| `pixel_art.py` | Trilha PixelArt. Oferece funções para desenhar na matriz de LEDs 5 x 5 pelo terminal, como `leds(x, y, r, g, b)`, `apagar()`, `gravar(id)` e `carregar(id)`. | `ssd1306.py` |
| `motor_gerador.py` | Programa complementar. Lê dois módulos INA226, um em cada barramento I2C, e mostra tensão, corrente e potência de um motor e de um gerador lado a lado, com a razão entre as duas potências. | `ssd1306.py` |

A trilha de programação assistida por inteligência artificial usa uma plataforma web
desenvolvida por Jonas Souza Pinto, que não faz parte deste repositório.

### Como gravar na placa

1. Instale o [Thonny](https://thonny.org) e o MicroPython na BitDogLab.
2. Baixe este repositório e abra a pasta no Thonny.
3. Envie para a placa as bibliotecas que o programa usa.
4. Abra o programa da trilha e execute, ou salve na placa com o nome `main.py` para
   que ele comece sozinho ao ligar.

O passo a passo, com as telas, está no manual da pasta `documentos/`.

### Parâmetros que podem ser ajustados

| Programa | Parâmetro | Valor | Significado |
|---|---|---|---|
| `solar.py` | `AREA_PAINEL` | 0,06 m x 0,11 m | Área do painel |
| `solar.py` | divisor em `ler_irradiancia` | 122 | Converte luminosidade (lux) em irradiância (W/m²), com valor aproximado para a luz do sol |
| `eolic.py` | `RAIO_ROTOR` | 0,065 m | Raio das pás e do anemômetro |
| `eolic.py` | `RHO_AR` | 1,2 kg/m³ | Densidade do ar |
| `eolic.py` | `FATOR_CALIB` | 3,0 | Fator do anemômetro de copos, valor da literatura |

## Placa expansora

A pasta `hardware/` reúne:

- `Gerber_Placa-Expansora_PCB_Placa-Expansora_2026-10-29.zip`: arquivos de fabricação
  da placa de circuito impresso
- `esquematico_placa_expansora.png`: esquemático completo
- `placa_expansora_pcb.png`: desenho da placa
- `ligacoes_placa_expansora.csv`: ligação de cada conector aos canais do PCA9685 e aos
  pinos do PCF8575, com os números usados nos programas
- `esquema_ligacoes_maquete.png`: esquemático simplificado da maquete
- `lista_de_materiais.csv`: itens de um conjunto completo, com quantidade, preço de
  varejo, loja e endereço consultado em novembro de 2026

Um conjunto completo custa cerca de R$ 1.050. A BitDogLab com os itens das trilhas de
energia soma cerca de R$ 526.

## Material didático

- `documentos/Manual_de_Montagem_e_Utilizacao.pdf`: lista de materiais, identificação
  dos componentes, instalação do ambiente de programação, esquemas de ligação e
  montagem da maquete
- `documentos/Roteiros_Experimentais.pdf`: roteiros das trilhas de energia solar e de
  energia eólica, com tabelas para os dados e espaço para os gráficos

## Dados

A pasta `dados/` traz as respostas das oficinas realizadas com 18 estudantes de uma
escola pública de Campinas (SP), em forma de contagens por nota, sem identificação
dos participantes. O programa `analise.py` refaz os números da dissertação a partir
desses arquivos. Os detalhes estão em [`dados/README.md`](dados/README.md).

## Como citar

GRAEL, B. S. **Trilhas educacionais para Ciências e Energias Renováveis baseadas em
experimentação com tecnologias abertas**. 2026. Dissertação (Mestrado em Engenharia
Elétrica) – Faculdade de Engenharia Elétrica e de Computação, Universidade Estadual de
Campinas, Campinas, 2026.

## Agradecimentos

Trabalho realizado com apoio da Fundação de Amparo à Pesquisa do Estado de São Paulo
(FAPESP), processo nº 2025/06492-0. As opiniões, hipóteses e conclusões ou
recomendações expressas neste material são de responsabilidade do autor e não
necessariamente refletem a visão da FAPESP.
