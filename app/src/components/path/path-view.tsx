import { useRouter } from "expo-router";
import { useTranslation } from "react-i18next";
import { ActivityIndicator, View } from "react-native";

import { EnergyCounter } from "@/components/gamification/energy-counter";
import { UnitCard } from "@/components/path/unit-card";
import { AppText, Button, Counter } from "@/components/ui";
import { useCurrentUser } from "@/hooks/use-current-user";
import { usePath } from "@/hooks/use-path";
import { useTheme } from "@/hooks/use-theme";
import { errorMessage } from "@/i18n/error-message";

export function PathView() {
  const { t } = useTranslation();
  const theme = useTheme();
  const router = useRouter();
  const path = usePath();
  const me = useCurrentUser();

  // La ruta de la lección también juega repasos y evaluaciones: `slug` es la clave del nodo.
  const openNode = (key: string) => router.push({ pathname: "/leccion/[slug]", params: { slug: key } });

  return (
    <View style={{ gap: theme.spacing.lg }}>
      <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
        <AppText variant="title" accessibilityRole="header">
          {t("home.title")}
        </AppText>
        {me.data ? (
          <View style={{ flexDirection: "row", gap: theme.spacing.md }}>
            <Counter
              testID="streak-counter"
              icon="flame"
              color="streak"
              value={me.data.streak_current}
              accessibilityLabel={t("home.streak", { count: me.data.streak_current })}
            />
            <Counter
              testID="xp-counter"
              icon="flash"
              color="xp"
              value={me.data.xp_total}
              accessibilityLabel={t("home.xp", { count: me.data.xp_total })}
            />
            <EnergyCounter energy={me.data.energy} />
          </View>
        ) : null}
      </View>

      {path.isPending ? (
        <ActivityIndicator
          color={theme.colors.primary}
          accessibilityLabel={t("home.loading")}
          style={{ marginTop: theme.spacing.xl }}
        />
      ) : path.isError ? (
        <View style={{ gap: theme.spacing.md }}>
          <AppText color="error" accessibilityRole="alert">
            {errorMessage(path.error)}
          </AppText>
          <Button label={t("common.retry")} variant="secondary" onPress={() => void path.refetch()} />
        </View>
      ) : (
        path.data.stages.map((stage) => (
          <View key={stage.slug} style={{ gap: theme.spacing.md }}>
            <AppText variant="caption" color="textMuted" accessibilityRole="header">
              {stage.title.toUpperCase()}
            </AppText>
            {stage.sections.flatMap((section) =>
              section.units.map((unit) => (
                <UnitCard key={unit.slug} unit={unit} onOpenNode={openNode} />
              )),
            )}
          </View>
        ))
      )}
    </View>
  );
}
