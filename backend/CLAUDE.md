# backend/: convenciones

> El dominio (producto, glosario, reglas globales) está en el CLAUDE.md raíz. **No lo repitas aquí**; este archivo solo contiene convenciones del backend.

Stack: Python 3.12 · FastAPI · SQLAlchemy 2 async · Alembic · Pydantic v2 · PostgreSQL · uv · Ruff · mypy · pytest.

---

## 1. Estructura

```
backend/
├── .env.example
├── pyproject.toml           ← crear
├── alembic/                 ← crear (uv run alembic init -t async alembic)
├── tests/
│   ├── api/                 ← crear
│   ├── services/            ← crear
│   └── tutor/               ← crear
└── app/
    ├── main.py              ← crear  instancia de FastAPI y registro de routers
    ├── core/
    │   ├── config.py        ← crear  Settings (pydantic-settings) leídos del .env
    │   ├── db.py            ← crear  engine y sesión async
    │   └── security.py      ← crear  JWT y hashing de contraseñas
    ├── api/                 routers por recurso; delgados
    ├── models/              modelos ORM de SQLAlchemy
    ├── schemas/             modelos Pydantic de entrada y salida
    ├── services/            lógica de negocio
    │   ├── exercises/       un validador por tipo + registro
    │   └── tutor/           servicio del tutor + adaptadores de LLM
    └── content_import/      lee contenido/ y lo carga en la base de datos
```

## 2. Comandos (cuando exista pyproject.toml)

```
uv sync
docker compose up -d db
uv run alembic upgrade head
uv run fastapi dev app/main.py
uv run ruff check . && uv run ruff format --check . && uv run mypy app && uv run pytest
```

---

## 3. Reglas

### 3.1 Capas: `api` → `services` → `models`

- **Por qué:** las rutas se pueden probar y cambiar sin tocar la lógica, y la lógica se reutiliza desde el importador, los jobs y las pruebas.
- `api/` solo recibe, valida con schemas, llama a un servicio y devuelve un schema.
- `services/` contiene la lógica y usa la sesión de base de datos que recibe.
- **Prohibido:** consultas de SQLAlchemy dentro de `api/`; lógica de negocio en las rutas; que un servicio importe de `api/`.
- **Correcto:**
  ```python
  @router.post("/exercises/{instance_id}/check", response_model=CheckResult, operation_id="checkExercise")
  async def check_exercise(instance_id: UUID, body: CheckRequest, db: DbSession, user: CurrentUser) -> CheckResult:
      return await exercise_service.check(db, user, instance_id, body.answer)
  ```

### 3.2 Async de punta a punta

- **Por qué:** FastAPI y el driver async (`asyncpg`) solo rinden si nada bloquea el event loop.
- **Prohibido:** `Session` síncrona, `requests`, `time.sleep` y cualquier I/O bloqueante en código async. Para HTTP se usa `httpx.AsyncClient`.
- **Correcto:** `result = await db.execute(select(User).where(User.id == user_id))`

### 3.3 Schemas Pydantic v2 como contrato

- **Por qué:** el OpenAPI se genera de los schemas y de él sale el cliente de la app; si devuelves modelos ORM, el contrato cambia sin que nadie lo note.
- Schemas separados por uso: `XCreate`, `XUpdate`, `XRead`. Configuración `model_config = ConfigDict(from_attributes=True)` en los de lectura.
- **Prohibido:** devolver modelos ORM directamente; `dict` sin tipo como respuesta; usar `class Config` (es de Pydantic v1).
- **Correcto:**
  ```python
  class UserRead(BaseModel):
      model_config = ConfigDict(from_attributes=True)
      id: UUID
      display_name: str
      xp: int
  ```

### 3.4 Migraciones con Alembic

- **Por qué:** todos los integrantes y el servidor deben tener el mismo esquema, reproducible.
- **Prohibido:** `Base.metadata.create_all()` fuera de las pruebas; modificar una migración que ya está en `main`; cambiar modelos sin migración en el mismo PR.
- **Correcto:** `uv run alembic revision --autogenerate -m "add streak table"`, revisar el archivo generado y luego `upgrade head`.

### 3.5 Configuración solo desde `core/config.py`

- **Por qué:** un único lugar valida y tipa las variables de entorno; si falta una, la app falla al arrancar y no a mitad de una petición.
- **Prohibido:** `os.environ` / `os.getenv` fuera de `core/config.py`; valores de gamificación (EXP, energía, tamaño de liga) fijos en el código de los servicios.
- **Correcto:**
  ```python
  class Settings(BaseSettings):
      model_config = SettingsConfigDict(env_file=".env")
      database_url: str
      jwt_secret: SecretStr
      llm_provider: str
  ```

### 3.6 Autenticación: JWT propio

- **Decisión:** autenticación propia con JWT, sin proveedor externo. Todo vive en `core/security.py` y en un `services/auth`.
- **Por qué:** no dependemos de un servicio de terceros y lo controlamos todo desde el backend.
- Contraseñas con hash **Argon2** (`pwdlib`). JWT firmados con `PyJWT` y `JWT_SECRET` del `.env`.
- Access token de vida corta + refresh token de vida larga. El refresh se guarda **hasheado** en la base de datos para poder revocarlo y se rota en cada uso.
- **Decisiones pendientes:** duración exacta de cada token; algoritmo (HS256 vs. RS256); inicio de sesión social.
- **Prohibido:** guardar contraseñas o refresh tokens en texto plano; poner datos sensibles en el payload del JWT; validar el token a mano en cada ruta.
- **Correcto:** la ruta recibe el usuario por dependencia: `user: CurrentUser` (un `Annotated[User, Depends(get_current_user)]`).

### 3.7 Ejercicios: un validador por tipo + registro

- **Por qué:** agregar un tipo nuevo no debe tocar los existentes ni llenar el servicio de `if tipo == ...`.
- Cada tipo implementa la misma interfaz (`generate_instance` y `validate`) y se registra por su id (`multiple_choice`, `fill_pattern`, `numeric`...).
- **Prohibido:** `if`/`match` por tipo de ejercicio fuera del registro; validar respuestas en la app; enviar la solución al cliente antes de Comprobar.
- **Correcto:**
  ```python
  @register("numeric")
  class NumericValidator(ExerciseValidator):
      def generate_instance(self, exercise: Exercise, rng: Random) -> ExerciseInstance: ...
      def validate(self, instance: ExerciseInstance, answer: NumericAnswer) -> CheckResult: ...
  ```

### 3.8 Ejercicios numéricos parametrizados

- **Por qué:** cada intento tiene valores distintos para que no se memoricen respuestas, y la validación debe ser reproducible.
- El backend sortea los parámetros dentro de los rangos del temario, **guarda la instancia** (parámetros + semilla) y devuelve el enunciado ya resuelto con un `exercise_instance_id`.
- Al Comprobar, el backend recalcula el resultado con la fórmula del temario, normaliza los prefijos SI de la unidad (m, k, µ, M...) y compara con la tolerancia.
- **Prohibido:** `eval()` / `exec()` sobre fórmulas; confiar en parámetros enviados por el cliente; comparar floats con `==`.
- **Correcto:** evaluar la fórmula con un parser seguro sobre un AST con lista blanca de operadores y funciones (`+ - * / ^ ( )`, `sqrt`, `abs`, `sin`, `cos`, `tan`, `atan`, `log10`, `pi`).

### 3.9 Tutor con IA

- **Por qué:** debe ayudar sin regalar la respuesta, y no debe atarnos a un proveedor de LLM.
- Interfaz `TutorProvider` en `services/tutor/` con **un adaptador por proveedor**; se elige con `LLM_PROVIDER` / `LLM_MODEL` del `.env`.
- El prompt se construye **solo** con contenido del temario: teoría de la lección, conceptos, enunciado con sus parámetros, pistas y el historial de pistas ya dadas.
- **El prompt nunca incluye:** el resultado calculado, la opción correcta, `respuestas_aceptadas` ni la `explicacion`.
- Toda respuesta del LLM pasa por un **filtro de salida** que detecta el resultado final (en cualquier prefijo SI y dentro de la tolerancia) o la opción correcta; si lo encuentra, descarta la respuesta y devuelve la siguiente pista del temario.
- **Pruebas obligatorias** en `tests/tutor/`:
  1. `build_prompt` nunca contiene el resultado ni la opción correcta, para **todos** los ejercicios de `contenido/` y varias semillas.
  2. El filtro bloquea un proveedor falso que intenta filtrar la respuesta ("0.024 A", "24 mA", "la respuesta es la B"...).
  3. Las pruebas usan un proveedor **falso**; nunca llaman a un LLM real.
  - Un PR que toque `services/tutor/` no se aprueba si estas pruebas no pasan.
- **Prohibido:** llamar al SDK de un proveedor fuera de su adaptador; dar al LLM conocimiento fuera del temario; desactivar el filtro "temporalmente".
- **Correcto:**
  ```python
  prompt = build_prompt(lesson, instance, hints_given)
  raw = await provider.complete(prompt)
  return guard_output(raw, instance, fallback=next_hint(lesson, hints_given))
  ```

### 3.10 OpenAPI estable

- **Por qué:** la app genera su cliente con él; un nombre que cambia rompe el código de la app.
- Cada ruta declara `operation_id` en camelCase, `response_model` y `tags`.
- **Prohibido:** rutas sin `response_model`; renombrar un `operation_id` sin regenerar el cliente en el mismo PR.

### 3.11 Errores

- **Por qué:** los servicios no deben depender de HTTP.
- Los servicios lanzan excepciones de dominio (`NotEnoughEnergy`, `NodeLocked`...); un manejador en `main.py` las traduce a respuestas HTTP con un código de error estable que la app traduce con i18n.
- **Prohibido:** `HTTPException` dentro de `services/`; mensajes de error para el usuario escritos en el backend.
- **Correcto:** `raise NodeLocked(node_id)` → `409 {"code": "node_locked"}`.

### 3.12 Pruebas

- Pytest con `pytest-asyncio`. Base de datos de pruebas en PostgreSQL (no SQLite, porque cambia el comportamiento).
- Cada servicio nuevo trae pruebas en `tests/services/`; cada endpoint, al menos una prueba del caso feliz y una de error en `tests/api/`.

---

## 4. Checklists

### Nuevo endpoint
- [ ] Schemas de entrada y salida en `schemas/`.
- [ ] Lógica en un servicio de `services/`, sin SQL en la ruta.
- [ ] Ruta en `api/` con `operation_id`, `response_model` y `tags`.
- [ ] Protegida con `CurrentUser` si no es pública.
- [ ] Errores como excepciones de dominio con código estable.
- [ ] Migración de Alembic si cambió el esquema.
- [ ] Pruebas en `tests/api/` y `tests/services/`.
- [ ] Cliente de la app regenerado en el mismo PR.

### Nuevo tipo de ejercicio (parte backend)
- [ ] Id del tipo agregado a la tabla del CLAUDE.md raíz y al formato de `contenido/README.md`.
- [ ] Schema de la respuesta (`XAnswer`) y del ejercicio público (sin solución).
- [ ] Validador con `@register("<tipo>")` en `services/exercises/`.
- [ ] El importador reconoce y valida el tipo.
- [ ] El filtro del tutor sabe detectar la solución de este tipo + pruebas en `tests/tutor/`.
- [ ] Pruebas del validador: correcta, incorrecta y casos límite.

### Nuevo proveedor de LLM
- [ ] Adaptador en `services/tutor/` que implementa `TutorProvider`.
- [ ] Variables nuevas en `.env.example` y en `Settings`.
- [ ] Pruebas con respuestas grabadas o falsas; sin llamadas reales.
