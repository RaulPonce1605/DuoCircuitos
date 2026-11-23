// https://docs.expo.dev/guides/using-eslint/
const { defineConfig } = require("eslint/config");
const expoConfig = require("eslint-config-expo/flat");

module.exports = defineConfig([
  expoConfig,
  {
    ignores: ["dist/*", "src/api/*"],
  },
  {
    files: ["**/*.ts", "**/*.tsx"],
    rules: {
      // app/CLAUDE.md 4.8: TypeScript estricto
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/ban-ts-comment": "error",
      // app/CLAUDE.md 4.3: todo texto visible sale de i18n
      "react/jsx-no-literals": ["error", { noStrings: false, ignoreProps: true }],
      // app/CLAUDE.md 4.1: solo los servicios llaman al backend
      "no-restricted-globals": [
        "error",
        { name: "fetch", message: "Usa un servicio de src/services/ con el cliente generado." },
      ],
      "no-restricted-imports": [
        "error",
        { paths: [{ name: "axios", message: "Usa el cliente generado en src/api/." }] },
      ],
    },
  },
  {
    // En las pruebas los textos fijos son datos de prueba, no texto de la UI.
    files: ["**/__tests__/**", "**/*.test.ts", "**/*.test.tsx"],
    rules: { "react/jsx-no-literals": "off" },
  },
]);
