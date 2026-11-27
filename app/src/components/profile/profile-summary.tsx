import Ionicons from "@expo/vector-icons/Ionicons";
import { useRouter } from "expo-router";
import type { ComponentProps } from "react";
import { useTranslation } from "react-i18next";
import { ActivityIndicator, Pressable, View } from "react-native";

import { achievementGoal, badgeName, levelColor } from "@/components/achievements/names";
import { AppText, Button, Card } from "@/components/ui";
import { useAchievements } from "@/hooks/use-achievements";
import { useCurrentUser } from "@/hooks/use-current-user";
import { useTheme } from "@/hooks/use-theme";
import { errorMessage } from "@/i18n/error-message";
import type { ColorTokens } from "@/theme";

const AVATAR_SIZE = 72;
const RECENT_BADGES = 3;

type StatProps = {
  icon: ComponentProps<typeof Ionicons>["name"];
  color: keyof ColorTokens;
  label: string;
  value: string;
  testID: string;
};

function Stat({ icon, color, label, value, testID }: StatProps) {
  const theme = useTheme();
  return (
    <Card testID={testID} style={{ flexBasis: 140, flexGrow: 1, gap: theme.spacing.xs }}>
      <View accessible accessibilityLabel={`${label}: ${value}`} style={{ gap: theme.spacing.xs }}>
        <Ionicons name={icon} size={theme.sizes.iconMd} color={theme.colors[color]} />
        <AppText variant="subtitle" color={color}>
          {value}
        </AppText>
        <AppText variant="caption" color="textMuted">
          {label}
        </AppText>
      </View>
    </Card>
  );
}

/** Perfil: resumen (racha, EXP total, liga), logros y medallas. Todo sale del backend. */
export function ProfileSummary() {
  const { t, i18n } = useTranslation();
  const theme = useTheme();
  const router = useRouter();
  const me = useCurrentUser();
  const achievements = useAchievements();

  if (me.isPending) {
    return (
      <ActivityIndicator
        color={theme.colors.primary}
        accessibilityLabel={t("profile.loading")}
        style={{ marginTop: theme.spacing.xxl }}
      />
    );
  }
  if (me.isError) {
    return (
      <View style={{ gap: theme.spacing.md }}>
        <AppText color="error" accessibilityRole="alert">
          {errorMessage(me.error)}
        </AppText>
        <Button label={t("common.retry")} variant="secondary" onPress={() => void me.refetch()} />
      </View>
    );
  }

  const user = me.data;
  const since = new Date(user.created_at).toLocaleDateString(i18n.language, { month: "long", year: "numeric" });
  const levels = achievements.data?.achievements.reduce((sum, a) => sum + a.level, 0) ?? 0;
  const totalLevels = achievements.data?.achievements.reduce((sum, a) => sum + a.thresholds.length, 0) ?? 0;
  const recent = achievements.data?.badges.slice(0, RECENT_BADGES) ?? [];

  return (
    <View style={{ gap: theme.spacing.lg }}>
      <View style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.md }}>
        <View
          style={{
            width: AVATAR_SIZE,
            height: AVATAR_SIZE,
            borderRadius: theme.radii.pill,
            backgroundColor: theme.colors.primarySoft,
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <AppText variant="title" color="primary">
            {user.display_name.slice(0, 1).toUpperCase()}
          </AppText>
        </View>
        <View style={{ flex: 1, gap: theme.spacing.xxs }}>
          <AppText variant="title" accessibilityRole="header">
            {user.display_name}
          </AppText>
          <AppText variant="caption" color="textMuted">
            {t("profile.since", { date: since })}
          </AppText>
        </View>
        <Pressable
          onPress={() => router.push("/configuracion")}
          accessibilityRole="button"
          accessibilityLabel={t("profile.settings")}
          hitSlop={theme.spacing.sm}
          style={{ minWidth: theme.sizes.touchTarget, minHeight: theme.sizes.touchTarget, justifyContent: "center", alignItems: "center" }}
        >
          <Ionicons name="settings-outline" size={theme.sizes.iconLg} color={theme.colors.textMuted} />
        </Pressable>
      </View>

      <View style={{ gap: theme.spacing.sm }}>
        <AppText variant="subtitle" accessibilityRole="header">
          {t("profile.stats")}
        </AppText>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: theme.spacing.md }}>
          <Stat
            testID="profile-streak"
            icon="flame"
            color="streak"
            label={t("profile.streak")}
            value={t("profile.days", { count: user.streak_current })}
          />
          <Stat
            testID="profile-longest-streak"
            icon="flame-outline"
            color="streak"
            label={t("profile.longestStreak")}
            value={t("profile.days", { count: user.streak_longest })}
          />
          <Stat testID="profile-xp" icon="flash" color="xp" label={t("profile.xp")} value={String(user.xp_total)} />
          {/* Las ligas llegan en la fase 3: mientras, el alumno no tiene liga. */}
          <Stat testID="profile-league" icon="podium" color="primary" label={t("profile.league")} value={t("profile.noLeague")} />
        </View>
      </View>

      <Card style={{ gap: theme.spacing.sm }}>
        <AppText variant="subtitle" accessibilityRole="header">
          {t("profile.achievements")}
        </AppText>
        {achievements.isPending ? (
          <ActivityIndicator color={theme.colors.primary} accessibilityLabel={t("achievements.loading")} />
        ) : achievements.isError ? (
          <AppText color="error" accessibilityRole="alert">
            {errorMessage(achievements.error)}
          </AppText>
        ) : (
          <AppText color="textMuted">{t("profile.achievementsProgress", { levels, total: totalLevels })}</AppText>
        )}
        <Button label={t("profile.seeAchievements")} variant="secondary" onPress={() => router.push("/logros")} />
      </Card>

      <Card style={{ gap: theme.spacing.sm }}>
        <AppText variant="subtitle" accessibilityRole="header">
          {t("profile.badges")}
        </AppText>
        {achievements.data && recent.length === 0 ? <AppText color="textMuted">{t("profile.noBadges")}</AppText> : null}
        {recent.map((badge) => (
          <View
            key={`${badge.achievement_id}-${badge.level}`}
            style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.sm }}
          >
            <Ionicons name="medal" size={theme.sizes.iconLg} color={theme.colors[levelColor(badge.level)]} />
            <View style={{ flex: 1 }}>
              <AppText variant="bodyStrong">{badgeName(badge)}</AppText>
              <AppText variant="caption" color="textMuted">
                {achievementGoal(badge.achievement_id, badge.threshold)}
              </AppText>
            </View>
          </View>
        ))}
        <Button label={t("profile.seeBadges")} variant="secondary" onPress={() => router.push("/medallas")} />
      </Card>
    </View>
  );
}
