import { render, screen } from "@testing-library/react-native";

import { AppProviders } from "@/components/app-providers";
import { LeagueView } from "@/components/leagues/league-view";
import es from "@/i18n/es.json";
import { ApiError } from "@/services/api-client";
import type { League } from "@/services/leagues-service";

const mockCurrent = jest.fn();

jest.mock("@/services/leagues-service", () => ({
  leaguesService: { current: (...args: unknown[]) => mockCurrent(...args) },
}));

const NOW = new Date("2026-11-26T18:00:00Z").getTime();

const LEAGUE: League = {
  tier: 1,
  tier_id: "capacitor",
  tiers: ["resistor", "capacitor", "inductor"],
  week_start: "2026-11-23",
  ends_at: "2026-11-30T00:00:00Z",
  joined: true,
  group_size: 20,
  members: [
    { rank: 1, display_name: "Luis", xp: 120, is_me: false, zone: "promotion" },
    { rank: 2, display_name: "Ana", xp: 80, is_me: true, zone: null },
    { rank: 3, display_name: null, xp: 0, is_me: false, zone: "demotion" },
  ],
  last_result: { week_start: "2026-11-16", tier: 0, result: "promoted", final_rank: 2, final_xp: 310 },
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
      <LeagueView />
    </AppProviders>,
  );
}

describe("LeagueView", () => {
  it("muestra nivel, tiempo restante, ranking con zonas y el resultado anterior", async () => {
    mockCurrent.mockResolvedValue(LEAGUE);
    await renderView();

    expect(await screen.findByRole("header", { name: "Liga Capacitor" })).toBeOnTheScreen();
    expect(screen.getByText("Termina en 4 días")).toBeOnTheScreen();
    expect(screen.getByLabelText("Lugar 1: Luis, 120 EXP. Zona de ascenso")).toBeOnTheScreen();
    expect(screen.getByLabelText("Lugar 2: Ana (tú), 80 EXP")).toBeOnTheScreen();
    expect(screen.getByLabelText("Lugar 3: Alumno anónimo, 0 EXP. Zona de descenso")).toBeOnTheScreen();
    expect(screen.getByText("¡Subiste de liga! Quedaste en el lugar 2 con 310 EXP.")).toBeOnTheScreen();
  });

  it("si aún no entra a la liga lo invita a terminar una lección", async () => {
    mockCurrent.mockResolvedValue({ ...LEAGUE, joined: false, members: [], last_result: null });
    await renderView();

    expect(await screen.findByText(es.leagues.notJoinedTitle)).toBeOnTheScreen();
    expect(screen.queryByTestId("league-last-result")).toBeNull();
  });

  it("un nivel que la app no conoce se muestra con su número", async () => {
    mockCurrent.mockResolvedValue({ ...LEAGUE, tier: 5, tier_id: "nuevo" });
    await renderView();

    expect(await screen.findByRole("header", { name: "Liga Nivel 6" })).toBeOnTheScreen();
  });

  it("muestra el error traducido", async () => {
    mockCurrent.mockRejectedValue(new ApiError("network", 0));
    await renderView();

    expect(await screen.findByRole("alert")).toHaveTextContent(es.errors.network);
  });
});
