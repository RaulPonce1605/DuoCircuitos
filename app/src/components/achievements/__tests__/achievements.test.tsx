import { fireEvent, render, screen } from "@testing-library/react-native";

import { AchievementsView } from "@/components/achievements/achievements-view";
import { BadgesView, badgeSlots } from "@/components/achievements/badges-view";
import { AppProviders } from "@/components/app-providers";
import { MoreMenu } from "@/components/more/more-menu";
import es from "@/i18n/es.json";
import type { Achievements } from "@/services/rewards-service";

const mockAchievements = jest.fn();
const mockPush = jest.fn();

jest.mock("@/services/rewards-service", () => ({
  rewardsService: { achievements: (...args: unknown[]) => mockAchievements(...args) },
}));
jest.mock("expo-router", () => ({ useRouter: () => ({ push: mockPush }) }));

const DATA: Achievements = {
  achievements: [
    { id: "lessons", metric: "lessons_completed", value: 3, thresholds: [1, 5, 10], level: 1, next_threshold: 5 },
    { id: "streak", metric: "streak_longest", value: 40, thresholds: [3, 7, 30], level: 3, next_threshold: null },
    { id: "nuevo", metric: "xp_total", value: 0, thresholds: [50], level: 0, next_threshold: 50 },
  ],
  badges: [
    { achievement_id: "streak", level: 3, threshold: 30, earned_at: "2026-11-20T12:00:00Z" },
    { achievement_id: "streak", level: 2, threshold: 7, earned_at: "2026-11-10T12:00:00Z" },
    { achievement_id: "streak", level: 1, threshold: 3, earned_at: "2026-11-05T12:00:00Z" },
    { achievement_id: "lessons", level: 1, threshold: 1, earned_at: "2026-11-01T12:00:00Z" },
  ],
};

beforeEach(() => {
  jest.clearAllMocks();
  mockAchievements.mockResolvedValue(DATA);
});

describe("AchievementsView", () => {
  it("muestra el nivel y lo que falta para el siguiente", async () => {
    await render(
      <AppProviders>
        <AchievementsView />
      </AppProviders>,
    );

    expect(await screen.findByText("Aprendiz de circuitos")).toBeOnTheScreen();
    expect(screen.getByText("Completa 5 lecciones")).toBeOnTheScreen();
    expect(screen.getByText("3 de 5")).toBeOnTheScreen();
    // Del umbral 1 al 5, con 3: va a la mitad del nivel.
    expect(screen.getByLabelText("Progreso de Aprendiz de circuitos")).toHaveAccessibilityValue({ now: 50 });
    expect(screen.getByText(es.achievements.completed)).toBeOnTheScreen();
    // Un logro que la app aún no conoce sale con nombre genérico.
    expect(screen.getByText(es.achievements.unknown)).toBeOnTheScreen();
  });
});

describe("BadgesView", () => {
  it("arma una medalla por nivel y cuenta las ganadas", () => {
    const slots = badgeSlots(DATA);
    expect(slots).toHaveLength(7);
    expect(slots.filter((slot) => slot.earned)).toHaveLength(4);
  });

  it("muestra ganadas y bloqueadas", async () => {
    await render(
      <AppProviders>
        <BadgesView />
      </AppProviders>,
    );

    expect(await screen.findByText("4 de 7 ganadas")).toBeOnTheScreen();
    expect(screen.getByText("Constancia: Oro")).toBeOnTheScreen();
    expect(screen.getByTestId("badge-lessons-2")).toHaveTextContent(new RegExp(es.badges.locked));
  });
});

describe("MoreMenu", () => {
  it("lleva a logros, medallas y configuración", async () => {
    await render(
      <AppProviders>
        <MoreMenu />
      </AppProviders>,
    );

    await fireEvent.press(screen.getByRole("button", { name: es.more.friends }));
    await fireEvent.press(screen.getByRole("button", { name: es.more.achievements }));
    await fireEvent.press(screen.getByRole("button", { name: es.more.badges }));
    await fireEvent.press(screen.getByRole("button", { name: es.more.shop }));
    await fireEvent.press(screen.getByRole("button", { name: es.more.settings }));
    expect(mockPush.mock.calls).toEqual([["/amigos"], ["/logros"], ["/medallas"], ["/tienda"], ["/configuracion"]]);
  });
});
