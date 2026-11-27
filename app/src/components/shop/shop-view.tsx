import Ionicons from "@expo/vector-icons/Ionicons";
import type { ComponentProps } from "react";
import { useTranslation } from "react-i18next";
import { ActivityIndicator, View } from "react-native";

import { AppText, Button, Card, Screen } from "@/components/ui";
import { useShop } from "@/hooks/use-shop";
import { useTheme } from "@/hooks/use-theme";
import { errorMessage } from "@/i18n/error-message";
import type { Shop, ShopItem } from "@/services/shop-service";
import type { ColorTokens } from "@/theme";

const ITEM_ICON: Record<ShopItem["id"], { icon: ComponentProps<typeof Ionicons>["name"]; color: keyof ColorTokens }> = {
  energy_refill: { icon: "battery-charging", color: "energy" },
  streak_freeze: { icon: "snow", color: "primary" },
};

function ItemCard({
  item,
  shop,
  onBuy,
  buying,
}: {
  item: ShopItem;
  shop: Shop;
  onBuy: () => void;
  buying: boolean;
}) {
  const { t } = useTranslation();
  const theme = useTheme();
  const look = ITEM_ICON[item.id];
  return (
    <Card testID={`shop-item-${item.id}`} style={{ gap: theme.spacing.sm }}>
      <View style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.md }}>
        <Ionicons name={look.icon} size={theme.sizes.iconLg} color={theme.colors[look.color]} />
        <View style={{ flex: 1, gap: theme.spacing.xxs }}>
          <AppText variant="subtitle">{t(`shop.items.${item.id}.title`)}</AppText>
          <AppText color="textMuted">{t(`shop.items.${item.id}.description`)}</AppText>
          {item.id === "streak_freeze" ? (
            <AppText variant="caption" color="textMuted">
              {t("shop.freezesOwned", { count: shop.streak_freezes, max: shop.streak_freeze_max })}
            </AppText>
          ) : null}
        </View>
      </View>
      <Button
        label={t("shop.buy", { price: item.price })}
        variant="secondary"
        onPress={onBuy}
        disabled={item.unavailable_reason !== null || buying}
        loading={buying}
        accessibilityHint={item.unavailable_reason ? t(`shop.unavailable.${item.unavailable_reason}`) : undefined}
      />
      {item.unavailable_reason ? (
        <AppText variant="caption" color="textMuted" align="center">
          {t(`shop.unavailable.${item.unavailable_reason}`)}
        </AppText>
      ) : null}
    </Card>
  );
}

/** Tienda: monedas por recargas de energía y protectores de racha (precios del backend). */
export function ShopView() {
  const { t } = useTranslation();
  const theme = useTheme();
  const { shop, buy } = useShop();

  return (
    <Screen scroll>
      {shop.isPending ? (
        <ActivityIndicator
          color={theme.colors.primary}
          accessibilityLabel={t("shop.loading")}
          style={{ marginTop: theme.spacing.xl }}
        />
      ) : shop.isError ? (
        <View style={{ gap: theme.spacing.md }}>
          <AppText color="error" accessibilityRole="alert">
            {errorMessage(shop.error)}
          </AppText>
          <Button label={t("common.retry")} variant="secondary" onPress={() => void shop.refetch()} />
        </View>
      ) : (
        <>
          <Card borderTone="coins" style={{ alignItems: "center", gap: theme.spacing.xs }}>
            <View
              accessible
              accessibilityLabel={t("shop.coins", { count: shop.data.coins })}
              style={{ flexDirection: "row", alignItems: "center", gap: theme.spacing.sm }}
            >
              <Ionicons name="logo-bitcoin" size={theme.sizes.iconLg} color={theme.colors.coins} />
              <AppText variant="title" color="coins">
                {String(shop.data.coins)}
              </AppText>
            </View>
            <AppText variant="caption" color="textMuted" align="center">
              {t("shop.howToEarn")}
            </AppText>
          </Card>
          {buy.isError ? (
            <AppText color="error" accessibilityRole="alert">
              {errorMessage(buy.error)}
            </AppText>
          ) : buy.isSuccess ? (
            <AppText color="success" accessibilityLiveRegion="polite">
              {t("shop.bought")}
            </AppText>
          ) : null}
          {shop.data.items.map((item) => (
            <ItemCard
              key={item.id}
              item={item}
              shop={shop.data}
              buying={buy.isPending && buy.variables === item.id}
              onBuy={() => buy.mutate(item.id)}
            />
          ))}
        </>
      )}
    </Screen>
  );
}
