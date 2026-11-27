import { render, screen } from "@testing-library/react-native";

import { AppProviders } from "@/components/app-providers";
import { EnergyCounter } from "@/components/gamification/energy-counter";

const NOW = new Date("2026-11-26T12:00:00Z").getTime();

beforeEach(() => {
  jest.useFakeTimers({ now: NOW });
});

afterEach(() => {
  jest.useRealTimers();
});

async function renderCounter(energy: Parameters<typeof EnergyCounter>[0]["energy"]) {
  await render(
    <AppProviders>
      <EnergyCounter energy={energy} />
    </AppProviders>,
  );
}

describe("EnergyCounter", () => {
  it("con energía llena lo dice", async () => {
    await renderCounter({ current: 5, max: 5, next_refill_at: null });
    expect(screen.getByLabelText("Energía llena: 5 de 5")).toHaveTextContent(/5$/);
  });

  it("si se está recargando dice en cuántos minutos llega la siguiente", async () => {
    await renderCounter({ current: 3, max: 5, next_refill_at: "2026-11-26T12:12:30Z" });
    expect(screen.getByLabelText("Energía: 3 de 5. La siguiente llega en 13 minutos")).toBeOnTheScreen();
  });

  it("usa singular con un minuto", async () => {
    await renderCounter({ current: 0, max: 5, next_refill_at: "2026-11-26T12:00:20Z" });
    expect(screen.getByLabelText("Energía: 0 de 5. La siguiente llega en 1 minuto")).toHaveTextContent(/0$/);
  });
});
