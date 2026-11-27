import Ionicons from "@expo/vector-icons/Ionicons";
import { useTranslation } from "react-i18next";
import { ActivityIndicator, Pressable, View } from "react-native";

import { NewBadges } from "@/components/rewards/new-badges";
import { AppText, Button, Card, Screen } from "@/components/ui";
import { type ChestTarget, useOpenChest } from "@/hooks/use-chest";
import { useTheme } from "@/hooks/use-theme";
import { errorMessage } from "@/i18n/error-message";

const CHEST_ICON_SIZE = 140;

type Props = {
  target: ChestTarget;
  onContinue: () => void;
};

/**
 * Pantalla del cofre: "Pulsa para abrir" (CLAUDE.md 1.2). El premio lo sortea el backend al
 * abrirlo; aquí solo se muestra.
 */
export function ChestView({ target, onContinue }: Props) {
  const { t } = useTranslation();
  const theme = useTheme();
  const open = useOpenChest(target);
  const chest = open.data;

  const title = target.kind === "node" ? t("chest.nodeTitle") : t("chest.title");

  if (!chest) {
    return (
      <Screen
        footer={
          open.isError ? <Button label={t("chest.continue")} variant="secondary" onPress={onContinue} /> : null
        }
      >
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center", gap: theme.spacing.lg }}>
          <AppText variant="display" align="center" accessibilityRole="header">
            {title}
          </AppText>
          <Pressable
            testID="chest-closed"
            onPress={() => open.mutate()}
            disabled={open.isPending}
            accessibilityRole="button"
            accessibilityLabel={t("chest.open")}
            accessibilityState={{ busy: open.isPending }}
            style={({ pressed }) => ({ transform: [{ scale: pressed ? 0.94 : 1 }] })}
          >
            <Ionicons name="gift" size={CHEST_ICON_SIZE} color={theme.colors.accent} />
          </Pressable>
          {open.isPending ? (
            <ActivityIndicator color={theme.colors.accent} accessibilityLabel={t("chest.opening")} />
          ) : (
            <AppText variant="subtitle" color="textMuted" align="center">
              {t("chest.tapToOpen")}
            </AppText>
          )}
          {open.isError ? (
            <AppText color="error" accessibilityRole="alert" align="center">
              {errorMessage(open.error)}
            </AppText>
          ) : null}
        </View>
      </Screen>
    );
  }

  const reward = chest.reward ?? { xp: 0, energy: 0 };
  return (
    <Screen scroll footer={<Button label={t("chest.continue")} onPress={onContinue} />}>
      <View style={{ alignItems: "center", gap: theme.spacing.sm, marginTop: theme.spacing.lg }}>
        <Ionicons name="gift-outline" size={CHEST_ICON_SIZE / 2} color={theme.colors.accent} />
        <AppText variant="title" align="center" accessibilityRole="header">
          {t("chest.opened")}
        </AppText>
      </View>
      <View testID="chest-reward" accessibilityLiveRegion="polite" style={{ gap: theme.spacing.md }}>
        <Card borderTone="xp" style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.md }}>
          <Ionicons name="flash" size={theme.sizes.iconLg} color={theme.colors.xp} />
          <AppText variant="title" color="xp">
            {t("chest.xp", { count: reward.xp })}
          </AppText>
        </Card>
        <Card borderTone="energy" style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.md }}>
          <Ionicons name="battery-charging" size={theme.sizes.iconLg} color={theme.colors.energy} />
          <AppText variant="subtitle" color="energy">
            {reward.energy > 0 ? t("chest.energy", { count: reward.energy }) : t("chest.noEnergy")}
          </AppText>
        </Card>
      </View>
      <NewBadges badges={chest.new_badges} />
    </Screen>
  );
}
