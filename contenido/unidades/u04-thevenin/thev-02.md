---
id: thev-02
unidad: u04-thevenin
titulo: Norton y máxima transferencia de potencia
objetivos:
  - Convertir un equivalente de Thévenin en uno de Norton.
  - Calcular la resistencia de Thévenin cuando hay fuentes de corriente.
  - Calcular la carga que recibe la máxima potencia y cuánta potencia es.
conceptos:
  - Equivalente de Norton
  - Corriente de Norton
  - Máxima transferencia de potencia
ejercicios:
  - id: thev-02-corriente-norton
    tipo: numeric
    enunciado: "Un circuito tiene un equivalente de Thévenin con Vth = {Vth} V y Rth = {Rth} Ω. ¿Cuánto vale la corriente de Norton?"
    parametros:
      Vth: { min: 2, max: 24, paso: 1 }
      Rth: { min: 1, max: 50, paso: 1 }
    solucion: "Vth / Rth"
    unidad: A
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "La corriente de Norton es la corriente en corto circuito entre a y b. Si se ponen en corto las terminales del equivalente de Thévenin, solo queda Rth: IN = Vth / Rth."
    pistas:
      - "La corriente de Norton es la que circula si unes a y b con un cable."
      - "Con a y b en corto, la fuente Vth solo ve a Rth."

  - id: thev-02-potencia-maxima
    tipo: numeric
    enunciado: "Un circuito tiene un equivalente de Thévenin con Vth = {Vth} V y Rth = {Rth} Ω. ¿Cuál es la potencia máxima que puede entregar a una carga?"
    parametros:
      Vth: { min: 5, max: 24, paso: 1 }
      Rth: { min: 2, max: 50, paso: 2 }
    solucion: "Vth^2 / (4 * Rth)"
    unidad: W
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "La potencia es máxima cuando RL = Rth. Entonces la corriente es Vth / (2 · Rth) y la potencia en la carga es P = I² · RL = Vth² / (4 · Rth)."
    pistas:
      - "Primero averigua qué valor de carga recibe la máxima potencia."
      - "Con RL = Rth, calcula la corriente de la malla y luego P = I² · RL."

  - id: thev-02-rth-fuente-corriente
    tipo: numeric
    enunciado: "Entre las terminales a y b hay una fuente de corriente de {Is} A en paralelo con R1 = {R1} Ω, y una resistencia R2 = {R2} Ω en serie entre ese arreglo y la terminal a. ¿Cuál es la resistencia de Thévenin vista desde a y b?"
    parametros:
      Is: { min: 1, max: 5, paso: 1 }
      R1: { min: 2, max: 40, paso: 2 }
      R2: { min: 1, max: 30, paso: 1 }
    solucion: "R1 + R2"
    unidad: Ω
    tolerancia: { tipo: relativa, valor: 0.01 }
    explicacion: "Para Rth se apaga la fuente de corriente, que se convierte en un circuito abierto. Desde a y b solo quedan R1 y R2 en un único camino: Rth = R1 + R2. El valor de la fuente no importa."
    pistas:
      - "Para calcular Rth, primero apaga la fuente de corriente."
      - "Una fuente de corriente apagada es un circuito abierto: ¿qué resistores quedan en el camino entre a y b?"

  - id: thev-02-carga-maxima
    tipo: multiple_choice
    enunciado: "¿Con qué resistencia de carga RL recibe la máxima potencia un circuito cuya resistencia de Thévenin es Rth?"
    opciones:
      - "RL = 0"
      - "RL = Rth"
      - "RL = 2 · Rth"
      - "RL lo más grande posible"
    correcta: 1
    explicacion: "Con RL muy pequeña pasa mucha corriente pero casi no cae voltaje en la carga; con RL muy grande cae mucho voltaje pero casi no pasa corriente. El punto medio óptimo es RL = Rth."
    pistas:
      - "Si RL = 0 no cae voltaje en la carga, y si RL es enorme casi no pasa corriente."
      - "El óptimo está en un punto intermedio que depende solo del circuito que alimenta la carga."

  - id: thev-02-norton-paralelo
    tipo: fill_pattern
    enunciado: "En el equivalente de Norton, la fuente de corriente IN va en ___ con la resistencia RN."
    respuestas_aceptadas: ["paralelo"]
    explicacion: "El equivalente de Norton es una fuente de corriente IN en paralelo con RN, mientras que el de Thévenin es una fuente de voltaje en serie con Rth."
    pistas:
      - "En el equivalente de Thévenin, la fuente y la resistencia van en serie; en el de Norton, no."
      - "La fuente de corriente y RN están conectadas entre los mismos dos nodos, a y b."
---

El **equivalente de Norton** representa el mismo circuito que el de Thévenin, pero con una **fuente de corriente IN en paralelo** con una resistencia RN. Los dos equivalentes son intercambiables.

La resistencia es la misma en los dos: RN = Rth. La **corriente de Norton** es la corriente en **corto circuito** entre a y b: IN = Vth / Rth. Al revés, Vth = IN · RN.

Cuando el circuito tiene fuentes de corriente, Rth se calcula igual que antes: se apagan las fuentes independientes. Una fuente de corriente apagada es un **circuito abierto**, así que se quita junto con lo que quede colgando de ella.

**Máxima transferencia de potencia:** un circuito entrega la mayor potencia posible a una carga cuando RL = Rth. Con una carga muy pequeña pasa mucha corriente pero casi no cae voltaje en ella; con una carga muy grande cae mucho voltaje pero casi no pasa corriente.

Con RL = Rth, la corriente es Vth / (2 · Rth) y la potencia máxima es Pmax = Vth² / (4 · Rth). Por ejemplo, con Vth = 12 V y Rth = 6 Ω, Pmax = 144 / 24 = 6 W.
