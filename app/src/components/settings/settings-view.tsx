import { type ReactNode, useState } from "react";
import { useTranslation } from "react-i18next";
import { ActivityIndicator, Switch, View } from "react-native";

import { AppText, Button, Card, ListRow, Screen, TextField } from "@/components/ui";
import { useCurrentUser } from "@/hooks/use-current-user";
import { useSession } from "@/hooks/use-session";
import { useTheme } from "@/hooks/use-theme";
import { useUpdateUser } from "@/hooks/use-update-user";
import { errorMessage } from "@/i18n/error-message";
import { deviceTimezone, type User } from "@/services/auth-service";
import type { UserUpdate } from "@/services/user-service";

type ToggleField = keyof Pick<UserUpdate, "notify_streak_reminder" | "notify_challenges" | "profile_public">;

function Section({ title, children }: { title: string; children: ReactNode }) {
  const theme = useTheme();
  return (
    <View style={{ gap: theme.spacing.sm }}>
      <AppText variant="subtitle" accessibilityRole="header">
        {title}
      </AppText>
      <Card style={{ gap: theme.spacing.xs }}>{children}</Card>
    </View>
  );
}

function SettingsForm({ user }: { user: User }) {
  const { t } = useTranslation();
  const theme = useTheme();
  const { signOut } = useSession();
  const update = useUpdateUser();
  const [name, setName] = useState(user.display_name);
  const device = deviceTimezone();
  const trimmed = name.trim();

  const toggle = (field: ToggleField, label: string, hint: string, icon: "flame" | "flag" | "eye") => (
    <ListRow
      icon={icon}
      label={label}
      detail={hint}
      trailing={
        <Switch
          value={user[field]}
          onValueChange={(value) => update.mutate({ [field]: value })}
          disabled={update.isPending}
          accessibilityLabel={label}
          trackColor={{ true: theme.colors.primary, false: theme.colors.surfaceMuted }}
        />
      }
    />
  );

  return (
    <>
      {update.isError ? (
        <AppText color="error" accessibilityRole="alert">
          {errorMessage(update.error)}
        </AppText>
      ) : update.isSuccess ? (
        <AppText color="success" accessibilityLiveRegion="polite">
          {t("settings.saved")}
        </AppText>
      ) : null}

      <Section title={t("settings.preferences")}>
        <TextField label={t("settings.displayName")} value={name} onChangeText={setName} maxLength={50} />
        <Button
          label={t("settings.save")}
          variant="secondary"
          onPress={() => update.mutate({ display_name: trimmed })}
          disabled={trimmed === "" || trimmed === user.display_name}
          loading={update.isPending && update.variables?.display_name !== undefined}
        />
        <ListRow icon="time" label={t("settings.timezone")} detail={`${user.timezone}. ${t("settings.timezoneHint")}`} />
        {device !== user.timezone ? (
          <Button
            label={t("settings.useDeviceTimezone", { timezone: device })}
            variant="secondary"
            onPress={() => update.mutate({ timezone: device })}
            disabled={update.isPending}
          />
        ) : null}
      </Section>

      <Section title={t("settings.notifications")}>
        {toggle("notify_streak_reminder", t("settings.streakReminder"), t("settings.streakReminderHint"), "flame")}
        {toggle("notify_challenges", t("settings.challengeAlerts"), t("settings.challengeAlertsHint"), "flag")}
        <AppText variant="caption" color="textMuted">
          {t("settings.notificationsNote")}
        </AppText>
      </Section>

      <Section title={t("settings.privacy")}>
        {toggle("profile_public", t("settings.publicProfile"), t("settings.publicProfileHint"), "eye")}
      </Section>

      <Section title={t("settings.account")}>
        <Button label={t("settings.logout")} variant="danger" onPress={() => void signOut()} />
      </Section>
    </>
  );
}

/** Configuración (CLAUDE.md 1.6): preferencias, notificaciones, privacidad y cerrar sesión. */
export function SettingsView() {
  const { t } = useTranslation();
  const theme = useTheme();
  const me = useCurrentUser();

  return (
    <Screen scroll>
      {me.isPending ? (
        <ActivityIndicator color={theme.colors.primary} accessibilityLabel={t("profile.loading")} />
      ) : me.isError ? (
        <View style={{ gap: theme.spacing.md }}>
          <AppText color="error" accessibilityRole="alert">
            {errorMessage(me.error)}
          </AppText>
          <Button label={t("common.retry")} variant="secondary" onPress={() => void me.refetch()} />
        </View>
      ) : (
        <SettingsForm user={me.data} />
      )}
    </Screen>
  );
}
