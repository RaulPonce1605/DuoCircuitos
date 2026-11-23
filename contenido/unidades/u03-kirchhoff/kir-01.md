---
id: kir-01
unidad: u03-kirchhoff
titulo: Leyes de Kirchhoff
objetivos:
  - Aplicar la Ley de Corrientes de Kirchhoff en un nodo.
  - Aplicar la Ley de Voltajes de Kirchhoff en una malla.
  - Resolver una malla con fuentes que se oponen.
conceptos:
  - Nodo y malla
  - Ley de Corrientes de Kirchhoff (LCK)
  - Ley de Voltajes de Kirchhoff (LVK)
  - Conservación de la carga y de la energía
ejercicios:
  - id: kir-01-lck
    tipo: numeric
    enunciado: "A un nodo entran dos corrientes de {I1} A y {I2} A. Salen dos ramas: por una salen {I3} A. ¿Cuánta corriente sale por la otra rama?"
    parametros:
      I1: { min: 2, max: 10, paso: 1 }
      I2: { min: 2, max: 10, paso: 1 }
      I3: { min: 0.5, max: 3.5, paso: 0.5 }
    solucion: "I1 + I2 - I3"
    unidad: A
    tolerancia: { tipo: relativa, valor: 0.01 }
    explicacion: "Por LCK, lo que entra al nodo es igual a lo que sale: I1 + I2 = I3 + I. Despejando, I = I1 + I2 − I3."
    pistas:
      - "Toda la corriente que entra a un nodo tiene que salir."
      - "Suma lo que entra y resta lo que ya sabes que sale."

  - id: kir-01-lvk
    tipo: numeric
    enunciado: "Una malla tiene una fuente de {Vs} V y tres resistores en serie. En dos de ellos se miden caídas de {V1} V y {V2} V. ¿Cuál es la caída en el tercer resistor?"
    parametros:
      Vs: { min: 20, max: 30, paso: 1 }
      V1: { min: 2, max: 8, paso: 1 }
      V2: { min: 2, max: 8, paso: 1 }
    solucion: "Vs - V1 - V2"
    unidad: V
    tolerancia: { tipo: relativa, valor: 0.01 }
    explicacion: "Por LVK, al recorrer la malla la suma de voltajes es cero: Vs − V1 − V2 − V3 = 0. Despejando, V3 = Vs − V1 − V2."
    pistas:
      - "Recorre la malla completa sumando subidas y restando caídas."
      - "Lo que sube la fuente debe ser igual a la suma de lo que bajan los resistores."

  - id: kir-01-fuentes-opuestas
    tipo: numeric
    enunciado: "Una malla tiene dos fuentes que se oponen, una de {V1} V y otra de {V2} V, y dos resistores de {R1} Ω y {R2} Ω, todo en serie. ¿Cuál es la corriente?"
    parametros:
      V1: { min: 10, max: 24, paso: 1 }
      V2: { min: 1, max: 9, paso: 1 }
      R1: { min: 1, max: 10, paso: 1 }
      R2: { min: 1, max: 10, paso: 1 }
    solucion: "(V1 - V2) / (R1 + R2)"
    unidad: A
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "LVK en el sentido de la fuente mayor: V1 − I · R1 − V2 − I · R2 = 0. Entonces I = (V1 − V2) / (R1 + R2), y circula en el sentido que impone la fuente mayor."
    pistas:
      - "Plantea LVK recorriendo la malla en el sentido de la fuente mayor."
      - "Si las fuentes se oponen, el voltaje neto es la diferencia entre ellas."

  - id: kir-01-principio-lck
    tipo: multiple_choice
    enunciado: "¿En qué principio físico se basa la Ley de Corrientes de Kirchhoff?"
    opciones:
      - "Conservación de la energía"
      - "Conservación de la carga"
      - "Ley de Ohm"
      - "Conservación del momento"
    correcta: 1
    explicacion: "La corriente es carga en movimiento. Como la carga no se crea ni se destruye en un nodo, lo que entra debe salir. La LVK, en cambio, se basa en la conservación de la energía."
    pistas:
      - "La LCK habla de lo que entra y sale de un nodo."
      - "¿Qué es lo que realmente fluye por los cables?"

  - id: kir-01-lvk-suma
    tipo: fill_pattern
    enunciado: "La Ley de Voltajes de Kirchhoff dice que la suma de los voltajes alrededor de una malla cerrada es igual a ___."
    respuestas_aceptadas: ["0", "cero", "0 V"]
    explicacion: "Al recorrer una malla y regresar al punto de partida, el potencial vuelve a su valor inicial: la suma de subidas y caídas es 0."
    pistas:
      - "Recorre la malla y regresa al punto de partida: ¿cuánto cambió el potencial al final?"
      - "Lo que suben las fuentes lo bajan los resistores."
---

Un **nodo** es un punto donde se unen dos o más elementos. Una **malla** es un camino cerrado que no pasa dos veces por el mismo nodo.

La **Ley de Corrientes de Kirchhoff (LCK)** dice que toda la corriente que entra a un nodo tiene que salir: Σ I que entran = Σ I que salen. Se basa en la **conservación de la carga**: en un nodo la carga no se acumula ni se pierde.

Por ejemplo, si a un nodo entran 5 A y salen dos ramas, y por una salen 2 A, por la otra salen 5 − 2 = 3 A.

La **Ley de Voltajes de Kirchhoff (LVK)** dice que, al recorrer cualquier malla cerrada, la suma de los voltajes es cero: Σ V = 0. Lo que suben las fuentes lo bajan los resistores. Se basa en la **conservación de la energía**.

Para aplicar LVK se elige un sentido de recorrido. Una fuente que se recorre de − a + suma su voltaje; un resistor que se recorre en el sentido de la corriente resta I · R. Si dos fuentes de una malla se oponen, el voltaje neto que mueve la corriente es su diferencia, y la corriente circula en el sentido que impone la fuente mayor.
