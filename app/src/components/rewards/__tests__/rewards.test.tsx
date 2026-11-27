import { fireEvent, render, screen } from "@testing-library/react-native";

import { AppProviders } from "@/components/app-providers";
import { ChestView } from "@/components/rewards/chest-view";
import { StreakView } from "@/components/rewards/streak-view";
import es from "@/i18n/es.json";
import { ApiError } from "@/services/api-client";
import type { LessonSummary } from "@/services/lesson-service";
import type { Chest } from "@/services/rewards-service";

const mockOpenChest = jest.fn();
const mockOpenNodeChest = jest.fn();
const mockSummary = jest.fn();
const mockUseCurrentUser = jest.fn();

jest.mock("@/services/rewards-service", () => ({
  rewardsService: {
    openChest: (...args: unknown[]) => mockOpenChest(...args),
    openNodeChest: (...args: unknown[]) => mockOpenNodeChest(...args),
  },
}));
jest.mock("@/services/lesson-service", () => ({
  lessonService: { summary: (...args: unknown[]) => mockSummary(...args) },
}));
jest.mock("@/hooks/use-current-user", () => ({
  CURRENT_USER_QUERY_KEY: ["me"],
  useCurrentUser: () => mockUseCurrentUser(),
}));

const CHEST: Chest = {
  id: "c-1",
  source: "lesson",
  reward: { xp: 7, energy: 1 },
  new_badges: [{ achievement_id: "chests", level: 1, threshold: 1, earned_at: "2026-11-26T12:00:00Z" }],
  energy: { current: 5, max: 5, next_refill_at: null },
};

beforeEach(() => {
  jest.clearAllMocks();
  mockUseCurrentUser.mockReturnValue({ data: { streak_longest: 9 } });
});

describe("ChestView", () => {
  it("pulsa para abrir y muestra el premio del backend", async () => {
    mockOpenChest.mockResolvedValue(CHEST);
    const onContinue = jest.fn();
    await render(
      <AppProviders>
        <ChestView target={{ kind: "attempt", chestId: "c-1" }} onContinue={onContinue} />
      </AppProviders>,
    );

    expect(screen.getByText(es.chest.tapToOpen)).toBeOnTheScreen();
    await fireEvent.press(screen.getByRole("button", { name: es.chest.open }));

    expect(mockOpenChest).toHaveBeenCalledWith("c-1");
    expect(await screen.findByText("+7 EXP")).toBeOnTheScreen();
    expect(screen.getByText("+1 de energía")).toBeOnTheScreen();
    expect(screen.getByText("Cazatesoros: Bronce")).toBeOnTheScreen();
    await fireEvent.press(screen.getByRole("button", { name: es.chest.continue }));
    expect(onContinue).toHaveBeenCalled();
  });

  it("el cofre del camino se abre por su nodo", async () => {
    mockOpenNodeChest.mockResolvedValue({ ...CHEST, source: "node", reward: { xp: 20, energy: 0 }, new_badges: [] });
    await render(
      <AppProviders>
        <ChestView target={{ kind: "node", nodeKey: "u01:chest:1" }} onContinue={jest.fn()} />
      </AppProviders>,
    );

    expect(screen.getByText(es.chest.nodeTitle)).toBeOnTheScreen();
    await fireEvent.press(screen.getByRole("button", { name: es.chest.open }));

    expect(mockOpenNodeChest).toHaveBeenCalledWith("u01:chest:1");
    expect(await screen.findByText("+20 EXP")).toBeOnTheScreen();
    expect(screen.getByText(es.chest.noEnergy)).toBeOnTheScreen();
  });

  it("si falla lo dice y deja continuar", async () => {
    mockOpenNodeChest.mockRejectedValue(new ApiError("node_locked", 409));
    await render(
      <AppProviders>
        <ChestView target={{ kind: "node", nodeKey: "u01:chest:1" }} onContinue={jest.fn()} />
      </AppProviders>,
    );

    await fireEvent.press(screen.getByRole("button", { name: es.chest.open }));

    expect(await screen.findByRole("alert")).toHaveTextContent(es.errors.node_locked);
    expect(screen.getByRole("button", { name: es.chest.continue })).toBeOnTheScreen();
  });
});

const SUMMARY: LessonSummary = {
  attempt_id: "a-1",
  node: { key: "ohm-01", type: "lesson", unit_title: "Ley de Ohm" },
  lesson: { slug: "ohm-01", title: "Voltaje, corriente y resistencia" },
  exercise_count: 5,
  first_try_correct: 5,
  accuracy: 100,
  xp_awarded: 55,
  concepts: [],
  streak: 4,
  streak_extended: true,
  chest_id: "c-1",
  new_badges: [],
};

async function renderStreak(summary: LessonSummary) {
  mockSummary.mockResolvedValue(summary);
  const onContinue = jest.fn();
  await render(
    <AppProviders>
      <StreakView attemptId="a-1" onContinue={onContinue} />
    </AppProviders>,
  );
  return onContinue;
}

describe("StreakView", () => {
  it("celebra que la racha creció", async () => {
    const onContinue = await renderStreak(SUMMARY);

    expect(await screen.findByText("4 días de racha")).toBeOnTheScreen();
    expect(screen.getByText(es.streak.up)).toBeOnTheScreen();
    expect(screen.getByText("Tu mejor racha: 9")).toBeOnTheScreen();
    await fireEvent.press(screen.getByRole("button", { name: es.streak.continue }));
    expect(onContinue).toHaveBeenCalled();
  });

  it("si ya había practicado hoy dice que se mantiene", async () => {
    await renderStreak({ ...SUMMARY, streak_extended: false });
    expect(await screen.findByText(es.streak.kept)).toBeOnTheScreen();
  });

  it("el primer día dice que empezó una racha, en singular", async () => {
    await renderStreak({ ...SUMMARY, streak: 1 });
    expect(await screen.findByText("1 día de racha")).toBeOnTheScreen();
    expect(screen.getByText(es.streak.start)).toBeOnTheScreen();
  });
});
