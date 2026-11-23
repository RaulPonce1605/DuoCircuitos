# Formato del temario

Todo el contenido de la app sale de esta carpeta. Hay dos tipos de archivo:

1. **`camino.yaml`**: el orden del camino (etapas → secciones → unidades → nodos).
2. **Lecciones**: un Markdown por lección en `unidades/<unidad>/<id>.md`, con frontmatter YAML (los datos y ejercicios) y un cuerpo en Markdown (la teoría).

Las claves están en español porque las escribe el equipo de contenido; el importador del backend (`backend/app/content_import/`) las traduce a los modelos en inglés.

---

## 1. `camino.yaml`

```yaml
etapas:
  - id: e1-fundamentos
    titulo: Fundamentos
    secciones:
      - id: s1-magnitudes
        titulo: Magnitudes eléctricas
        unidades:
          - id: u01-ley-de-ohm
            titulo: Ley de Ohm
            nodos:
              - { tipo: leccion, leccion: ohm-01 }
              - { tipo: leccion, leccion: ohm-02 }
              - { tipo: repaso }
              - { tipo: cofre }
              - { tipo: evaluacion }
```

| Campo | Obligatorio | Descripción |
|---|---|---|
| `id` | sí | Minúsculas, números y guiones. No se cambia una vez publicado. |
| `titulo` | sí | Texto visible en la app. |
| `nodos[].tipo` | sí | `leccion`, `repaso`, `cofre` o `evaluacion`. |
| `nodos[].leccion` | solo en `leccion` | `id` de la lección. |

- El orden de las listas **es** el orden de desbloqueo.
- `repaso` y `evaluacion` toman ejercicios de las lecciones de su unidad.

---

## 2. Lección

### 2.1 Frontmatter

| Campo | Obligatorio | Descripción |
|---|---|---|
| `id` | sí | Igual al nombre del archivo sin `.md`. |
| `unidad` | sí | `id` de la unidad en `camino.yaml`. |
| `titulo` | sí | Texto visible. |
| `objetivos` | sí | Lista: qué podrá hacer el estudiante al terminar. |
| `conceptos` | sí | Lista de conceptos; aparecen en el resumen final. |
| `ejercicios` | sí | Lista de ejercicios (ver 2.2). |

### 2.2 Campos de un ejercicio

Comunes a todos los tipos:

| Campo | Obligatorio | Descripción |
|---|---|---|
| `id` | sí | Único dentro de la lección. |
| `tipo` | sí | `multiple_choice`, `fill_pattern`, `numeric` (`circuit_diagram`, para después). |
| `enunciado` | sí | Texto de la pregunta. En `numeric` usa `{param}` para insertar valores. |
| `explicacion` | sí | Se muestra después de Comprobar. |
| `pistas` | sí | Mínimo 2, de general a concreta. Nunca contienen la respuesta. |

Por tipo:

| Tipo | Campos extra |
|---|---|
| `multiple_choice` | `opciones` (lista), `correcta` (índice desde 0) |
| `fill_pattern` | `respuestas_aceptadas` (lista; se comparan sin distinguir mayúsculas ni espacios) |
| `numeric` | `parametros`, `solucion`, `unidad`, `tolerancia` |

Detalle de `numeric`:

- **`parametros`**: cada variable con `min`, `max` y `paso`. El backend sortea un valor múltiplo de `paso` dentro del rango.
- **`solucion`**: fórmula con los nombres de los parámetros. Permitido: `+ - * / ^ ( )`, `sqrt`, `abs`, `sin`, `cos`, `tan`, `atan`, `log10`, `ln`, `exp`, `pi`. Nada más. Se permiten números con notación científica (`1.72e-8`).
- **`unidad`**: unidad SI base del resultado (`A`, `V`, `Ω`, `W`...). El estudiante puede responder con prefijo SI (`mA`, `kΩ`) y el backend lo convierte.
- **`tolerancia`**: `{ tipo: relativa, valor: 0.02 }` (±2 %) o `{ tipo: absoluta, valor: 0.01 }` (± en la unidad base).

### 2.3 Cuerpo

Debajo del frontmatter va la **teoría** de la lección en Markdown. Es lo que el tutor usa como fuente y lo que puede mostrarse como introducción. Debe cubrir todos los `conceptos`.

---

## 3. Ejemplo: Ley de Ohm

Archivo `unidades/u01-ley-de-ohm/ohm-01.md`:

```markdown
---
id: ohm-01
unidad: u01-ley-de-ohm
titulo: Voltaje, corriente y resistencia
objetivos:
  - Relacionar voltaje, corriente y resistencia con la Ley de Ohm.
  - Calcular la corriente en un circuito con una sola resistencia.
conceptos:
  - Ley de Ohm
  - Proporcionalidad inversa entre corriente y resistencia
ejercicios:
  - id: ohm-01-mc
    tipo: multiple_choice
    enunciado: "Si el voltaje se mantiene y la resistencia se duplica, la corriente…"
    opciones:
      - "Se duplica"
      - "Se reduce a la mitad"
      - "No cambia"
      - "Se cuadruplica"
    correcta: 1
    explicacion: "Con V constante, I = V / R: si R se duplica, I se reduce a la mitad."
    pistas:
      - "¿Qué ecuación relaciona las tres magnitudes?"
      - "Escribe I en función de V y R y observa qué pasa si R crece."

  - id: ohm-01-fill
    tipo: fill_pattern
    enunciado: "V = I · ___"
    respuestas_aceptadas: ["R"]
    explicacion: "La Ley de Ohm es V = I · R."
    pistas:
      - "Falta la magnitud que se opone al paso de la corriente."
      - "Se mide en ohms (Ω)."

  - id: ohm-01-calc
    tipo: numeric
    enunciado: "Una resistencia de {R} Ω está conectada a una fuente de {V} V. ¿Qué corriente circula?"
    parametros:
      V: { min: 5, max: 24, paso: 1 }
      R: { min: 100, max: 1000, paso: 50 }
    solucion: "V / R"
    unidad: A
    tolerancia: { tipo: relativa, valor: 0.02 }
    explicacion: "Despejando de V = I · R se obtiene I = V / R. Divide el voltaje entre la resistencia."
    pistas:
      - "¿Qué magnitud te piden y cuáles conoces?"
      - "Despeja I de V = I · R."
      - "Cuida las unidades: V entre Ω da A. Puedes responder en mA."
---

La **Ley de Ohm** relaciona tres magnitudes de un circuito: el voltaje (V), la corriente (I) y la resistencia (R).

V = I · R

Si el voltaje se mantiene constante, la corriente y la resistencia son **inversamente proporcionales**: cuanto mayor es la resistencia, menor es la corriente.
```
