import { type ColorTokens, darkTheme, lightTheme } from "@/theme";

/** Contraste WCAG 2.x entre dos colores #RRGGBB. */
function contrast(a: string, b: string): number {
  const luminance = (hex: string) => {
    const [r, g, bl] = [1, 3, 5].map((i) => {
      const c = parseInt(hex.slice(i, i + 2), 16) / 255;
      return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * bl;
  };
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

// [texto, fondo, mínimo]. 4.5 = AA para texto normal; 3 = AA para íconos y texto grande.
const PAIRS: [keyof ColorTokens, keyof ColorTokens, number][] = [
  ["text", "background", 4.5],
  ["text", "surface", 4.5],
  ["textMuted", "surface", 4.5],
  ["textMuted", "background", 4.5],
  ["textOnPrimary", "primary", 4.5],
  ["primary", "surface", 4.5],
  ["primary", "primarySoft", 3],
  ["accent", "surface", 4.5],
  ["success", "successSoft", 4.5],
  ["error", "errorSoft", 4.5],
  ["text", "successSoft", 4.5],
  ["text", "errorSoft", 4.5],
  ["xp", "surface", 3],
  ["streak", "surface", 3],
  ["energy", "surface", 3],
  ["coins", "surface", 3],
  ["warning", "surface", 3],
  ["locked", "surface", 2],
];

describe.each([
  ["claro", lightTheme],
  ["oscuro", darkTheme],
])("tema %s", (_, theme) => {
  it.each(PAIRS)("%s sobre %s es legible (≥ %d:1)", (fg, bg, min) => {
    expect(contrast(theme.colors[fg], theme.colors[bg])).toBeGreaterThanOrEqual(min);
  });

  it("todos los colores son hex válidos", () => {
    for (const color of Object.values(theme.colors)) {
      expect(color).toMatch(/^#[0-9A-F]{6}$/);
    }
  });
});

it("el tema claro y el oscuro definen los mismos tokens", () => {
  expect(Object.keys(darkTheme.colors).sort()).toEqual(Object.keys(lightTheme.colors).sort());
});
