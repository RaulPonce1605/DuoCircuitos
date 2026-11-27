import { fireEvent, render, screen } from "@testing-library/react-native";

import { AppProviders } from "@/components/app-providers";
import { ProfileSummary } from "@/components/profile/profile-summary";
import { SettingsView } from "@/components/settings/settings-view";
import es from "@/i18n/es.json";
import { ApiError } from "@/services/api-client";
import type { User } from "@/services/auth-service";
import type { Achievements } from "@/services/rewards-service";

const mockGetCurrentUser = jest.fn();
const mockAchievements = jest.fn();
const mockUpdate = jest.fn();
const mockSignOut = jest.fn();
const mockPush = jest.fn();

jest.mock("@/services/auth-service", () => ({
  authService: { getCurrentUser: (...args: unknown[]) => mockGetCurrentUser(...args) },
  deviceTimezone: () => "Europe/Madrid",
}));
jest.mock("@/services/rewards-service", () => ({
  rewardsService: { achievements: (...args: unknown[]) => mockAchievements(...args) },
}));
jest.mock("@/services/user-service", () => ({
  userService: { update: (...args: unknown[]) => mockUpdate(...args) },
}));
jest.mock("@/hooks/use-session", () => ({ useSession: () => ({ signOut: mockSignOut }) }));
jest.mock("expo-router", () => ({ useRouter: () => ({ push: mockPush }) }));

const USER: User = {
  id: "u-1",
  email: "ana@example.com",
  display_name: "Ana",
  timezone: "America/Mexico_City",
  xp_total: 340,
  streak_current: 1,
  streak_longest: 8,
  created_at: "2026-11-02T12:00:00Z",
  energy: { current: 5, max: 5, next_refill_at: null },
  notify_streak_reminder: true,
  notify_challenges: false,
  profile_public: true,
};

const ACHIEVEMENTS: Achievements = {
  achievements: [
    { id: "lessons", metric: "lessons_completed", value: 6, thresholds: [1, 5, 10], level: 2, next_threshold: 10 },
    { id: "streak", metric: "streak_longest", value: 8, thresholds: [3, 7, 30], level: 2, next_threshold: 30 },
  ],
  badges: [
    { achievement_id: "streak", level: 2, threshold: 7, earned_at: "2026-11-20T12:00:00Z" },
    { achievement_id: "lessons", level: 2, threshold: 5, earned_at: "2026-11-19T12:00:00Z" },
    { achievement_id: "streak", level: 1, threshold: 3, earned_at: "2026-11-10T12:00:00Z" },
    { achievement_id: "lessons", level: 1, threshold: 1, earned_at: "2026-11-02T12:00:00Z" },
  ],
};

beforeEach(() => {
  jest.clearAllMocks();
  mockGetCurrentUser.mockResolvedValue(USER);
  mockAchievements.mockResolvedValue(ACHIEVEMENTS);
});

describe("ProfileSummary", () => {
  it("muestra racha, EXP total, liga, logros y las medallas recientes", async () => {
    await render(
      <AppProviders>
        <ProfileSummary />
      </AppProviders>,
    );

    expect(await screen.findByRole("header", { name: "Ana" })).toBeOnTheScreen();
    expect(screen.getByLabelText("Racha: 1 día")).toBeOnTheScreen();
    expect(screen.getByLabelText("Mejor racha: 8 días")).toBeOnTheScreen();
    expect(screen.getByLabelText("EXP total: 340")).toBeOnTheScreen();
    expect(screen.getByLabelText(`Liga: ${es.profile.noLeague}`)).toBeOnTheScreen();
    expect(await screen.findByText("4 de 6 niveles alcanzados")).toBeOnTheScreen();
    // Solo las 3 más recientes.
    expect(screen.getByText("Constancia: Plata")).toBeOnTheScreen();
    expect(screen.getByText("Constancia: Bronce")).toBeOnTheScreen();
    expect(screen.queryByText("Aprendiz de circuitos: Bronce")).toBeNull();

    await fireEvent.press(screen.getByRole("button", { name: es.profile.settings }));
    await fireEvent.press(screen.getByRole("button", { name: es.profile.seeAchievements }));
    await fireEvent.press(screen.getByRole("button", { name: es.profile.seeBadges }));
    expect(mockPush.mock.calls).toEqual([["/configuracion"], ["/logros"], ["/medallas"]]);
  });

  it("sin medallas invita a empezar", async () => {
    mockAchievements.mockResolvedValue({ ...ACHIEVEMENTS, badges: [] });
    await render(
      <AppProviders>
        <ProfileSummary />
      </AppProviders>,
    );

    expect(await screen.findByText(es.profile.noBadges)).toBeOnTheScreen();
  });

  it("si falla la carga lo dice", async () => {
    mockGetCurrentUser.mockRejectedValue(new ApiError("network", 0));
    await render(
      <AppProviders>
        <ProfileSummary />
      </AppProviders>,
    );

    expect(await screen.findByRole("alert")).toHaveTextContent(es.errors.network);
  });
});

async function renderSettings() {
  await render(
    <AppProviders>
      <SettingsView />
    </AppProviders>,
  );
  await screen.findByLabelText(es.settings.displayName);
}

describe("SettingsView", () => {
  it("guarda el nombre nuevo", async () => {
    mockUpdate.mockResolvedValue({ ...USER, display_name: "Ana Luisa" });
    await renderSettings();

    expect(screen.getByRole("button", { name: es.settings.save })).toBeDisabled();
    await fireEvent.changeText(screen.getByLabelText(es.settings.displayName), "  Ana Luisa ");
    await fireEvent.press(screen.getByRole("button", { name: es.settings.save }));

    expect(mockUpdate).toHaveBeenCalledWith({ display_name: "Ana Luisa" });
    expect(await screen.findByText(es.settings.saved)).toBeOnTheScreen();
  });

  it("los interruptores guardan notificaciones y privacidad", async () => {
    mockUpdate.mockImplementation(async (changes: Partial<User>) => ({ ...USER, ...changes }));
    await renderSettings();

    expect(screen.getByRole("switch", { name: es.settings.challengeAlerts })).toHaveProp("value", false);
    await fireEvent(screen.getByRole("switch", { name: es.settings.challengeAlerts }), "valueChange", true);
    await fireEvent(screen.getByRole("switch", { name: es.settings.publicProfile }), "valueChange", false);

    expect(mockUpdate.mock.calls).toEqual([[{ notify_challenges: true }], [{ profile_public: false }]]);
    expect(await screen.findByRole("switch", { name: es.settings.publicProfile })).toHaveProp("value", false);
  });

  it("ofrece usar la zona horaria del dispositivo si es otra", async () => {
    mockUpdate.mockResolvedValue({ ...USER, timezone: "Europe/Madrid" });
    await renderSettings();

    await fireEvent.press(screen.getByRole("button", { name: "Usar la de este dispositivo (Europe/Madrid)" }));

    expect(mockUpdate).toHaveBeenCalledWith({ timezone: "Europe/Madrid" });
    expect(await screen.findByText(new RegExp("^Europe/Madrid\\."))).toBeOnTheScreen();
    expect(screen.queryByRole("button", { name: /Usar la de este dispositivo/ })).toBeNull();
  });

  it("muestra el error traducido si no se pudo guardar", async () => {
    mockUpdate.mockRejectedValue(new ApiError("validation_error", 422));
    await renderSettings();

    await fireEvent.changeText(screen.getByLabelText(es.settings.displayName), "Otro");
    await fireEvent.press(screen.getByRole("button", { name: es.settings.save }));

    expect(await screen.findByRole("alert")).toHaveTextContent(es.errors.validation_error);
  });

  it("cierra sesión", async () => {
    await renderSettings();
    await fireEvent.press(screen.getByRole("button", { name: es.settings.logout }));
    expect(mockSignOut).toHaveBeenCalled();
  });
});
