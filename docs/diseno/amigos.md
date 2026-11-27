# Diseño: amigos y seguidores

Decisiones de la fase 3.

## 1. Reglas

- **Seguir** es en un solo sentido, sin pedir permiso. Dos alumnos que se siguen entre sí son **amigos**.
- Solo se pueden **encontrar y seguir perfiles públicos** (Configuración → Privacidad). Un perfil privado no aparece en la búsqueda y seguirlo responde `404`.
- Si alguien con perfil privado te sigue, aparece en tus seguidores como "Alumno anónimo" y no lo puedes seguir de vuelta.
- Nadie se puede seguir a sí mismo (`409 cannot_follow_self`). Seguir dos veces no duplica nada.
- De cada alumno se ve: nombre (si es público), EXP total, racha y liga. Nada más: ni correo ni progreso detallado.

## 2. Búsqueda

Por nombre, sin distinguir mayúsculas, con **al menos 2 letras** y hasta 20 resultados ordenados por EXP. Los caracteres `%` y `_` se buscan tal cual, no como comodines.

## 3. API

| Ruta | Para qué |
|---|---|
| `GET /friends` (`getFriends`) | A quiénes sigo y quiénes me siguen |
| `GET /users/search?q=` (`searchUsers`) | Buscar perfiles públicos |
| `POST /users/{id}/follow` (`followUser`) | Seguir |
| `DELETE /users/{id}/follow` (`unfollowUser`) | Dejar de seguir |

La tabla `follows` guarda `(follower_id, followee_id)`. La pantalla **Amigos** se abre desde Más.
