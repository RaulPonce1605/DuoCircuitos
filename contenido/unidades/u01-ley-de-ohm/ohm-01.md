---
id: ohm-01
unidad: u01-ley-de-ohm
titulo: Voltaje, corriente y resistencia
objetivos:
  - Distinguir voltaje, corriente y resistencia y sus unidades.
  - Calcular la corriente a partir de la carga y el tiempo.
  - Calcular la resistencia de un conductor con su resistividad, longitud y área.
conceptos:
  - Voltaje
  - Corriente eléctrica
  - Resistencia y resistividad
  - Conductancia
  - Medición con amperímetro
ejercicios:
  - id: ohm-01-unidad-resistencia
    tipo: multiple_choice
    enunciado: "¿En qué unidad se mide la resistencia eléctrica?"
    opciones:
      - "Volt"
      - "Ampere"
      - "Ohm"
      - "Watt"
    correcta: 2
    explicacion: "El volt mide voltaje, el ampere mide corriente y el watt mide potencia. La resistencia se mide en ohms (Ω)."
    pistas:
      - "Piensa qué magnitud mide cada una de las opciones."
      - "La unidad lleva el apellido del físico alemán que estudió la relación entre voltaje y corriente."

  - id: ohm-01-corriente-carga
    tipo: numeric
    enunciado: "Por un conductor pasan {Q} C de carga en {t} min. ¿Cuál es la corriente?"
    parametros:
      Q: { min: 30, max: 600, paso: 30 }
      t: { min: 1, max: 10, paso: 1 }
    solucion: "Q / (t * 60)"
    unidad: A
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "La corriente es la carga que pasa por segundo: I = Q / t. Primero se convierte el tiempo a segundos (1 min = 60 s) y después se divide la carga entre ese tiempo."
    pistas:
      - "La corriente es la cantidad de carga que pasa por un punto cada segundo."
      - "Usa I = Q / t, pero antes convierte los minutos a segundos."

  - id: ohm-01-amperimetro
    tipo: multiple_choice
    enunciado: "Un circuito tiene una fuente de voltaje y un resistor. ¿Cómo se conecta un amperímetro para medir la corriente del resistor?"
    opciones:
      - "En paralelo con el resistor"
      - "En serie con el resistor"
      - "Entre las terminales de la fuente"
      - "No importa cómo se conecte"
    correcta: 1
    explicacion: "El amperímetro mide la carga que lo atraviesa, así que debe estar en el mismo camino que el resistor: en serie. El voltímetro es el que se conecta en paralelo."
    pistas:
      - "Piensa qué tiene que atravesar el medidor para poder medir la corriente."
      - "La corriente que quieres medir tiene que pasar por dentro del medidor."

  - id: ohm-01-resistividad
    tipo: numeric
    enunciado: "Un alambre de cobre (ρ = 1.72 × 10⁻⁸ Ω·m) mide {L} m y tiene una sección de {A} mm². ¿Cuál es su resistencia?"
    parametros:
      L: { min: 10, max: 200, paso: 10 }
      A: { min: 0.5, max: 4, paso: 0.5 }
    solucion: "1.72e-8 * L / (A * 1e-6)"
    unidad: Ω
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "La resistencia de un conductor es R = ρ · L / A. El área se convierte a metros cuadrados (1 mm² = 1 × 10⁻⁶ m²) antes de sustituir."
    pistas:
      - "La resistencia crece con la longitud y disminuye con el área de la sección."
      - "Usa R = ρ · L / A y convierte el área: 1 mm² = 1 × 10⁻⁶ m²."

  - id: ohm-01-conductancia
    tipo: fill_pattern
    enunciado: "La conductancia es el inverso de la resistencia: G = 1 / ___"
    respuestas_aceptadas: ["R"]
    explicacion: "La conductancia mide qué tan fácil pasa la corriente: G = 1 / R. Se mide en siemens (S)."
    pistas:
      - "La conductancia es lo contrario de la oposición al paso de la corriente."
      - "Busca la magnitud que se mide en ohms."
---

El **voltaje** (V) es la diferencia de potencial que empuja a las cargas a moverse por un circuito. Se mide en **volts** (V).

La **corriente** (I) es la cantidad de carga que pasa por un punto cada segundo: I = Q / t, con la carga Q en coulombs (C) y el tiempo t en segundos (s). Se mide en **amperes** (A). Por ejemplo, si por un cable pasan 30 C en 10 s, la corriente es 30 C / 10 s = 3 A.

La **resistencia** (R) es la oposición de un material al paso de la corriente. Se mide en **ohms** (Ω) y depende del material, la longitud y el grosor del conductor: R = ρ · L / A, donde ρ es la **resistividad** del material (Ω·m), L la longitud (m) y A el área de la sección (m²). Un cable más largo tiene más resistencia; uno más grueso, menos.

La **conductancia** (G) es el inverso de la resistencia: G = 1 / R. Indica qué tan fácil pasa la corriente y se mide en **siemens** (S).

Para medir corriente se usa un **amperímetro**, que se conecta **en serie**: la corriente que se quiere medir tiene que atravesarlo. El **voltímetro**, en cambio, se conecta en paralelo con el elemento cuyo voltaje se quiere medir.
