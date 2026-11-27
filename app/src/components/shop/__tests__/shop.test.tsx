import { fireEvent, render, screen } from "@testing-library/react-native";

import { AppProviders } from "@/components/app-providers";
import { ShopView } from "@/components/shop/shop-view";
import es from "@/i18n/es.json";
import { ApiError } from "@/services/api-client";
import type { Shop } from "@/services/shop-service";

const mockGet = jest.fn();
const mockBuy = jest.fn();

jest.mock("@/services/shop-service", () => ({
  shopService: {
    get: (...args: unknown[]) => mockGet(...args),
    buy: (...args: unknown[]) => mockBuy(...args),
  },
}));

const SHOP: Shop = {
  coins: 200,
  streak_freezes: 1,
  streak_freeze_max: 2,
  energy: { current: 2, max: 5, next_refill_at: "2099-01-01T00:00:00Z" },
  items: [
    { id: "energy_refill", price: 60, unavailable_reason: null },
    { id: "streak_freeze", price: 150, unavailable_reason: null },
  ],
};

beforeEach(() => {
  jest.clearAllMocks();
  mockGet.mockResolvedValue(SHOP);
});

async function renderShop() {
  await render(
    <AppProviders>
      <ShopView />
    </AppProviders>,
  );
  await screen.findByText(es.shop.items.energy_refill.title);
}

describe("ShopView", () => {
  it("muestra monedas, artículos y cuántos protectores tiene", async () => {
    await renderShop();

    expect(screen.getByLabelText("200 monedas")).toBeOnTheScreen();
    expect(screen.getByText("Tienes 1 de 2")).toBeOnTheScreen();
    expect(screen.getByRole("button", { name: "Comprar por 60" })).toBeEnabled();
  });

  it("compra y muestra lo que devuelve el backend", async () => {
    mockBuy.mockResolvedValue({
      ...SHOP,
      coins: 50,
      streak_freezes: 2,
      items: [
        { id: "energy_refill", price: 60, unavailable_reason: "not_enough_coins" },
        { id: "streak_freeze", price: 150, unavailable_reason: "streak_freeze_limit" },
      ],
    });
    await renderShop();

    await fireEvent.press(screen.getByRole("button", { name: "Comprar por 150" }));

    expect(mockBuy).toHaveBeenCalledWith("streak_freeze");
    expect(await screen.findByText(es.shop.bought)).toBeOnTheScreen();
    expect(screen.getByLabelText("50 monedas")).toBeOnTheScreen();
    expect(screen.getByText(es.shop.unavailable.streak_freeze_limit)).toBeOnTheScreen();
    expect(screen.getByRole("button", { name: "Comprar por 150" })).toBeDisabled();
  });

  it("traduce el error del backend", async () => {
    mockBuy.mockRejectedValue(new ApiError("not_enough_coins", 409));
    await renderShop();

    await fireEvent.press(screen.getByRole("button", { name: "Comprar por 60" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(es.errors.not_enough_coins);
  });
});
