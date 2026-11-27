# Diseño: tutor con IA ("Pedir ayuda")

Decisiones de la fase 2. Las reglas están en `backend/CLAUDE.md` 3.9; aquí está el porqué de cada pieza.

## 1. Cómo responde

1. El alumno pulsa **Pedir ayuda** durante un ejercicio. Puede escribir una duda o no escribir nada.
2. El backend arma el prompt **solo con el temario**: teoría y conceptos de la lección, el enunciado con sus valores, la unidad y las pistas del temario **hasta el nivel de ayuda actual**. La primera vez, solo la primera pista; cada petición desbloquea la siguiente.
3. El proveedor configurado responde (`LLM_PROVIDER`, `LLM_MODEL`).
4. El **filtro de salida** busca la solución en la respuesta. Si la encuentra, si la respuesta viene vacía o es demasiado larga, o si el proveedor falla, se descarta y el alumno recibe la **siguiente pista del temario**. La app la marca como "Pista del temario".

Sin proveedor configurado (`LLM_PROVIDER=` vacío), el tutor da las pistas del temario en orden. No gasta nada, y así funciona en local y en el CI.

## 2. Qué nunca llega al modelo

- El resultado, la opción correcta, las respuestas aceptadas y la explicación.
- **Las opciones de opción múltiple**, porque una de ellas es la respuesta. El tutor ayuda con el concepto.
- Si la teoría contiene por casualidad la solución de esta instancia (un ejemplo con los mismos números, o la palabra que completa el patrón), **se tacha** con `[…]` antes de mandarla.

## 3. Cómo detecta la solución el filtro

Cada validador implementa `solution_spans`, así que agregar un tipo nuevo no toca el filtro:

| Tipo | Detecta |
|---|---|
| `numeric` | Cualquier número cuyo valor, en la unidad base, quede dentro de la tolerancia del resultado: `0.024 A`, `24 mA`, `2.4e-2`, `24 × 10⁻³ A`. Los números sin unidad se prueban con todos los prefijos SI. Los que llevan la unidad de otra magnitud (`12 V` cuando se pide una corriente) no cuentan. |
| `multiple_choice` | El texto de la opción correcta, o su letra o número en el orden en que se mostró ("la B", "opción 2", "inciso b"). |
| `fill_pattern` | Una respuesta aceptada de 3 letras o más como palabra completa, o el patrón ya completado (`G = 1 / R`, `63 %`). |

El filtro prefiere bloquear de más: una pista del temario de más no hace daño; una respuesta regalada sí.

## 4. Límites

| Límite | Por defecto | Variable |
|---|---|---|
| Peticiones por alumno por hora | 30 | `TUTOR_REQUESTS_PER_HOUR` |
| Peticiones por ejercicio mostrado | 6 | `TUTOR_REQUESTS_PER_EXERCISE` |

Cada respuesta del tutor se guarda en `tutor_messages`; los límites cuentan esas filas. Al pasarse, el backend responde `429` con `tutor_rate_limited` o `tutor_exercise_limit`. Un reintento de un ejercicio fallado es una instancia nueva, con su propio límite.

## 5. Proveedores

- `anthropic`: Claude, con el SDK oficial, en `services/tutor/anthropic_provider.py`. Esfuerzo `LLM_EFFORT=low` (las pistas son cortas). Con `LLM_SERVER_FALLBACKS=true`, si el modelo rechaza una petición, la API la repite con otro modelo.
- Para agregar otro proveedor: un adaptador que implemente `TutorProvider` y su valor en `LLM_PROVIDER` (ver el checklist de `backend/CLAUDE.md`).

## 6. Pruebas

- `tests/tutor/test_prompt.py`: prueba obligatoria 1. Recorre los 50 ejercicios con 12 semillas.
- `tests/tutor/test_guard.py`: prueba obligatoria 2.
- `tests/conftest.py` → `_no_real_llm`: prueba obligatoria 3. Cualquier prueba que llame al adaptador real falla.
- `tests/tutor/preguntas_alumnos.yaml`: preguntas típicas de alumnos, incluidas las que intentan sacar la respuesta. Se prueban con un ejercicio de cada tipo.
