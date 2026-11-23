// Configuración común de Jest.

// Las fuentes se dan por cargadas: Jest no descarga archivos de fuente.
jest.mock("@expo-google-fonts/space-grotesk", () => ({
  useFonts: () => [true, null],
  SpaceGrotesk_600SemiBold: "SpaceGrotesk_600SemiBold",
  SpaceGrotesk_700Bold: "SpaceGrotesk_700Bold",
}));
