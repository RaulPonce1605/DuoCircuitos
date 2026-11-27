import { Redirect, Stack } from "expo-router";
import { useTranslation } from "react-i18next";

import { useSession } from "@/hooks/use-session";
import { useTheme } from "@/hooks/use-theme";
import { fonts } from "@/theme";

/** Pantallas que se abren desde Perfil o Más: logros, medallas y configuración. */
export default function AccountLayout() {
  const { t } = useTranslation();
  const theme = useTheme();
  const { status } = useSession();
  if (status !== "signedIn") {
    return <Redirect href="/login" />;
  }
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: theme.colors.surface },
        headerTintColor: theme.colors.primary,
        headerTitleStyle: { fontFamily: fonts.headingMedium, color: theme.colors.text },
        contentStyle: { backgroundColor: theme.colors.background },
      }}
    >
      <Stack.Screen name="logros" options={{ title: t("achievements.title") }} />
      <Stack.Screen name="medallas" options={{ title: t("badges.title") }} />
      <Stack.Screen name="configuracion" options={{ title: t("settings.title") }} />
      <Stack.Screen name="tienda" options={{ title: t("shop.title") }} />
      <Stack.Screen name="amigos" options={{ title: t("friends.title") }} />
    </Stack>
  );
}
