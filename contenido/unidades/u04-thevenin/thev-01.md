---
id: thev-01
unidad: u04-thevenin
titulo: Equivalente de Thévenin
objetivos:
  - Calcular el voltaje de Thévenin como voltaje en circuito abierto.
  - Calcular la resistencia de Thévenin apagando las fuentes independientes.
  - Usar el equivalente de Thévenin para calcular la corriente en una carga.
conceptos:
  - Equivalente de Thévenin
  - Voltaje de Thévenin
  - Resistencia de Thévenin
  - Apagar fuentes independientes
ejercicios:
  - id: thev-01-voltaje
    tipo: numeric
    enunciado: "Una fuente de {Vs} V alimenta R1 = {R1} Ω en serie con R2 = {R2} Ω. Las terminales a y b están en los extremos de R2 y no hay nada conectado entre ellas. ¿Cuánto vale el voltaje de Thévenin?"
    parametros:
      Vs: { min: 6, max: 24, paso: 1 }
      R1: { min: 1, max: 20, paso: 1 }
      R2: { min: 1, max: 20, paso: 1 }
    solucion: "Vs * R2 / (R1 + R2)"
    unidad: V
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "Vth es el voltaje entre a y b sin carga. Como no sale corriente por las terminales, R1 y R2 forman un divisor de voltaje: Vth = Vs · R2 / (R1 + R2)."
    pistas:
      - "El voltaje de Thévenin se mide entre a y b sin conectar nada."
      - "Sin carga, R1 y R2 llevan la misma corriente: es un divisor de voltaje."

  - id: thev-01-resistencia
    tipo: numeric
    enunciado: "Una fuente de {Vs} V alimenta R1 = {R1} Ω en serie con R2 = {R2} Ω. Las terminales a y b están en los extremos de R2. ¿Cuánto vale la resistencia de Thévenin vista desde a y b?"
    parametros:
      Vs: { min: 6, max: 24, paso: 1 }
      R1: { min: 1, max: 20, paso: 1 }
      R2: { min: 1, max: 20, paso: 1 }
    solucion: "R1 * R2 / (R1 + R2)"
    unidad: Ω
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "Para Rth se apaga la fuente de voltaje (se reemplaza por un corto). Desde a y b, R1 queda conectado entre los mismos dos puntos que R2, así que están en paralelo: Rth = R1 · R2 / (R1 + R2). El valor de la fuente no importa."
    pistas:
      - "Para calcular Rth, primero apaga la fuente de voltaje."
      - "Con la fuente en corto, mira desde a y b: ¿R1 y R2 quedan en serie o en paralelo?"

  - id: thev-01-corriente-carga
    tipo: numeric
    enunciado: "Un circuito tiene un equivalente de Thévenin con Vth = {Vth} V y Rth = {Rth} Ω. Si se conecta una carga de {RL} Ω entre a y b, ¿qué corriente circula por la carga?"
    parametros:
      Vth: { min: 2, max: 24, paso: 1 }
      Rth: { min: 1, max: 50, paso: 1 }
      RL: { min: 5, max: 100, paso: 5 }
    solucion: "Vth / (Rth + RL)"
    unidad: A
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "Con el equivalente, el circuito es solo una malla: la fuente Vth en serie con Rth y la carga RL. Por la Ley de Ohm, I = Vth / (Rth + RL)."
    pistas:
      - "Dibuja el equivalente: una fuente Vth en serie con Rth, y la carga conectada a la salida."
      - "Rth y RL quedan en serie."

  - id: thev-01-apagar-fuente
    tipo: multiple_choice
    enunciado: "Para calcular la resistencia de Thévenin, ¿con qué se reemplaza una fuente de voltaje independiente?"
    opciones:
      - "Con un corto circuito"
      - "Con un circuito abierto"
      - "Con un resistor del mismo valor"
      - "Se deja igual"
    correcta: 0
    explicacion: "Apagar una fuente de voltaje es hacer que su voltaje valga 0 V, y el elemento con 0 V entre sus terminales sin importar la corriente es un corto circuito. Una fuente de corriente apagada, en cambio, es un circuito abierto."
    pistas:
      - "Apagar una fuente de voltaje significa que su voltaje vale 0 V."
      - "¿Qué elemento tiene 0 V entre sus terminales, pase la corriente que pase?"

  - id: thev-01-circuito-abierto
    tipo: fill_pattern
    enunciado: "El voltaje de Thévenin es el voltaje entre a y b con las terminales en circuito ___."
    respuestas_aceptadas: ["abierto"]
    explicacion: "Vth es el voltaje en circuito abierto: se mide entre a y b sin conectar ninguna carga, de modo que no sale corriente por las terminales."
    pistas:
      - "Vth se mide sin conectar ninguna carga entre a y b."
      - "Sin carga, no circula corriente entre a y b."

  - id: thev-01-diagrama-apagar
    tipo: circuit_diagram
    enunciado: "Para calcular la resistencia de Thévenin vista desde a y b, ¿qué elemento se reemplaza por un cable (un corto)? Tócalo."
    diagrama:
      elementos:
        - { id: v1, tipo: fuente_voltaje, desde: [0, 2], hasta: [0, 0], etiqueta: "V1" }
        - { id: w1, tipo: cable, desde: [0, 0], hasta: [1, 0] }
        - { id: r1, tipo: resistor, desde: [1, 0], hasta: [3, 0], etiqueta: "R1" }
        - { id: r2, tipo: resistor, desde: [3, 0], hasta: [3, 2], etiqueta: "R2" }
        - { id: w2, tipo: cable, desde: [3, 0], hasta: [5, 0] }
        - { id: w3, tipo: cable, desde: [3, 2], hasta: [5, 2] }
        - { id: w4, tipo: cable, desde: [3, 2], hasta: [0, 2] }
      nodos:
        - { punto: [5, 0], etiqueta: "a" }
        - { punto: [5, 2], etiqueta: "b" }
    correctos: [v1]
    explicacion: "Para Rth se apagan las fuentes independientes: una fuente de voltaje apagada vale 0 V, así que se reemplaza por un cable. Los resistores se quedan donde están."
    pistas:
      - "Para Rth se apagan las fuentes independientes."
      - "Una fuente de voltaje apagada vale 0 V: ¿qué elemento tiene 0 V entre sus extremos?"

---

El **teorema de Thévenin** dice que cualquier circuito lineal, visto desde dos terminales a y b, se comporta igual que una sola fuente de voltaje **Vth** en serie con una sola resistencia **Rth**. Ese par es el **equivalente de Thévenin**.

El **voltaje de Thévenin** (Vth) es el voltaje entre a y b en **circuito abierto**, es decir, sin nada conectado entre las terminales. Como no sale corriente por a y b, muchas veces se calcula con un divisor de voltaje.

La **resistencia de Thévenin** (Rth) es la resistencia que se ve desde a y b con las **fuentes independientes apagadas**. Apagar una fuente de voltaje es reemplazarla por un **corto circuito** (0 V); apagar una fuente de corriente es reemplazarla por un **circuito abierto** (0 A). Después se calcula la resistencia equivalente vista desde las terminales.

Por ejemplo, una fuente de 12 V con R1 = 4 Ω en serie y R2 = 12 Ω entre a y b: Vth = 12 · 12 / (4 + 12) = 9 V. Con la fuente en corto, R1 y R2 quedan en paralelo vistos desde a y b: Rth = (4 · 12) / (4 + 12) = 3 Ω.

La ventaja es que, con el equivalente, conectar cualquier carga RL es una sola malla: I = Vth / (Rth + RL). No hay que resolver todo el circuito de nuevo cada vez que cambia la carga.
