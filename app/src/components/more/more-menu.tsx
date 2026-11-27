import { useRouter } from "expo-router";
import { useTranslation } from "react-i18next";

import { AppText, Card, ListRow } from "@/components/ui";
import { useTheme } from "@/hooks/use-theme";

/** Pestaña Más: accesos a logros, medallas y configuración. */
export function MoreMenu() {
  const { t } = useTranslation();
  const theme = useTheme();
  const router = useRouter();
  return (
    <>
      <AppText variant="title" accessibilityRole="header">
        {t("more.title")}
      </AppText>
      <Card style={{ gap: theme.spacing.xs }}>
        <ListRow icon="trophy" label={t("more.achievements")} onPress={() => router.push("/logros")} />
        <ListRow icon="medal" iconColor="accent" label={t("more.badges")} onPress={() => router.push("/medallas")} />
      </Card>
      <Card>
        <ListRow icon="settings" label={t("more.settings")} onPress={() => router.push("/configuracion")} />
      </Card>
    </>
  );
}
