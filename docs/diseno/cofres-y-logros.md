# Diseño: cofres, logros y medallas

Decisiones de la fase 2. El backend decide los premios y las medallas (CLAUDE.md 5.4). Las cifras viven en `app/core/config.py`.

## 1. Cofres

Hay dos clases de cofre:

| Cofre | Cuándo sale | Premio | Variables |
|---|---|---|---|
| **De lección** | Al terminar cualquier intento (lección, repaso o evaluación) | 2 a 10 EXP al azar + 1 de energía | `CHEST_LESSON_XP_MIN`, `CHEST_LESSON_XP_MAX`, `CHEST_LESSON_ENERGY` |
| **Del camino** | El nodo cofre de cada unidad, una vez por alumno | 15 a 30 EXP al azar + 5 de energía | `CHEST_NODE_XP_MIN`, `CHEST_NODE_XP_MAX`, `CHEST_NODE_ENERGY` |

- El premio **se sortea al abrir** y queda guardado. Abrirlo de nuevo devuelve el mismo premio y no da más.
- La EXP del cofre se guarda como evento `source = "chest"`, para las ligas y los desafíos. No cuenta en la "EXP ganada" del resumen de la lección.
- El nodo cofre ahora es **obligatorio**: abrirlo lo completa y desbloquea la evaluación.

### Flujo al terminar (CLAUDE.md 1.2)

Resumen → **Cofre** ("Pulsa para abrir") → **Racha** → Inicio.

El resumen trae `chest_id`. La pantalla del cofre lo abre con `POST /chests/{id}/open`. La de racha usa el mismo resumen (`streak`, `streak_extended`). El nodo cofre del camino se abre con `POST /nodes/{key}/chest`.

## 2. Logros y medallas

- Un **logro** tiene niveles: una métrica y sus umbrales. Cada nivel alcanzado da una **medalla** (Bronce, Plata, Oro), que se entrega una sola vez.
- Los logros se revisan al terminar un intento y al abrir un cofre. Las medallas ganadas al terminar se guardan con su intento y el resumen las celebra.

| Logro (`id`) | Métrica | Umbrales |
|---|---|---|
| `lessons` | Lecciones completadas (distintas) | 1, 5, 10 |
| `streak` | Racha más larga | 3, 7, 30 |
| `xp` | EXP total | 100, 500, 1500 |
| `perfect` | Lecciones con 100 % de precisión (cada intento cuenta) | 1, 5, 15 |
| `units` | Evaluaciones de unidad completadas | 1, 3, 5 |
| `chests` | Cofres abiertos | 1, 10, 25 |

- La lista vive en `Settings.achievements` y se puede cambiar con `ACHIEVEMENTS` (JSON) sin tocar el código.
- Los **nombres** viven en la app (`achievements.items.<id>`). Si el backend agrega un logro que la app no conoce, la app lo muestra con un nombre genérico.
- Si se quita un logro de la configuración, sus medallas dejan de mostrarse, pero no se borran.

## 3. API

| Ruta | Para qué |
|---|---|
| `POST /chests/{chest_id}/open` (`openChest`) | Abrir el cofre de un intento |
| `POST /nodes/{node_key}/chest` (`openNodeChest`) | Abrir el nodo cofre del camino (`409 not_a_chest` si no es cofre) |
| `GET /me/achievements` (`getAchievements`) | Logros con su progreso y medallas ganadas |
