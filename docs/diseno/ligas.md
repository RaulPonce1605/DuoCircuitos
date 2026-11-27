# Diseño: ligas semanales

Decisiones de la fase 3. El backend arma, ordena y cierra las ligas (CLAUDE.md 5.4). Las cifras viven en `app/core/config.py`.

## 1. Niveles

Cinco niveles con nombres de componentes de circuitos, de menor a mayor. Los nombres de la app son propios, no los de las apps de referencia.

| Índice | `tier_id` | Nombre |
|---|---|---|
| 0 | `resistor` | Resistor |
| 1 | `capacitor` | Capacitor |
| 2 | `inductor` | Inductor |
| 3 | `transistor` | Transistor |
| 4 | `superconductor` | Superconductor |

La lista se cambia con `LEAGUE_TIERS` (JSON). Si el backend manda un nivel que la app no conoce, la app lo muestra como "Nivel N".

## 2. La semana

- La semana va de **lunes 00:00 a lunes 00:00 UTC** y es la misma para todos, así todos los de un grupo compiten en el mismo periodo.
- Un alumno **entra** a la liga de la semana la primera vez que gana EXP en ella, al terminar un intento o al abrir un cofre.
- Se le asigna el primer grupo de su nivel que tenga lugar (`LEAGUE_GROUP_SIZE`, 20). Si no hay ninguno, se crea uno. Un candado de Postgres por semana y nivel evita que dos alumnos llenen de más el mismo grupo.
- La EXP de la semana **no se guarda aparte**: se suma de `xp_events`. Así cuenta toda la EXP (lecciones, cofres, desafíos) y no se puede desincronizar.
- Ranking: más EXP primero. En un empate, gana quien entró antes.

## 3. Cierre automático

No hay tareas programadas. La primera vez que un miembro del grupo vuelve (al ganar EXP o al abrir Ligas) después de que terminó la semana, el grupo se cierra:

| Lugar | Resultado | Variable |
|---|---|---|
| Los primeros 5 (con al menos 1 EXP) | Suben un nivel (no del último) | `LEAGUE_PROMOTE_COUNT` |
| Los últimos 5 | Bajan un nivel (no del primero) | `LEAGUE_DEMOTE_COUNT` |
| El resto | Se quedan | |

- En un grupo chico las zonas no se enciman: primero se reparten los lugares para subir.
- El nivel nuevo se calcula desde el nivel del grupo, así que cerrar dos veces da lo mismo.
- El resultado se guarda (`final_rank`, `final_xp`, `result`) y la pantalla lo anuncia **una sola vez**.

## 4. Privacidad

Con el perfil privado (`profile_public = false`, en Configuración), los demás ven a ese alumno como "Alumno anónimo", pero sigue compitiendo. Su propio nombre sí lo ve.

## 5. API

`GET /leagues/current` (`getCurrentLeague`) devuelve el nivel, cuándo termina la semana, si ya entró, el ranking con la zona de cada lugar (`promotion`, `demotion` o null) y el último resultado sin ver. `/me` trae `league_tier` y `league_tier_id` para el Perfil.
