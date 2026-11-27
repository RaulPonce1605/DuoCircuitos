import type { components } from "@/api/schema";
import { api } from "@/services/api-client";
import { authService } from "@/services/auth-service";

export type Shop = components["schemas"]["ShopRead"];
export type ShopItem = components["schemas"]["ShopItemRead"];

/** Precios y reglas de la tienda son del backend; aquí solo se leen y se piden compras. */
export const shopService = {
  get: (): Promise<Shop> => authService.authed(() => api.GET("/shop")),

  buy: (itemId: ShopItem["id"]): Promise<Shop> =>
    authService.authed(() => api.POST("/shop/items/{item_id}/buy", { params: { path: { item_id: itemId } } })),
};
