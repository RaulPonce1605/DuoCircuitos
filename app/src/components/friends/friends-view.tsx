import Ionicons from "@expo/vector-icons/Ionicons";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { ActivityIndicator, View } from "react-native";

import { tierName } from "@/components/leagues/tier-name";
import { AppText, Button, Card, Screen, TextField } from "@/components/ui";
import { useFriends, useToggleFollow, useUserSearch } from "@/hooks/use-friends";
import { useTheme } from "@/hooks/use-theme";
import { errorMessage } from "@/i18n/error-message";
import type { UserCard } from "@/services/social-service";

function PersonRow({ card }: { card: UserCard }) {
  const { t } = useTranslation();
  const theme = useTheme();
  const toggle = useToggleFollow();
  const name = card.display_name ?? t("leagues.anonymous");
  const badge = card.is_following && card.follows_me ? t("friends.mutual") : card.follows_me ? t("friends.followsYou") : null;
  return (
    <View
      testID={`person-${card.id}`}
      style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.md, paddingVertical: theme.spacing.xs }}
    >
      <Ionicons name="person-circle" size={theme.sizes.iconLg} color={theme.colors.primary} />
      <View style={{ flex: 1, gap: theme.spacing.xxs }}>
        <AppText variant="bodyStrong">{name}</AppText>
        <AppText variant="caption" color="textMuted">
          {t("friends.stats", { xp: card.xp_total, streak: card.streak, tier: tierName(card.league_tier_id, card.league_tier) })}
        </AppText>
        {badge ? (
          <AppText variant="caption" color="accent">
            {badge}
          </AppText>
        ) : null}
      </View>
      {/* A un perfil privado (sin nombre) no se le puede seguir. */}
      {card.display_name !== null || card.is_following ? (
        <Button
          label={card.is_following ? t("friends.unfollow") : t("friends.follow")}
          variant={card.is_following ? "secondary" : "primary"}
          fullWidth={false}
          onPress={() => toggle.mutate(card)}
          loading={toggle.isPending}
        />
      ) : null}
    </View>
  );
}

function PeopleList({ title, people, empty }: { title: string; people: UserCard[]; empty: string }) {
  const theme = useTheme();
  return (
    <Card style={{ gap: theme.spacing.xs }}>
      <AppText variant="subtitle" accessibilityRole="header">
        {title}
      </AppText>
      {people.length === 0 ? <AppText color="textMuted">{empty}</AppText> : null}
      {people.map((card) => (
        <PersonRow key={card.id} card={card} />
      ))}
    </Card>
  );
}

/** Amigos y seguidores: buscar perfiles públicos y seguirlos. */
export function FriendsView() {
  const { t } = useTranslation();
  const theme = useTheme();
  const [query, setQuery] = useState("");
  const friends = useFriends();
  const search = useUserSearch(query);

  return (
    <Screen scroll>
      <TextField
        label={t("friends.searchLabel")}
        hint={t("friends.searchHint")}
        value={query}
        onChangeText={setQuery}
        maxLength={50}
        autoCapitalize="words"
      />
      {search.isFetching ? <ActivityIndicator color={theme.colors.primary} /> : null}
      {search.data ? (
        <Card style={{ gap: theme.spacing.xs }}>
          {search.data.length === 0 ? <AppText color="textMuted">{t("friends.noResults")}</AppText> : null}
          {search.data.map((card) => (
            <PersonRow key={card.id} card={card} />
          ))}
        </Card>
      ) : null}

      {friends.isPending ? (
        <ActivityIndicator color={theme.colors.primary} accessibilityLabel={t("friends.loading")} />
      ) : friends.isError ? (
        <View style={{ gap: theme.spacing.md }}>
          <AppText color="error" accessibilityRole="alert">
            {errorMessage(friends.error)}
          </AppText>
          <Button label={t("common.retry")} variant="secondary" onPress={() => void friends.refetch()} />
        </View>
      ) : (
        <>
          <PeopleList title={t("friends.following")} people={friends.data.following} empty={t("friends.emptyFollowing")} />
          <PeopleList title={t("friends.followers")} people={friends.data.followers} empty={t("friends.emptyFollowers")} />
        </>
      )}
    </Screen>
  );
}
