# Diseño: perfil y configuración

Decisiones de la fase 2.

## 1. Perfil (pestaña)

- **Resumen:** racha actual, mejor racha, EXP total y liga. Las ligas llegan en la fase 3: mientras tanto se muestra "Sin liga aún".
- **Logros:** cuántos niveles se han alcanzado de cuántos hay, con un acceso a la pantalla de Logros.
- **Medallas recientes:** las 3 últimas, con un acceso a la pantalla de Medallas.
- El engrane abre **Configuración** (CLAUDE.md 1.6). También se abre desde Más.
- Todo sale de `/me` y `/me/achievements`.

## 2. Configuración

| Sección | Qué se cambia | Campo |
|---|---|---|
| Preferencias | Nombre visible | `display_name` |
| Preferencias | Zona horaria: un botón ofrece la del dispositivo si es distinta | `timezone` |
| Notificaciones | Recordatorio de racha | `notify_streak_reminder` |
| Notificaciones | Avisos de desafíos | `notify_challenges` |
| Privacidad | Perfil público: otros alumnos ven tu nombre y tu EXP en las ligas | `profile_public` |
| Cuenta | Cerrar sesión | — |

- `PATCH /me` (`updateCurrentUser`) cambia **solo lo que se manda**. El nombre y la zona horaria se validan igual que al registrarse. El correo y la contraseña no se cambian aquí.
- Las preferencias de notificaciones **se guardan desde ahora**, pero los avisos se envían en la fase 3 (tarea de notificaciones). La pantalla lo dice.
- `profile_public` lo usarán las ligas y los amigos de la fase 3.
- Cambiar la zona horaria cambia el "día" de la racha y de los desafíos (ver `exp-y-racha.md`).
