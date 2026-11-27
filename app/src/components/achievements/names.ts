import i18n from "@/i18n";
import es from "@/i18n/es.json";
import type { Badge } from "@/services/rewards-service";
import type { ColorTokens } from "@/theme";

type KnownAchievement = keyof typeof es.achievements.items;
type KnownLevel = Exclude<keyof typeof es.badges.level, "other">;

function isKnownAchievement(id: string): id is KnownAchievement {
  return Object.prototype.hasOwnProperty.call(es.achievements.items, id);
}

function isKnownLevel(level: string): level is KnownLevel {
  return level !== "other" && Object.prototype.hasOwnProperty.call(es.badges.level, level);
}

/** Nombre de un logro. Si el backend agrega uno que la app aún no conoce, usa un nombre genérico. */
export function achievementTitle(id: string): string {
  return isKnownAchievement(id) ? i18n.t(`achievements.items.${id}.title`) : i18n.t("achievements.unknown");
}

/** "Completa 5 lecciones". */
export function achievementGoal(id: string, threshold: number): string {
  return isKnownAchievement(id) ? i18n.t(`achievements.items.${id}.goal`, { count: threshold }) : String(threshold);
}

export function levelName(level: number): string {
  const key = String(level);
  return isKnownLevel(key) ? i18n.t(`badges.level.${key}`) : i18n.t("badges.level.other", { level });
}

/** "Constancia: Plata". */
export function badgeName(badge: Pick<Badge, "achievement_id" | "level">): string {
  return i18n.t("badges.name", { achievement: achievementTitle(badge.achievement_id), level: levelName(badge.level) });
}

/** Color de la medalla según el nivel: cobre, gris y dorado (tokens del tema). */
export function levelColor(level: number): keyof ColorTokens {
  if (level <= 1) {
    return "accent";
  }
  return level === 2 ? "textMuted" : "xp";
}
