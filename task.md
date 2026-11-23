# Plan de tareas — Proyecto final de circuitos

Fuente: [Plan de tareas en Claude Docs](https://claude.ai/artifact/LBa2i9T76Tt9bndQYTStch) (2026-11-15)

## Resumen

Las fases van en orden: primero que una lección funcione de punta a punta, después todo lo demás. Sin fechas: mientras antes terminemos, mejor. Somos 4, cada quien dueño de un módulo, y todos trabajamos con Claude Code siguiendo los CLAUDE.md del repo.

| Inicial | Persona | Dueño de |
| --- | --- | --- |
| R | Rico | Todo el backend y la IA: auth, modelos, validación de ejercicios, gamificación del lado del servidor, tutor y sus pruebas |
| Alex | Alex | App: navegación, camino, pantalla de lección, componentes de ejercicio, perfil |
| D | Danna | La carpeta de información (temario) completa desde el inicio, su revisión y las pruebas de contenido en la app |
| Ali | Ali | Pantallas de gamificación, diseño, CI y despliegue de la web |

Rico lleva todo el backend y la IA; los demás solo tocan backend para revisar PRs. Uso "Alex" y "Ali" completos porque los dos empiezan con A.

**Reglas para todos**

- Una rama `feature/*` por tarea y PR a `main`; otra persona revisa antes de hacer merge.
- Cada PR sigue el checklist del CLAUDE.md de su módulo y trae pruebas.
- Si una tarea bloquea a otro, se avisa el mismo día.
- Junta corta 2 veces por semana: qué terminé, qué sigue, qué me bloquea.

## Fase 0 — Arranque

Antes de programar: el repo listo para los 4 y la carpeta de información completa. El temario se arma de una vez al inicio, no se va construyendo durante el proyecto.

- [ ] **D** — Reunir el material del curso: apuntes, libro y lo que pida el profesor
- [x] **D** — Armar la carpeta de información completa: `camino.yaml` y todas las unidades (Ley de Ohm, serie y paralelo, Kirchhoff, Thévenin, circuitos RC) con teoría, ejercicios de cálculo, explicaciones y pistas
- [ ] **D** — Revisar con alguien que sepa circuitos que fórmulas y respuestas sean correctas
- [ ] **D** — Guardar las capturas de referencia en `docs/referencias/`
- [ ] **R** — Hacer `git init -b main`, crear el repo en GitHub y agregar a los 3 como colaboradores
- [x] **R** — Proteger `main`: sin push directo, PR con 1 aprobación
- [x] **R** — Revisar y limpiar el repo accidental de `C:\Users\raulp`
- [x] **R** — Inicializar backend con uv (FastAPI, Ruff, mypy, pytest) y `docker-compose.yml` con PostgreSQL
- [x] **R** — Script que valida el formato de la carpeta de información y corre en el CI
- [x] **Alex** — Inicializar la app con create-expo-app (TypeScript, Expo Router) y moverla a `app/`
- [x] **Alex** — Configurar ESLint, TanStack Query, i18n y la carpeta `theme/`
- [x] **Ali** — CI en GitHub Actions: lint y pruebas de backend y app en cada PR
- [x] **Ali** — Agregar al `.claude/settings.json` la regla deny equivalente para PowerShell
- [ ] **Todos** — Leer los 4 CLAUDE.md, clonar, levantar el proyecto y abrir un PR de prueba

## Fase 1 — MVP: una lección de punta a punta

Al terminar la fase 1, un alumno se registra, entra al camino, hace una lección con opción múltiple y cálculo, recibe EXP y ve su racha.

### La base

- [x] **R** — Modelos y migración inicial: usuario, etapa, sección, unidad, nodo, lección, ejercicio, intento, progreso
- [x] **R** — Auth con JWT propio: registro, login, refresh, Argon2 y pruebas
- [x] **R** — Importador: carga toda la carpeta de información y `camino.yaml` a la base de datos
- [ ] **Alex** — Navegación con las 5 pestañas (Inicio, Desafíos, Ligas, Perfil, Más) y pantallas vacías
- [ ] **Alex** — Pantallas de registro e inicio de sesión y dónde guardar los tokens en móvil y web
- [ ] **Alex** — Componentes base en `ui/`: botón, barra de progreso, tarjeta, contador
- [x] **Ali** — Diseñar el sistema de EXP y racha: cuánto da cada ejercicio, cuándo se rompe la racha, zona horaria
- [ ] **Ali** — Tokens de diseño propios: colores, tipografía, espaciado (sin marca de Duolingo)

### La lección funciona

- [x] **R** — Endpoint del camino con nodos bloqueados y desbloqueados según el progreso
- [x] **R** — Endpoints para iniciar lección y comprobar respuesta; valores parametrizados generados en el backend
- [x] **R** — Validadores: opción múltiple, completar patrón y cálculo con unidad y tolerancia (parser seguro, sin `eval`)
- [x] **R** — Backend de EXP y racha: sumar al terminar la lección, con pruebas
- [ ] **Alex** — Pantalla del camino conectada a la API
- [ ] **Alex** — Pantalla de lección: barra de progreso, ejercicio, botón Comprobar, retroalimentación
- [ ] **Alex** — Componentes de los 3 tipos de ejercicio
- [ ] **Ali** — Pantalla de resumen de lección: EXP, % de precisión, conceptos
- [ ] **D** — Recorrer cada lección en la app y corregir errores del temario
- [ ] **Todos** — Probar el flujo completo en web y en el celular con Expo Go

## Fase 2 — Tutor y gamificación

Al terminar la fase 2, el alumno puede pedir ayuda en cualquier ejercicio, y la app ya se siente como un juego: energía, cofres, logros, desafíos y perfil.

### Tutor con IA

- [ ] **R** — Interfaz `TutorProvider` con un adaptador para el LLM elegido (`LLM_PROVIDER`, `LLM_MODEL`)
- [ ] **R** — Prompt del tutor: recibe enunciado, fórmula y pistas del temario, nunca el resultado
- [ ] **R** — Filtro que bloquea respuestas con el resultado (0.5 A, 500 mA, "la B")
- [ ] **R** — Las 3 pruebas obligatorias del tutor en `tests/tutor/`, con proveedor falso
- [ ] **R** — Endpoint del tutor con límite de peticiones por usuario para no gastar de más
- [ ] **D** — Lista de preguntas típicas de alumnos (incluidas las que intentan sacar la respuesta) para probar al tutor
- [ ] **Alex** — Botón "Pedir ayuda" y panel de chat del tutor dentro de la lección

### Gamificación

- [ ] **R** — Backend de energía: se gasta al fallar y se recarga con el tiempo
- [ ] **R** — Backend de cofres, logros y medallas
- [ ] **R** — Desafíos diarios y mensual: se generan cada día y se actualizan al ganar EXP
- [ ] **R** — Nodos de repaso y evaluación de unidad: mezclan ejercicios de toda la unidad
- [ ] **Ali** — Contador de energía en la app
- [ ] **Ali** — Pantalla de cofre ("Pulsa para abrir") y pantalla de racha al terminar la lección
- [ ] **Ali** — Pantallas de logros y medallas
- [ ] **Alex** — Pantalla de Desafíos con barras de progreso
- [ ] **Alex** — Perfil: resumen (racha, EXP total, liga), logros y medallas
- [ ] **Alex** — Configuración: preferencias, notificaciones, privacidad, cerrar sesión

## Fase 3 — Extras (solo si las fases 1 y 2 están terminadas)

Nada de esta fase entra si algo de la fase 1 o 2 sigue fallando. Ordenadas de más a menos valor para la demo.

- [ ] **R** — Ligas semanales: grupos, ranking por EXP y cierre automático cada semana
- [ ] **Alex** — Pantalla de Ligas con ranking y tiempo restante
- [ ] **R** — Ejercicio de identificar en un diagrama: formato en el temario y validador
- [ ] **D** — Ejercicios de diagrama para cada unidad
- [ ] **Alex** — Componente que dibuja el circuito y deja tocar sus elementos
- [ ] **R** — Backend de la tienda: recargas de energía y protector de racha
- [ ] **Ali** — Pantalla de la tienda
- [ ] **R** — Amigos y seguidores
- [ ] **Ali** — Notificaciones para recordar la racha

## Cierre — Pulido y demo

Esta fase es para que todo lo hecho funcione sin fallas, no para empezar funciones nuevas.

- [ ] **R** — Desplegar backend y base de datos en un servidor
- [ ] **Ali** — Desplegar la app web en un hosting
- [ ] **Ali** — Usuario de demo con progreso a la mitad, racha y logros para mostrar
- [ ] **Alex** — Revisar la app en celulares Android y iPhone y en la web; corregir pantallas rotas
- [ ] **R** — Revisar seguridad: ningún secreto en el repo, validación en backend, límites de peticiones
- [ ] **D** — Revisión final del temario: ortografía, fórmulas, explicaciones y pistas
- [ ] **R** — README final: cómo levantar el proyecto y cómo agregar una lección
- [ ] **Todos** — Guion de la demo y presentación; ensayarla al menos 2 veces

## El proyecto está terminado cuando

- Un alumno nuevo se registra y completa al menos 3 unidades en web y en el celular.
- Todos los ejercicios se validan en el backend.
- El tutor ayuda sin dar el resultado, y sus pruebas pasan.
- EXP, racha, energía, cofres, logros, desafíos y perfil funcionan.
- El CI pasa en `main` y la app está desplegada.

## Preguntas abiertas

- ¿Cuál es la fecha exacta de entrega? Si se acerca antes de terminar, se recorta la fase 3.
- ¿Qué proveedor de IA usará el tutor y quién paga las llamadas?
- ¿Dónde se despliega: un servicio gratuito o un servidor de Fractal?
