import { useReminders } from "@/hooks/use-reminders";

/** Programa los avisos de racha y desafíos mientras hay sesión. No dibuja nada. */
export function RemindersManager() {
  useReminders();
  return null;
}
