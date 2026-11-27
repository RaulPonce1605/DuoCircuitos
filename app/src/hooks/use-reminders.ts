import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { useCurrentUser } from "@/hooks/use-current-user";
import {
  CHALLENGES_REMINDER_HOUR,
  nextStreakReminder,
  type PermissionStatus,
  remindersService,
} from "@/services/reminders";

/**
 * Mantiene programados los avisos según la Configuración del alumno y si ya practicó hoy.
 * Se monta una vez dentro de la sesión; cada cambio del usuario (terminar una lección, cambiar
 * un interruptor) vuelve a programarlos.
 */
export function useReminders(): PermissionStatus | null {
  const { t } = useTranslation();
  const me = useCurrentUser();
  const [permission, setPermission] = useState<PermissionStatus | null>(null);
  const user = me.data;

  useEffect(() => {
    if (!user || !remindersService.supported()) {
      return;
    }
    const wantsAny = user.notify_streak_reminder || user.notify_challenges;
    let cancelled = false;
    void (async () => {
      const status = await remindersService.permission(wantsAny);
      if (cancelled) {
        return;
      }
      setPermission(status);
      if (status !== "granted" || !wantsAny) {
        await remindersService.clear();
        return;
      }
      const streak = user.streak_current;
      await remindersService.apply({
        streak: user.notify_streak_reminder
          ? {
              at: nextStreakReminder(new Date(), user.practiced_today),
              title: t("notifications.streakTitle"),
              body: streak > 0 ? t("notifications.streakBody", { count: streak }) : t("notifications.startBody"),
            }
          : null,
        challenges: user.notify_challenges
          ? {
              hour: CHALLENGES_REMINDER_HOUR,
              title: t("notifications.challengesTitle"),
              body: t("notifications.challengesBody"),
            }
          : null,
      });
    })();
    return () => {
      cancelled = true;
    };
  }, [user, t]);

  return permission;
}

/** Solo lee el permiso del teléfono (sin pedirlo ni programar nada), para Configuración. */
export function useNotificationPermission(): PermissionStatus | null {
  const [permission, setPermission] = useState<PermissionStatus | null>(null);
  useEffect(() => {
    let cancelled = false;
    void remindersService.permission(false).then((status) => {
      if (!cancelled) {
        setPermission(status);
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);
  return permission;
}
