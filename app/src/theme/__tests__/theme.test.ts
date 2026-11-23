import { darkTheme, lightTheme } from "@/theme";

describe("theme", () => {
  it("el tema claro y el oscuro definen los mismos tokens", () => {
    expect(Object.keys(darkTheme.colors).sort()).toEqual(Object.keys(lightTheme.colors).sort());
  });

  it("todos los colores son hex válidos", () => {
    for (const color of [...Object.values(lightTheme.colors), ...Object.values(darkTheme.colors)]) {
      expect(color).toMatch(/^#[0-9A-F]{6}$/);
    }
  });
});
