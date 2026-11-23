# app/: convenciones

> El dominio (producto, glosario, reglas globales) está en el CLAUDE.md raíz. **No lo repitas aquí**; este archivo solo contiene convenciones de la app.

Stack: Expo · React Native · Expo Router · TypeScript estricto. Objetivos: iOS, Android y web.

---

## 1. Inicializar Expo (una sola vez)

`create-expo-app` falla si la carpeta destino ya tiene archivos, y `app/` ya tiene este CLAUDE.md y `src/`. Por eso:

1. Generar el proyecto en una carpeta temporal **fuera** del repo con la plantilla de TypeScript.
2. Mover su contenido a `app/` sin sobrescribir `CLAUDE.md` ni `src/`.
3. Configurar Expo Router para usar `src/app/` como carpeta de rutas y borrar la carpeta de rutas de ejemplo de la plantilla.
4. Activar `"strict": true` en `tsconfig.json` y el alias `@/*` → `src/*`.

## 2. Estructura

```
app/
├── package.json             ← crear
├── app.json                 ← crear
├── tsconfig.json            ← crear
├── assets/                  ← crear  íconos, fuentes e imágenes propias
└── src/
    ├── app/                 rutas de Expo Router; solo componen pantallas
    │   ├── (tabs)/          ← crear  inicio, desafios, ligas, perfil, mas
    │   └── leccion/         ← crear
    ├── components/
    │   ├── ui/              piezas genéricas: Button, ProgressBar, Card...
    │   └── exercises/       un componente por tipo de ejercicio + registro
    ├── hooks/               estado y datos para las pantallas
    ├── services/            casos de uso; únicos que llaman al cliente API
    ├── api/                 cliente GENERADO desde el OpenAPI; no se edita
    ├── theme/               colores, tipografía, espaciados, radios
    └── i18n/                configuración y archivos de textos (es.json)
```

## 3. Comandos (cuando exista package.json)

```
npx expo start
npm run lint
npx tsc --noEmit
npm test
npm run api:generate        ← crear  regenera src/api desde el OpenAPI del backend
```

---

## 4. Reglas

### 4.1 Capas: Pantalla → Hook → Servicio → Cliente API

- **Por qué:** cada capa se prueba por separado; si cambia el backend solo se toca el servicio; las pantallas quedan simples.
- **Pantalla** (`src/app/` + componentes): dibuja y llama hooks.
- **Hook** (`src/hooks/`): expone datos, estado de carga y acciones; usa TanStack Query para caché y reintentos (el `QueryClient` está en `src/services/query-client.ts`).
- **Servicio** (`src/services/`): llama al cliente generado y adapta la respuesta al modelo de la app.
- **Cliente API** (`src/api/`): generado; nadie lo escribe a mano.
- **Prohibido:** `fetch`, `axios` o el cliente API dentro de componentes, pantallas o hooks; saltarse capas; lógica de negocio en componentes.
- **Correcto:**
  ```ts
  export const lessonService = {
    check: (instanceId: string, answer: Answer) =>
      api.POST("/exercises/{instance_id}/check", { params: { path: { instance_id: instanceId } }, body: { answer } }),
  };

  export function useCheckExercise() {
    return useMutation({ mutationFn: ({ id, answer }: CheckArgs) => lessonService.check(id, answer) });
  }

  export default function LessonScreen() {
    const check = useCheckExercise();
    ...
  }
  ```

### 4.2 Cliente API generado

- **Por qué:** los tipos de la app siempre coinciden con el backend; si algo cambia, falla la compilación y no la app en producción.
- Herramientas: `openapi-typescript` (corre con `npx` en versión fija, porque aún no soporta TypeScript 6 como dependencia) genera `src/api/schema.d.ts` desde `backend/openapi.json`; `openapi-fetch` hace las peticiones tipadas.
- El CI falla si `backend/openapi.json` o `src/api/` están desactualizados.
- **Prohibido:** editar archivos de `src/api/`; escribir a mano tipos que ya existen en el OpenAPI.
- **Correcto:** cambia el backend → `npm run api:generate` → se commitea el resultado en el mismo PR.

### 4.3 i18n obligatorio

- **Por qué:** ningún texto queda escondido en el código; la revisión de redacción se hace en un solo archivo y se pueden agregar idiomas después.
- Todo texto visible sale de `src/i18n/` con claves por pantalla: `lesson.check`, `home.streak`.
- Los códigos de error del backend (`node_locked`...) se traducen en `errors.<code>`.
- **Prohibido:** texto literal en JSX (`<Text>Comprobar</Text>`); concatenar textos traducidos; mostrar mensajes de error crudos del backend.
- **Correcto:** `<Text>{t("lesson.check")}</Text>`

### 4.4 Tema propio

- **Por qué:** identidad visual propia y consistente; cambiar la paleta debe ser editar un archivo.
- Colores, tipografía, espaciados y radios salen de `src/theme/`.
- **Prohibido:** colores hex, tamaños o fuentes sueltos en componentes; usar la paleta, mascota, ilustraciones o assets de las referencias.
- **Correcto:** `backgroundColor: theme.colors.surface`

### 4.5 Ejercicios: un componente por tipo + registro

- **Por qué:** agregar un tipo no toca la pantalla de lección ni los otros tipos.
- Carpeta `components/exercises/<tipo>/` con un componente que recibe el ejercicio público y devuelve una respuesta; se registra por id en `components/exercises/registry.ts`.
- El componente **no valida**: solo arma la respuesta. La validación es del backend.
- **Prohibido:** `switch` por tipo en la pantalla de lección; recibir o calcular la solución en el cliente.
- **Correcto:**
  ```ts
  export const exerciseRegistry: Record<ExerciseType, ExerciseComponent> = {
    multiple_choice: MultipleChoice,
    fill_pattern: FillPattern,
    numeric: NumericAnswer,
  };
  ```

### 4.6 Rutas delgadas

- **Por qué:** Expo Router decide la navegación por los archivos; si la lógica vive ahí, no se puede reutilizar ni probar.
- Un archivo en `src/app/` solo lee parámetros de la ruta y compone componentes y hooks.
- **Prohibido:** estado complejo o llamadas a servicios directamente en archivos de ruta.

### 4.7 Sesión y tokens

- Mobile: tokens en `expo-secure-store`. Web: **decisión pendiente** (secure-store no funciona en web).
- **Prohibido:** tokens en `AsyncStorage` o en logs.

### 4.8 TypeScript estricto

- **Por qué:** los errores se ven al compilar y no en el teléfono de alguien.
- **Prohibido:** `any`, `@ts-ignore`, `as` para forzar tipos de la API.

---

## 5. Checklists

### Nueva pantalla
- [ ] Ruta en `src/app/` que solo compone.
- [ ] Hook en `src/hooks/` para datos y acciones.
- [ ] Servicio en `src/services/` si llama al backend.
- [ ] Todos los textos en `src/i18n/` (incluyendo errores y estados vacíos).
- [ ] Estilos desde `src/theme/`.
- [ ] Estados de carga, error y vacío manejados.
- [ ] Probada en web y en al menos un móvil (Expo Go o emulador).
- [ ] `npm run lint` y `npx tsc --noEmit` sin errores.

### Nuevo tipo de ejercicio (parte app)
- [ ] La parte backend ya está en `main` y el cliente regenerado.
- [ ] Componente en `components/exercises/<tipo>/` que solo arma la respuesta.
- [ ] Registrado en `components/exercises/registry.ts`.
- [ ] Textos en i18n.
- [ ] Prueba del componente con Jest.

### Consumir un endpoint nuevo
- [ ] `npm run api:generate` ejecutado y commiteado.
- [ ] Función en el servicio correspondiente.
- [ ] Hook que la expone.
- [ ] Códigos de error nuevos traducidos en `errors.*`.
