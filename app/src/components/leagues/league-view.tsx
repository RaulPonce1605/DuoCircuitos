import Ionicons from "@expo/vector-icons/Ionicons";
import { useTranslation } from "react-i18next";
import { ActivityIndicator, View } from "react-native";

import { tierName } from "@/components/leagues/tier-name";
import { AppText, Button, Card } from "@/components/ui";
import { useLeague } from "@/hooks/use-league";
import { useNow } from "@/hooks/use-now";
import { useTheme } from "@/hooks/use-theme";
import { errorMessage } from "@/i18n/error-message";
import type { League, LeagueMember } from "@/services/leagues-service";
import type { ColorTokens } from "@/theme";

const HOUR_MS = 3_600_000;
const RANK_WIDTH = 32;

function timeLeft(endsAt: string, now: number): { key: "leagues.endsIn" | "leagues.endsInDays"; count: number } {
  const hours = Math.max(1, Math.ceil((new Date(endsAt).getTime() - now) / HOUR_MS));
  return hours > 48 ? { key: "leagues.endsInDays", count: Math.ceil(hours / 24) } : { key: "leagues.endsIn", count: hours };
}

function MemberRow({ member }: { member: LeagueMember }) {
  const { t } = useTranslation();
  const theme = useTheme();
  const name = member.display_name ?? t("leagues.anonymous");
  const label = member.is_me ? t("leagues.you", { name }) : name;
  const zoneColor: keyof ColorTokens | null =
    member.zone === "promotion" ? "success" : member.zone === "demotion" ? "error" : null;
  const xp = t("leagues.xp", { count: member.xp });
  return (
    <View
      testID={`league-member-${member.rank}`}
      accessible
      accessibilityLabel={`${t("leagues.rankLabel", { rank: member.rank, name: label, xp })}${
        member.zone ? `. ${t(member.zone === "promotion" ? "leagues.promotionZone" : "leagues.demotionZone")}` : ""
      }`}
      style={{
        flexDirection: "row",
        alignItems: "center",
        gap: theme.spacing.md,
        paddingVertical: theme.spacing.sm,
        paddingHorizontal: theme.spacing.sm,
        borderRadius: theme.radii.sm,
        backgroundColor: member.is_me ? theme.colors.primarySoft : "transparent",
      }}
    >
      <AppText variant="bodyStrong" color={zoneColor ?? "textMuted"} style={{ width: RANK_WIDTH }} align="center">
        {String(member.rank)}
      </AppText>
      <AppText variant={member.is_me ? "bodyStrong" : "body"} style={{ flex: 1 }}>
        {label}
      </AppText>
      <AppText variant="bodyStrong" color="xp">
        {xp}
      </AppText>
      {zoneColor ? (
        <Ionicons
          name={member.zone === "promotion" ? "arrow-up" : "arrow-down"}
          size={theme.sizes.iconSm}
          color={theme.colors[zoneColor]}
        />
      ) : (
        <View style={{ width: theme.sizes.iconSm }} />
      )}
    </View>
  );
}

function LastResult({ league }: { league: League }) {
  const { t } = useTranslation();
  const theme = useTheme();
  const last = league.last_result;
  if (!last) {
    return null;
  }
  const tone: keyof ColorTokens = last.result === "promoted" ? "success" : last.result === "demoted" ? "error" : "primary";
  return (
    <Card testID="league-last-result" borderTone={tone} style={{ flexDirection: "row", gap: theme.spacing.md, alignItems: "center" }}>
      <Ionicons
        name={last.result === "promoted" ? "trending-up" : last.result === "demoted" ? "trending-down" : "remove"}
        size={theme.sizes.iconLg}
        color={theme.colors[tone]}
      />
      <AppText style={{ flex: 1 }} accessibilityLiveRegion="polite">
        {t(`leagues.result.${last.result}`, { rank: last.final_rank, xp: last.final_xp })}
      </AppText>
    </Card>
  );
}

/** Pestaña Ligas: nivel, tiempo restante y ranking de la semana (todo del backend). */
export function LeagueView() {
  const { t } = useTranslation();
  const theme = useTheme();
  const query = useLeague();
  const now = useNow();

  if (query.isPending) {
    return (
      <ActivityIndicator
        color={theme.colors.primary}
        accessibilityLabel={t("leagues.loading")}
        style={{ marginTop: theme.spacing.xxl }}
      />
    );
  }
  if (query.isError) {
    return (
      <View style={{ gap: theme.spacing.md }}>
        <AppText color="error" accessibilityRole="alert">
          {errorMessage(query.error)}
        </AppText>
        <Button label={t("common.retry")} variant="secondary" onPress={() => void query.refetch()} />
      </View>
    );
  }

  const league = query.data;
  const left = timeLeft(league.ends_at, now);
  return (
    <View style={{ gap: theme.spacing.lg }}>
      <View style={{ alignItems: "center", gap: theme.spacing.xs }}>
        <Ionicons name="podium" size={theme.sizes.iconLg * 2} color={theme.colors.accent} />
        <AppText variant="title" align="center" accessibilityRole="header">
          {t("leagues.tierLabel", { tier: tierName(league.tier_id, league.tier) })}
        </AppText>
        <AppText color="textMuted" align="center">
          {t(left.key, { count: left.count })}
        </AppText>
      </View>

      <LastResult league={league} />

      {league.joined ? (
        <Card style={{ gap: theme.spacing.xxs }}>
          {league.members.map((member) => (
            <MemberRow key={`${member.rank}-${member.is_me}`} member={member} />
          ))}
        </Card>
      ) : (
        <Card style={{ gap: theme.spacing.sm, alignItems: "center" }}>
          <AppText variant="subtitle" align="center">
            {t("leagues.notJoinedTitle")}
          </AppText>
          <AppText color="textMuted" align="center">
            {t("leagues.notJoined")}
          </AppText>
        </Card>
      )}
      <AppText variant="caption" color="textMuted" align="center">
        {t("leagues.rules")}
      </AppText>
    </View>
  );
}
