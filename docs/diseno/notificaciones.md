# Diseño: notificaciones

Decisiones de la fase 3.

## 1. Avisos locales, sin servidor de push

Los avisos los programa la app en el teléfono con `expo-notifications`. No hace falta un servidor de push, ni tokens de dispositivo, ni guardar nada nuevo en el backend, y funcionan sin conexión. En la web no hay avisos y la pantalla de Configuración lo dice.

| Aviso | Cuándo | Interruptor en Configuración |
|---|---|---|
| **Recordatorio de racha** | A las **19:00** (hora local del teléfono), solo si ese día aún no terminó una lección. Si ya practicó, se mueve al día siguiente. Dice cuántos días lleva de racha. | `notify_streak_reminder` |
| **Desafíos nuevos** | Todos los días a las **9:00** | `notify_challenges` |

Las horas están en `app/src/services/reminders.ts` (`STREAK_REMINDER_HOUR`, `CHALLENGES_REMINDER_HOUR`). No son cifras de gamificación: solo dicen cuándo avisar.

## 2. Cómo se mantienen al día

- `RemindersManager`, montado en las pestañas, vuelve a programar los avisos cada vez que cambia el usuario: al terminar una lección (`/me` trae `practiced_today`) o al cambiar un interruptor.
- Cada programación **reemplaza** todo lo anterior, y las programaciones van en fila para que dos cambios seguidos no se mezclen.
- El permiso del sistema se pide la primera vez que hay algún aviso encendido. Si el alumno lo niega, Configuración le dice cómo activarlo en los ajustes del teléfono.
- Al cerrar sesión se borran los avisos programados.

## 3. Backend

Solo cambia `/me`, que ahora trae `practiced_today`: si ya terminó una lección hoy, en su día local.
