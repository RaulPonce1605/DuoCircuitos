# Circuitos: guía raíz para Claude

App de aprendizaje gamificado de **circuitos eléctricos** para web, iOS y Android: un camino de lecciones cortas con ejercicios, EXP, rachas y ligas.

Este archivo es la **única fuente** del producto, el stack, la estructura, el glosario y las reglas globales. Los CLAUDE.md de `backend/`, `app/` y `contenido/` solo contienen las convenciones de su módulo y no repiten nada de aquí.

> Convención de este documento: `← crear` marca archivos o carpetas que **aún no existen** y se crearán al inicializar cada módulo.

---

## 1. Producto

### 1.1 Camino de aprendizaje

```
Etapa → Sección → Unidad → Nodo
```

- Tipos de nodo: **lección**, **repaso**, **cofre**, **evaluación**.
- Todo se **desbloquea en orden**: un nodo se habilita al completar el anterior; una unidad, al completar la anterior; y así hacia arriba.
- El orden y la estructura del camino se definen en `contenido/camino.yaml`. Las lecciones viven en `contenido/unidades/`.

### 1.2 Flujo de una lección

1. Pantalla de lección con **barra de progreso** y **energía** visibles.
2. Los ejercicios se presentan **uno por uno**.
3. El usuario responde y pulsa **Comprobar**. El backend valida y responde con correcto o incorrecto y la **explicación**.
4. Al terminar: **resumen** (EXP ganada, % de precisión, conceptos trabajados) → **cofre** → actualización de **racha**.

### 1.3 Tipos de ejercicio

Sistema **extensible**: cada tipo tiene **un componente** en la app y **un validador** en el backend. Agregar un tipo nuevo no modifica los existentes.

| Tipo (id en código) | Descripción | Estado |
|---|---|---|
| `multiple_choice` | Teoría: opción múltiple | MVP |
| `fill_pattern` | Teoría: completar el patrón | MVP |
| `numeric` | Cálculo práctico: valores parametrizados al azar, respuesta con unidad y tolerancia, validación en backend | MVP |
| `circuit_diagram` | Identificar elementos en un diagrama de circuito | Para después |

- Componente: `app/src/components/exercises/<tipo>/`
- Validador: `backend/app/services/exercises/`
- Formato en el temario: `contenido/README.md`

### 1.4 Tutor con IA ("Pedir ayuda")

- Botón disponible durante un ejercicio.
- Da **pistas paso a paso** y **nunca entrega la respuesta**.
- Usa **solo** el contenido del temario (la lección y el ejercicio actuales). No usa conocimiento externo.
- El proveedor de LLM se configura por `.env` (`LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`).

### 1.5 Gamificación

EXP, racha, energía, desafíos diarios y mensuales, ligas semanales, cofres, logros y medallas. Las cifras (EXP por ejercicio, recarga de energía, tamaño de liga, etc.) viven en la configuración del backend, nunca fijas en la app.

### 1.6 Navegación

Pestañas: **Inicio · Desafíos · Ligas · Perfil · Más**. **Configuración** se abre desde Perfil o Más.

### 1.7 Referencias visuales

- Las capturas de referencia están en `docs/referencias/`. **Esa carpeta no se versiona** (está en `.gitignore`); cada integrante la tiene en local.
- Se toma el **flujo**, **NO la marca**.
- **Prohibido:** el nombre "Duolingo" en la UI, el código o los assets; su mascota; su paleta; su tipografía; sus sonidos; sus ilustraciones; usar capturas como assets de la app.
- **Por qué:** es un proyecto propio. Copiar la marca es una infracción y además nos deja sin identidad visual.

---

## 2. Stack

| Capa | Tecnología |
|---|---|
| App | Expo (React Native + Expo Router), TypeScript estricto → iOS, Android y web |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2 (async), Alembic, Pydantic v2 |
| Base de datos | PostgreSQL |
| Contrato | OpenAPI del backend → cliente TypeScript **generado** en `app/src/api/` |
| Autenticación | JWT propio (detalles en `backend/CLAUDE.md`) |
| Infraestructura local | `docker-compose.yml` con backend + PostgreSQL |
| Herramientas Python | uv, Ruff, mypy, pytest |
| Herramientas app | ESLint (`expo lint`), `tsc --noEmit`, Jest |

---

## 3. Estructura

```
proyectofinalcircuitos/
├── CLAUDE.md                     ← este archivo
├── README.md
├── .gitignore
├── .claude/settings.json
├── docker-compose.yml            ← crear
├── docs/
│   └── referencias/              capturas de referencia (no se versionan)
├── contenido/                    temario: única fuente del contenido
│   ├── CLAUDE.md
│   ├── README.md                 formato del temario
│   ├── camino.yaml               ← crear
│   └── unidades/
├── backend/
│   ├── CLAUDE.md
│   ├── .env.example
│   ├── pyproject.toml            ← crear
│   ├── alembic/                  ← crear (alembic init)
│   ├── tests/
│   └── app/
│       ├── main.py               ← crear
│       ├── core/
│       ├── api/
│       ├── models/
│       ├── schemas/
│       ├── services/
│       │   ├── exercises/
│       │   └── tutor/
│       └── content_import/
└── app/
    ├── CLAUDE.md
    ├── package.json              ← crear (create-expo-app)
    ├── app.json                  ← crear
    ├── assets/                   ← crear
    └── src/
        ├── app/                  rutas de Expo Router
        ├── components/
        │   ├── ui/
        │   └── exercises/
        ├── hooks/
        ├── services/
        ├── api/                  generado, no se edita
        ├── theme/
        └── i18n/
```

---

## 4. Glosario del dominio

La columna "En código" es el nombre obligatorio en modelos, tipos, rutas y variables.

| Término | Significado | En código |
|---|---|---|
| Etapa | Nivel más alto del camino; agrupa secciones | `stage` |
| Sección | Agrupa unidades de un mismo tema | `section` |
| Unidad | Agrupa nodos sobre un concepto (p. ej. Ley de Ohm) | `unit` |
| Nodo | Paso del camino: lección, repaso, cofre o evaluación | `node` |
| Lección | Nodo con una serie de ejercicios nuevos | `lesson` |
| Repaso | Nodo que reutiliza ejercicios ya vistos de la unidad | `review` |
| Cofre | Nodo o recompensa que entrega premios | `chest` |
| Evaluación | Nodo que cierra la unidad y mide el dominio | `assessment` |
| Ejercicio | Pregunta individual dentro de un nodo | `exercise` |
| Comprobar | Enviar la respuesta para validarla | `check` |
| EXP | Puntos de experiencia ganados al practicar | `xp` |
| Precisión | % de ejercicios correctos al primer intento en una sesión | `accuracy` |
| Racha | Días consecutivos con al menos una lección completada | `streak` |
| Energía | Recurso que se consume al practicar y se recarga con el tiempo | `energy` |
| Desafío diario / mensual | Meta con recompensa en un periodo | `daily_challenge` / `monthly_challenge` |
| Liga | Competencia semanal por EXP entre un grupo de usuarios | `league` |
| Logro | Hito alcanzado (p. ej. 7 días de racha) | `achievement` |
| Medalla | Insignia visible que representa un logro | `badge` |
| Tutor | Asistente con IA que da pistas | `tutor` |
| Pista | Ayuda parcial que no revela la respuesta | `hint` |
| Temario | Todo el contenido en `contenido/` | `syllabus` |

---

## 5. Reglas globales

### 5.1 Idioma: UI y documentación en español, código en inglés

- **Por qué:** los usuarios y el equipo hablan español, pero las librerías, los errores y los ejemplos del ecosistema están en inglés; mezclar idiomas en el código hace los nombres impredecibles.
- **Prohibido:** identificadores en español (`calcularRacha`, `usuario_id`); textos de UI escritos en inglés o fijos en el código.
- **Correcto:**
  ```ts
  const { streak } = useStreak();
  <Text>{t("home.streak", { days: streak })}</Text>
  ```

### 5.2 Secretos solo en `.env`

- **Por qué:** un secreto en el repo queda en el historial de git para siempre, aunque se borre después.
- **Prohibido:** llaves, contraseñas o URLs con credenciales en el código, en `docker-compose.yml`, en los CLAUDE.md o en los commits; subir cualquier `.env`.
- Cada módulo que necesite configuración tiene un `.env.example` con las **claves sin valores secretos**. Al agregar una variable nueva, se agrega también ahí.
- **Correcto:**
  ```
  # backend/.env.example
  LLM_API_KEY=
  ```

### 5.3 El contenido sale solo de `contenido/`

- **Por qué:** el temario debe poder revisarse y corregirse sin tocar código, y el tutor solo puede usar lo que esté ahí.
- **Prohibido:** enunciados, explicaciones, pistas o fórmulas escritos en el backend o en la app; datos de lecciones insertados a mano en la base de datos.
- **Correcto:** se escribe la lección en `contenido/unidades/...` y se carga con el importador `backend/app/content_import/`.

### 5.4 El backend es la fuente de verdad

- **Por qué:** si la app decidiera qué es correcto o cuánta EXP se gana, cualquiera podría manipularla.
- **Prohibido:** validar respuestas, calcular EXP, energía, racha o ligas en la app; enviar al cliente la respuesta correcta antes de Comprobar.
- **Correcto:** la app envía `{ exerciseInstanceId, answer }` y muestra lo que el backend responde.

### 5.5 Commits convencionales

- **Por qué:** historial legible y changelog automatizable.
- Formato: `tipo(scope): descripción en español, en minúsculas`.
- Tipos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `style`, `perf`. Scopes: `app`, `backend`, `contenido`, `infra`, `docs`.
- **Prohibido:** mensajes como `cambios`, `fix`, `wip` o `asdf`; mezclar módulos que no tienen relación en un solo commit.
- **Correcto:** `feat(backend): validar respuestas numéricas con tolerancia`

### 5.6 Ramas y Pull Requests

- **Por qué:** `main` siempre debe funcionar y todo cambio pasa por revisión de otro integrante.
- Ramas: `feature/<descripcion-corta>`, `fix/<descripcion-corta>`, `docs/<descripcion-corta>`. Toda rama sale de `main` y vuelve a `main` por PR.
- **Prohibido:** commit directo a `main`; `git push --force` a ramas compartidas; aprobar tu propio PR.
- **Correcto:**
  ```
  git switch -c feature/ejercicio-numerico
  ...
  git push -u origin feature/ejercicio-numerico   → abrir PR a main
  ```

### 5.7 Antes de abrir un PR

- Lint y pruebas del módulo pasan en local.
- Si cambió el OpenAPI, el cliente de `app/src/api/` está regenerado en el mismo PR.
- Si cambió el esquema de la base de datos, hay una migración de Alembic.
- Se completó el checklist correspondiente del CLAUDE.md del módulo.
