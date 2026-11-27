# Tokens de diseño

Identidad visual **propia** de Circuitos (CLAUDE.md 1.7): nada de la paleta, tipografía, mascota ni ilustraciones de las apps de referencia. Los valores viven en `app/src/theme/` y los componentes solo los usan por nombre (`theme.colors.primary`), nunca con valores sueltos (`app/CLAUDE.md` 4.4).

## Idea

Una placa de circuito: **verde azulado** (la placa) como color principal y **cobre** (las pistas) como acento, sobre un fondo cálido de papel. Para títulos, **Space Grotesk**, una tipografía geométrica de aire técnico; el cuerpo usa la fuente del sistema, que es la más legible en cada plataforma.

## Colores

| Token | Claro | Oscuro | Uso |
|---|---|---|---|
| `primary` | `#0B6E77` | `#45C3CD` | Botón principal, nodo actual, progreso |
| `primarySoft` | `#D5ECEE` | `#123A3E` | Opción seleccionada, fondos suaves |
| `accent` | `#B85C22` | `#F0965A` | Cobre: detalles y énfasis |
| `success` / `successSoft` | `#24793A` / `#DDF0E1` | `#5CC97A` / `#173823` | Respuesta correcta |
| `error` / `errorSoft` | `#B3261E` / `#F9DEDC` | `#F2827A` / `#47201D` | Respuesta incorrecta |
| `xp` | `#8A5A00` | `#F2C14E` | EXP |
| `streak` | `#C2491D` | `#FF8A57` | Racha |
| `energy` | `#2F5FB3` | `#82AEF5` | Energía |
| `locked` | `#A39C92` | `#5E676D` | Nodos bloqueados |
| `background` · `surface` · `surfaceMuted` · `border` | | | Superficies |
| `text` · `textMuted` · `textOnPrimary` | | | Texto |

**Accesibilidad:** una prueba (`app/src/theme/__tests__/theme.test.ts`) exige contraste WCAG AA en los dos temas: 4.5:1 para texto y 3:1 para íconos y texto grande. Si cambias un color y el contraste no alcanza, el CI falla.

## Tipografía

| Estilo | Fuente | Tamaño / interlineado |
|---|---|---|
| `display` | Space Grotesk Bold | 34 / 40 |
| `title` | Space Grotesk Bold | 26 / 32 |
| `subtitle` | Space Grotesk SemiBold | 19 / 25 |
| `button` | Space Grotesk Bold | 16 / 20 |
| `body` · `bodyStrong` | Sistema | 16 / 23 |
| `caption` | Sistema | 13 / 18 |

## Espaciado, radios y tamaños

- **Espaciado** en escala de 4: `xxs 2 · xs 4 · sm 8 · md 16 · lg 24 · xl 32 · xxl 48`.
- **Radios:** `sm 8 · md 14 · lg 20 · pill 999`.
- **Bordes:** `thin 1 · thick 2`.
- **Tamaños:** área táctil mínima de 48, íconos de 18/24/32, barra de progreso de 14 y ancho máximo del contenido de 560 en web.

## Pendiente

Los íconos de la app y la imagen del splash todavía son los genéricos de Expo. El color de fondo del splash ya usa la paleta.
