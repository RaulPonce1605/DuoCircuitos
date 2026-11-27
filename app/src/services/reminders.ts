import * as Notifications from "expo-notifications";
import { Platform } from "react-native";

/** Horas locales de los avisos (docs/diseno/notificaciones.md). */
export const STREAK_REMINDER_HOUR = 19;
export const CHALLENGES_REMINDER_HOUR = 9;

export type ReminderPlan = {
  streak: { at: Date; title: string; body: string } | null;
  challenges: { hour: number; title: string; body: string } | null;
};

export type PermissionStatus = "granted" | "denied" | "undetermined" | "unsupported";

/** Las programaciones se encadenan: dos cambios seguidos no deben mezclar sus avisos. */
let queue: Promise<void> = Promise.resolve();

/** El próximo recordatorio de racha: hoy a la hora fija si aún no practica, si no, mañana. */
export function nextStreakReminder(now: Date, practicedToday: boolean): Date {
  const at = new Date(now);
  at.setHours(STREAK_REMINDER_HOUR, 0, 0, 0);
  if (practicedToday || at.getTime() <= now.getTime()) {
    at.setDate(at.getDate() + 1);
  }
  return at;
}

/**
 * Notificaciones locales: se programan en el teléfono, sin servidor de push. En la web no hay
 * (`unsupported`). Los textos llegan ya traducidos.
 */
export const remindersService = {
  supported: (): boolean => Platform.OS !== "web",

  async permission(ask: boolean): Promise<PermissionStatus> {
    if (Platform.OS === "web") {
      return "unsupported";
    }
    try {
      const current = await Notifications.getPermissionsAsync();
      if (current.granted || !ask || !current.canAskAgain) {
        return current.granted ? "granted" : current.canAskAgain ? "undetermined" : "denied";
      }
      const asked = await Notifications.requestPermissionsAsync();
      return asked.granted ? "granted" : "denied";
    } catch {
      return "unsupported"; // sin el módulo nativo (por ejemplo, en algunos simuladores)
    }
  },

  /** Reemplaza todos los avisos programados por los del plan (uno a la vez, en orden). */
  apply(plan: ReminderPlan): Promise<void> {
    queue = queue.then(() => applyNow(plan)).catch(() => undefined);
    return queue;
  },

  clear(): Promise<void> {
    queue = queue
      .then(() => (Platform.OS === "web" ? undefined : Notifications.cancelAllScheduledNotificationsAsync()))
      .catch(() => undefined);
    return queue;
  },
};

async function applyNow(plan: ReminderPlan): Promise<void> {
  if (Platform.OS === "web") {
    return;
  }
  await Notifications.cancelAllScheduledNotificationsAsync();
  if (plan.streak) {
    await Notifications.scheduleNotificationAsync({
      content: { title: plan.streak.title, body: plan.streak.body },
      trigger: { type: Notifications.SchedulableTriggerInputTypes.DATE, date: plan.streak.at },
    });
  }
  if (plan.challenges) {
    await Notifications.scheduleNotificationAsync({
      content: { title: plan.challenges.title, body: plan.challenges.body },
      trigger: {
        type: Notifications.SchedulableTriggerInputTypes.DAILY,
        hour: plan.challenges.hour,
        minute: 0,
      },
    });
  }
}
