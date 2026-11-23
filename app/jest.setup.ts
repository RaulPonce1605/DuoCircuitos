// Configuración común de Jest.

// Las fuentes se dan por cargadas: Jest no descarga archivos de fuente.
jest.mock("@expo-google-fonts/space-grotesk", () => ({
  useFonts: () => [true, null],
  SpaceGrotesk_600SemiBold: "SpaceGrotesk_600SemiBold",
  SpaceGrotesk_700Bold: "SpaceGrotesk_700Bold",
}));

// En Jest no hay pantalla que medir: el mock oficial da áreas seguras fijas.
jest.mock("react-native-safe-area-context", () =>
  jest.requireActual("react-native-safe-area-context/jest/mock").default,
);
