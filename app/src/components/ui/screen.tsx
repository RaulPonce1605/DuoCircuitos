import type { ReactNode } from "react";
import { ScrollView, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { useTheme } from "@/hooks/use-theme";

type Props = {
  children: ReactNode;
  /** Contenido desplazable (listas largas, formularios). */
  scroll?: boolean;
  /** Pie fijo abajo (por ejemplo, el botón Comprobar). */
  footer?: ReactNode;
};

/** Contenedor de pantalla: área segura, fondo del tema y ancho máximo en pantallas grandes. */
export function Screen({ children, scroll = false, footer }: Props) {
  const theme = useTheme();
  const content = {
    width: "100%" as const,
    maxWidth: theme.sizes.contentMaxWidth,
    alignSelf: "center" as const,
    padding: theme.spacing.md,
    gap: theme.spacing.md,
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: theme.colors.background }}>
      {scroll ? (
        <ScrollView contentContainerStyle={[content, { flexGrow: 1 }]}>{children}</ScrollView>
      ) : (
        <View style={[content, { flex: 1 }]}>{children}</View>
      )}
      {footer ? <View style={[content, { flex: 0 }]}>{footer}</View> : null}
    </SafeAreaView>
  );
}
