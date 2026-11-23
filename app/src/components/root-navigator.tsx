import { Stack } from "expo-router";

import { useSession } from "@/hooks/use-session";

/**
 * Navegador raíz. Mientras se recupera la sesión guardada no se pinta nada (sigue el splash);
 * después cada grupo decide: `(tabs)` exige sesión y `(auth)` exige no tenerla.
 */
export function RootNavigator() {
  const { status } = useSession();
  if (status === "loading") {
    return null;
  }
  return <Stack screenOptions={{ headerShown: false }} />;
}
