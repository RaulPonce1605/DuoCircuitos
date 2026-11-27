import i18n from "@/i18n";
import es from "@/i18n/es.json";

type KnownTier = Exclude<keyof typeof es.leagues.tiers, "unknown">;

function isKnownTier(id: string): id is KnownTier {
  return id !== "unknown" && Object.prototype.hasOwnProperty.call(es.leagues.tiers, id);
}

/** Nombre del nivel de liga. Si el backend agrega uno que la app no conoce: "Nivel 6". */
export function tierName(tierId: string, tier: number): string {
  return isKnownTier(tierId) ? i18n.t(`leagues.tiers.${tierId}`) : i18n.t("leagues.tiers.unknown", { level: tier + 1 });
}
