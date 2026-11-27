import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { CURRENT_USER_QUERY_KEY } from "@/hooks/use-current-user";
import { type Shop, type ShopItem, shopService } from "@/services/shop-service";

export const SHOP_QUERY_KEY = ["shop"] as const;

/** La tienda y la acción de comprar; al comprar se actualizan monedas y energía. */
export function useShop() {
  const queryClient = useQueryClient();
  const shop = useQuery({ queryKey: SHOP_QUERY_KEY, queryFn: shopService.get });
  const buy = useMutation({
    mutationFn: (itemId: ShopItem["id"]) => shopService.buy(itemId),
    onSuccess: (updated: Shop) => {
      queryClient.setQueryData(SHOP_QUERY_KEY, updated);
      void queryClient.invalidateQueries({ queryKey: CURRENT_USER_QUERY_KEY });
    },
  });
  return { shop, buy };
}
