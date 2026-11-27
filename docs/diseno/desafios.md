# Diseño: desafíos diarios y mensual

Decisiones de la fase 2. El backend genera y avanza los desafíos (CLAUDE.md 5.4). Las cifras viven en `app/core/config.py`.

## 1. Qué hay cada periodo

- **Diarios:** cada día local del alumno se eligen `DAILY_CHALLENGE_COUNT` (3) metas al azar de la lista diaria. Son siempre las mismas para el mismo alumno y el mismo día (semilla = alumno + fecha).
- **Mensual:** todas las metas de la lista mensual, cada mes.
- El "día" y el "mes" son los de la **zona horaria del alumno**, igual que la racha.
- No hay tareas programadas: los desafíos del periodo se crean la primera vez que se leen (`GET /challenges`) o que el alumno gana EXP.

| Lista | Meta (`kind`) | Objetivo | Premio |
|---|---|---|---|
| Diaria | `earn_xp`: gana EXP | 50 | 10 EXP |
| Diaria | `complete_lessons`: termina lecciones | 2 | 10 EXP |
| Diaria | `first_try_correct`: acierta al primer intento | 12 | 10 EXP |
| Diaria | `perfect_lessons`: lecciones sin errores | 1 | 15 EXP |
| Diaria | `open_chests`: abre cofres | 2 | 5 EXP |
| Mensual | `earn_xp`: gana EXP | 1500 | 100 EXP |

Las listas se cambian con `DAILY_CHALLENGES` y `MONTHLY_CHALLENGES` (JSON), sin tocar el código.

## 2. Cómo avanzan

| Evento | Avanza |
|---|---|
| Terminar un intento | `earn_xp` (EXP de la lección), `first_try_correct`; si es una lección: `complete_lessons` y, con 100 %, `perfect_lessons` |
| Abrir un cofre | `earn_xp` (EXP del cofre), `open_chests` |

- Al llegar a la meta, el desafío queda cumplido y entrega su EXP una sola vez (evento `source = "challenge"`).
- La EXP de un desafío **no cuenta** para otros desafíos de "gana EXP", para que uno no complete a otro. Sí cuenta para la EXP total y los logros.
- Los repasos y las evaluaciones cuentan para EXP y aciertos, pero no como "lección".

## 3. API

`GET /challenges` (`getChallenges`) devuelve `daily`, `monthly` y cuándo termina cada periodo (`daily_ends_at`, `monthly_ends_at`, a medianoche local). Los textos de cada meta están en la app (`challenges.kind.<kind>`).
