---
id: kir-02
unidad: u03-kirchhoff
titulo: Análisis de nodos y de mallas
objetivos:
  - Plantear las ecuaciones de nodo con LCK y resolver voltajes de nodo.
  - Plantear las ecuaciones de malla con LVK y resolver corrientes de malla.
  - Saber cuántas ecuaciones se necesitan en cada método.
conceptos:
  - Nodo de referencia
  - Análisis de nodos
  - Análisis de mallas
  - Corriente de malla
ejercicios:
  - id: kir-02-voltaje-nodo
    tipo: numeric
    enunciado: "Una fuente de {Vs} V alimenta el nodo A a través de R1 = {R1} Ω. Desde A bajan a tierra R2 = {R2} Ω y R3 = {R3} Ω. ¿Cuál es el voltaje del nodo A?"
    parametros:
      Vs: { min: 5, max: 24, paso: 1 }
      R1: { min: 1, max: 12, paso: 1 }
      R2: { min: 1, max: 12, paso: 1 }
      R3: { min: 1, max: 12, paso: 1 }
    solucion: "Vs * (R2 * R3 / (R2 + R3)) / (R1 + R2 * R3 / (R2 + R3))"
    unidad: V
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "LCK en A: la corriente que llega por R1 sale por R2 y R3, así que (VA − Vs) / R1 + VA / R2 + VA / R3 = 0. Al despejar VA queda un divisor de voltaje entre R1 y el paralelo de R2 y R3."
    pistas:
      - "Toma la tierra como 0 V y escribe LCK en el nodo A."
      - "La corriente que llega por R1 es (Vs − VA) / R1; la que sale por cada resistor a tierra es VA / R."

  - id: kir-02-fuente-corriente
    tipo: numeric
    enunciado: "Una fuente de corriente inyecta {Is} A al nodo A. De A a tierra hay R1 = {R1} Ω; de A al nodo B hay R2 = {R2} Ω; de B a tierra hay R3 = {R3} Ω. ¿Cuál es el voltaje del nodo A?"
    parametros:
      Is: { min: 1, max: 5, paso: 0.5 }
      R1: { min: 2, max: 20, paso: 2 }
      R2: { min: 1, max: 10, paso: 1 }
      R3: { min: 1, max: 10, paso: 1 }
    solucion: "Is * R1 * (R2 + R3) / (R1 + R2 + R3)"
    unidad: V
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "Nodo B: (VA − VB) / R2 = VB / R3. Nodo A: Is = VA / R1 + (VA − VB) / R2. Al resolver el sistema, la fuente ve a R1 en paralelo con (R2 + R3), así que VA = Is · R1 · (R2 + R3) / (R1 + R2 + R3)."
    pistas:
      - "Hay dos nodos desconocidos: plantea LCK en A y en B."
      - "Del nodo B despeja VB en función de VA y sustitúyelo en la ecuación de A."

  - id: kir-02-mallas
    tipo: numeric
    enunciado: "Un circuito tiene dos mallas lado a lado. La malla 1 tiene una fuente de {V} V y R1 = {R1} Ω. Las dos mallas comparten R2 = {R2} Ω. La malla 2 solo tiene R3 = {R3} Ω. ¿Qué corriente pasa por R2?"
    parametros:
      V: { min: 5, max: 24, paso: 1 }
      R1: { min: 1, max: 10, paso: 1 }
      R2: { min: 1, max: 10, paso: 1 }
      R3: { min: 1, max: 10, paso: 1 }
    solucion: "V * R3 / (R1 * (R2 + R3) + R2 * R3)"
    unidad: A
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "Con I1 e I2 en sentido horario: malla 1, V = R1 · I1 + R2 · (I1 − I2); malla 2, 0 = R2 · (I2 − I1) + R3 · I2. Al resolver, la corriente en R2 es I1 − I2 = V · R3 / (R1 · (R2 + R3) + R2 · R3)."
    pistas:
      - "Asigna una corriente de malla I1 e I2, las dos en sentido horario, y plantea LVK en cada malla."
      - "Por R2 pasan las dos corrientes de malla en sentidos opuestos, así que su corriente es I1 − I2."

  - id: kir-02-numero-ecuaciones
    tipo: multiple_choice
    enunciado: "Un circuito tiene 4 nodos. ¿Cuántas ecuaciones de nodo se necesitan para resolverlo?"
    opciones:
      - "2"
      - "3"
      - "4"
      - "5"
    correcta: 1
    explicacion: "Se elige un nodo como referencia (0 V). Quedan 4 − 1 = 3 voltajes desconocidos, así que se necesitan 3 ecuaciones."
    pistas:
      - "No todos los nodos tienen un voltaje desconocido."
      - "Uno de los nodos se usa como referencia y vale 0 V."

  - id: kir-02-ley-nodos
    tipo: fill_pattern
    enunciado: "En el análisis de nodos se aplica la Ley de ___ de Kirchhoff en cada nodo."
    respuestas_aceptadas: ["corrientes", "corriente"]
    explicacion: "En el análisis de nodos se escribe LCK (Ley de Corrientes) en cada nodo; en el de mallas se escribe LVK (Ley de Voltajes) en cada malla."
    pistas:
      - "En un nodo se juntan varias ramas: ¿qué magnitud entra y sale por ellas?"
      - "Es la ley que dice que lo que entra a un nodo tiene que salir."
---

El **análisis de nodos** y el **análisis de mallas** son métodos ordenados para resolver circuitos que no se reducen solo con serie y paralelo. En los dos se obtiene un sistema de ecuaciones.

En el análisis de nodos se elige un **nodo de referencia** (tierra, 0 V) y se nombran los voltajes de los demás nodos. En cada uno se aplica LCK escribiendo la corriente de cada resistor como (V_nodo − V_vecino) / R. Con n nodos se necesitan n − 1 ecuaciones.

Por ejemplo, si una fuente de 10 V alimenta el nodo V1 a través de 2 Ω, y desde V1 bajan a tierra dos resistores de 4 Ω: (V1 − 10) / 2 + V1 / 4 + V1 / 4 = 0, de donde V1 = 5 V.

En el análisis de mallas se asigna una **corriente de malla** a cada ventana del circuito, normalmente en sentido horario, y se aplica LVK en cada una. Un resistor compartido por dos mallas lleva la diferencia de las dos corrientes de malla.

Se elige el método que dé menos ecuaciones: nodos si hay pocos nodos o fuentes de corriente; mallas si hay pocas mallas o fuentes de voltaje.
