---
id: ohm-02
unidad: u01-ley-de-ohm
titulo: Ley de Ohm y potencia
objetivos:
  - Aplicar la Ley de Ohm para calcular corriente, voltaje o resistencia.
  - Calcular la potencia que disipa un elemento con cualquiera de sus tres fórmulas.
  - Predecir cómo cambia la potencia cuando cambia el voltaje.
conceptos:
  - Ley de Ohm
  - Potencia eléctrica
  - Fórmulas de potencia
ejercicios:
  - id: ohm-02-corriente
    tipo: numeric
    enunciado: "Un resistor de {R} Ω se conecta a una fuente de {V} V. ¿Qué corriente circula?"
    parametros:
      V: { min: 3, max: 24, paso: 1 }
      R: { min: 100, max: 2200, paso: 100 }
    solucion: "V / R"
    unidad: A
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "De la Ley de Ohm, V = I · R, se despeja I = V / R: se divide el voltaje entre la resistencia. El resultado suele quedar en miliamperes (1 mA = 0.001 A)."
    pistas:
      - "¿Qué ley relaciona voltaje, corriente y resistencia?"
      - "Despeja la corriente de V = I · R."

  - id: ohm-02-resistencia-foco
    tipo: numeric
    enunciado: "Un foco consume {P} W cuando se conecta a {V} V. ¿Cuál es su resistencia en operación?"
    parametros:
      P: { min: 20, max: 100, paso: 5 }
      V: { min: 100, max: 130, paso: 10 }
    solucion: "V^2 / P"
    unidad: Ω
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "La forma de la potencia que no usa la corriente es P = V² / R. Despejando, R = V² / P: se eleva el voltaje al cuadrado y se divide entre la potencia."
    pistas:
      - "Conoces la potencia y el voltaje, pero no la corriente."
      - "Usa la fórmula de potencia que relaciona P, V y R, y despeja R."

  - id: ohm-02-potencia-doble-voltaje
    tipo: multiple_choice
    enunciado: "Si el voltaje sobre un resistor fijo se duplica, ¿qué pasa con la potencia que disipa?"
    opciones:
      - "Se queda igual"
      - "Se duplica"
      - "Se cuadruplica"
      - "Se reduce a la mitad"
    correcta: 2
    explicacion: "Con P = V² / R y R fija: con el doble de voltaje, P' = (2V)² / R = 4 · V² / R = 4P. La potencia se multiplica por 4."
    pistas:
      - "Escribe la potencia en función del voltaje y la resistencia."
      - "En P = V² / R, el voltaje está elevado al cuadrado."

  - id: ohm-02-potencia-corriente
    tipo: numeric
    enunciado: "Por un resistor de {R} kΩ circula una corriente de {I} mA. ¿Qué potencia disipa?"
    parametros:
      R: { min: 1, max: 10, paso: 1 }
      I: { min: 1, max: 20, paso: 1 }
    solucion: "(I / 1000)^2 * (R * 1000)"
    unidad: W
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "Se convierten los datos a unidades base (mA → A dividiendo entre 1000, kΩ → Ω multiplicando por 1000) y se usa P = I² · R."
    pistas:
      - "Antes de calcular, pasa la corriente a amperes y la resistencia a ohms."
      - "Conoces la corriente y la resistencia: usa la forma de la potencia que solo tiene I y R."

  - id: ohm-02-potencia-formula
    tipo: fill_pattern
    enunciado: "La potencia eléctrica es el voltaje por la corriente: P = V · ___"
    respuestas_aceptadas: ["I"]
    explicacion: "La potencia es P = V · I: voltaje en volts por corriente en amperes da watts."
    pistas:
      - "Volts por esta magnitud dan watts."
      - "Es la magnitud que se mide en amperes."
---

La **Ley de Ohm** dice que la corriente en un resistor es proporcional al voltaje aplicado: V = I · R. Si el voltaje sube, la corriente sube en la misma proporción; si la resistencia sube con el mismo voltaje, la corriente baja.

De esa ecuación se despeja la magnitud que falte: I = V / R o R = V / I. Por ejemplo, un resistor de 4 Ω conectado a 12 V deja pasar I = 12 V / 4 Ω = 3 A.

La **potencia** (P) es la rapidez con que un elemento convierte energía eléctrica en calor, luz o movimiento. Se mide en **watts** (W) y vale P = V · I. En el ejemplo anterior, P = 12 V · 3 A = 36 W.

Combinando la potencia con la Ley de Ohm se obtienen tres **fórmulas de potencia** equivalentes: P = V · I = I² · R = V² / R. Se elige la que use los datos que se conocen: si no se conoce la corriente, P = V² / R; si no se conoce el voltaje, P = I² · R.

Como el voltaje aparece al cuadrado en P = V² / R, con una resistencia fija la potencia cambia con el cuadrado del voltaje: con el triple de voltaje, la potencia se multiplica por nueve.
