import { useTranslation } from "react-i18next";
import { View } from "react-native";

import { EmptyState } from "@/components/empty-state";
import { AppText, Button } from "@/components/ui";
import { useSession } from "@/hooks/use-session";
import { useTheme } from "@/hooks/use-theme";

/** Perfil mínimo de la fase 1: saludo y cerrar sesión. El perfil completo llega en la fase 2. */
export function ProfileSummary() {
  const { t } = useTranslation();
  const theme = useTheme();
  const { user, signOut } = useSession();

  return (
    <View style={{ flex: 1, gap: theme.spacing.md }}>
      {user ? (
        <AppText variant="subtitle" align="center">
          {t("profile.greeting", { name: user.display_name })}
        </AppText>
      ) : null}
      <EmptyState icon="person-circle" title={t("profile.title")} message={t("profile.empty")} />
      <Button label={t("profile.logout")} variant="secondary" onPress={() => void signOut()} />
    </View>
  );
}
