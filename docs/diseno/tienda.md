# Diseño: monedas, tienda y protector de racha

Decisiones de la fase 3. El backend decide precios, compras y premios (CLAUDE.md 5.4). Las cifras viven en `app/core/config.py`.

## 1. Monedas

La tienda cobra en **monedas**, no en EXP: la EXP decide las ligas y gastarla las desordenaría.

| De dónde salen | Cuántas | Variable |
|---|---|---|
| Cofre de lección | 5 a 15 al azar | `CHEST_LESSON_COINS_MIN`, `CHEST_LESSON_COINS_MAX` |
| Cofre del camino | 50 | `CHEST_NODE_COINS` |
| Cada desafío cumplido | 10 | `CHALLENGE_REWARD_COINS` |

## 2. Artículos

| Artículo (`id`) | Precio | Qué hace | Cuándo no se puede comprar |
|---|---|---|---|
| `energy_refill` | 60 | Llena la energía al instante | Con la energía llena (`energy_already_full`) |
| `streak_freeze` | 150 | Se guarda; cubre un día sin práctica | Con `STREAK_FREEZE_MAX` (2) guardados (`streak_freeze_limit`) |

- Sin monedas suficientes: `409 not_enough_coins`. La tienda dice de antemano por qué un artículo no se puede comprar (`unavailable_reason`).
- Cada compra se guarda en `purchases` (historial).
- Los precios se cambian con `SHOP_ENERGY_REFILL_PRICE` y `SHOP_STREAK_FREEZE_PRICE`. Los nombres de los artículos viven en la app (`shop.items.<id>`).

## 3. Protector de racha

- Se usa **solo**, sin que el alumno haga nada. Si faltaron días entre la última lección y hoy, y los protectores guardados alcanzan para **todos** esos días, se gastan (uno por día) y la racha sigue.
- Si no alcanzan, no se gasta ninguno y la racha se rompe como siempre.
- La racha que se muestra (`/me`) ya considera los protectores: no se ve rota si alcanzan.
- Se gastan al terminar la siguiente lección. Cada día cubierto se guarda en `streak_freeze_uses`.

## 4. API

`GET /shop` (`getShop`) y `POST /shop/items/{item_id}/buy` (`buyShopItem`). `/me` trae `coins` y `streak_freezes`, y el premio del cofre trae `coins`.
