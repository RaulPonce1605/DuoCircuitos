import { fireEvent, render, screen } from "@testing-library/react-native";

import { AppProviders } from "@/components/app-providers";
import { ChallengesView } from "@/components/challenges/challenges-view";
import es from "@/i18n/es.json";
import { ApiError } from "@/services/api-client";
import type { Challenges } from "@/services/challenges-service";

const mockList = jest.fn();

jest.mock("@/services/challenges-service", () => ({
  challengesService: { list: (...args: unknown[]) => mockList(...args) },
}));

const NOW = new Date("2026-11-26T18:00:00Z").getTime();

const DATA: Challenges = {
  daily: [
    {
      id: "d-1",
      period: "daily",
      kind: "complete_lessons",
      goal: 2,
      progress: 1,
      reward_xp: 10,
      reward_coins: 10,
      completed_at: null,
    },
    {
      id: "d-2",
      period: "daily",
      kind: "perfect_lessons",
      goal: 1,
      progress: 1,
      reward_xp: 15,
      reward_coins: 10,
      completed_at: "2026-11-26T17:00:00Z",
    },
  ],
  monthly: [
    { id: "m-1", period: "monthly", kind: "earn_xp", goal: 1500, progress: 300, reward_xp: 100, reward_coins: 10, completed_at: null },
  ],
  daily_ends_at: "2026-11-27T06:00:00Z",
  monthly_ends_at: "2026-12-01T06:00:00Z",
};

beforeEach(() => {
  jest.clearAllMocks();
  jest.useFakeTimers({ now: NOW });
});

afterEach(() => {
  jest.useRealTimers();
});

async function renderView() {
  await render(
    <AppProviders>
      <ChallengesView />
    </AppProviders>,
  );
}

describe("ChallengesView", () => {
  it("muestra los desafíos de hoy y del mes con su avance", async () => {
    mockList.mockResolvedValue(DATA);
    await renderView();

    expect(await screen.findByText(es.challenges.daily)).toBeOnTheScreen();
    expect(screen.getByText("Cambian en 12 horas")).toBeOnTheScreen();
    expect(screen.getByText("Termina en 5 días")).toBeOnTheScreen();
    expect(screen.getByText("Termina 2 lecciones")).toBeOnTheScreen();
    expect(screen.getByText("1 de 2")).toBeOnTheScreen();
    expect(screen.getByLabelText("Progreso: Termina 2 lecciones")).toHaveAccessibilityValue({ now: 50 });
    expect(screen.getByText("Termina 1 lección sin errores")).toBeOnTheScreen();
    expect(screen.getByText(es.challenges.done)).toBeOnTheScreen();
    expect(screen.getByText("Gana 1500 EXP")).toBeOnTheScreen();
    expect(screen.getByText("+100 EXP")).toBeOnTheScreen();
  });

  it("muestra el error y deja reintentar", async () => {
    mockList.mockRejectedValueOnce(new ApiError("network", 0)).mockResolvedValue(DATA);
    await renderView();

    expect(await screen.findByRole("alert")).toHaveTextContent(es.errors.network);
    await fireEvent.press(screen.getByRole("button", { name: es.common.retry }));
    expect(await screen.findByText(es.challenges.daily)).toBeOnTheScreen();
  });

  it("sin desafíos diarios lo dice", async () => {
    mockList.mockResolvedValue({ ...DATA, daily: [] });
    await renderView();

    expect(await screen.findByText(es.challenges.empty)).toBeOnTheScreen();
  });
});
