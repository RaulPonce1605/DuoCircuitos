# Diseño: nodos de repaso y evaluación

Decisiones de la fase 2. Las cifras viven en `app/core/config.py`.

## 1. Cómo se juegan

Se juegan igual que una lección: ejercicios uno por uno, Comprobar, los fallos vuelven al final de la cola, gastan energía y al terminar dan EXP con las reglas de `exp-y-racha.md`. Lo único distinto es **de dónde salen los ejercicios**:

| Nodo | Ejercicios | Variable |
|---|---|---|
| Repaso | Los 6 de la unidad que **más le han costado** al alumno (más respuestas incorrectas en todos sus intentos). Los empates se deciden al azar y el orden se baraja. | `REVIEW_EXERCISE_COUNT` |
| Evaluación | 8 ejercicios **al azar** de todas las lecciones de la unidad. | `ASSESSMENT_EXERCISE_COUNT` |

Si la unidad tiene menos ejercicios que la cifra, se usan todos. Los numéricos salen con valores nuevos cada vez.

## 2. En el camino

- Lección, repaso y evaluación son **obligatorios**: el siguiente nodo se desbloquea al completarlos.
- El cofre todavía no frena el avance (se abre en `cofres-y-logros.md`).
- El "siguiente paso" (`is_current`) es el primer nodo obligatorio disponible.

## 3. API

- `POST /nodes/{node_key}/attempts` (`startNode`) inicia cualquier nodo jugable. La clave de un nodo de lección es el slug de la lección (`ohm-01`); la de los demás es `unidad:tipo:n` (`u01-ley-de-ohm:review:1`). Un cofre responde `409 node_not_playable`.
- `POST /lessons/{lesson_slug}/attempts` sigue funcionando para las lecciones.
- El intento y el resumen traen `node` (`key`, `type`, `unit_title`) y `lesson` (null en repaso y evaluación). La app arma el título con i18n ("Repaso: Ley de Ohm").
- Los conceptos del resumen de un repaso o evaluación son los de las lecciones de donde salieron sus ejercicios.
