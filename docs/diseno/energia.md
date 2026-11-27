# Diseño: energía

Decisiones de la fase 2. El backend es la fuente de verdad (CLAUDE.md 5.4) y las cifras viven en `app/core/config.py`.

## 1. Reglas

| Concepto | Valor por defecto | Variable |
|---|---|---|
| Energía máxima | 5 | `ENERGY_MAX` |
| Gasto por respuesta incorrecta | 1 | `ENERGY_COST_PER_MISTAKE` |
| Minutos para recargar una unidad | 30 | `ENERGY_REFILL_MINUTES` |

- Una respuesta **correcta no gasta**. Solo los fallos cuestan.
- **Sin energía** (0) no se puede empezar una lección ni responder un ejercicio: el backend responde `409 not_enough_energy`. La lección queda a medias y se puede retomar cuando haya energía.
- Se recarga **una unidad cada periodo**, hasta el máximo. El periodo empieza a contar en el primer gasto con la energía llena. Gastar a la mitad de un periodo no reinicia el reloj de la unidad que ya venía.
- Los cofres pueden devolver energía (ver `docs/diseno/cofres-y-logros.md`).

## 2. Cómo se guarda

- `users.energy_used` guarda la energía **gastada** que aún no se recarga (0 = llena), no la que queda. Si baja `ENERGY_MAX`, nadie se queda con más energía que el máximo.
- `users.energy_updated_at` guarda desde cuándo corre la recarga de la siguiente unidad.
- No hay tareas programadas: la recarga se calcula al leer (`/me`, iniciar lección, Comprobar), igual que la racha.

## 3. Lo que ve la app

`energy: { current, max, next_refill_at }` viene en `/me`, al iniciar una lección y en cada Comprobar. La app muestra el contador en Inicio y en la lección, y dice en cuántos minutos llega la siguiente unidad.
