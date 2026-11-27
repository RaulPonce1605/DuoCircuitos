import { Platform } from "react-native";

import { nextStreakReminder, remindersService } from "@/services/reminders";

const mockCancel = jest.fn(async () => undefined);
const mockSchedule = jest.fn(async () => "id");
const mockGetPermissions = jest.fn();
const mockRequestPermissions = jest.fn();

jest.mock("expo-notifications", () => ({
  SchedulableTriggerInputTypes: { DATE: "date", DAILY: "daily" },
  cancelAllScheduledNotificationsAsync: () => mockCancel(),
  scheduleNotificationAsync: (...args: unknown[]) => mockSchedule(...(args as [])),
  getPermissionsAsync: () => mockGetPermissions(),
  requestPermissionsAsync: () => mockRequestPermissions(),
}));

const originalOS = Platform.OS;

function setOS(os: typeof Platform.OS) {
  Object.defineProperty(Platform, "OS", { configurable: true, get: () => os });
}

beforeEach(() => {
  jest.clearAllMocks();
  setOS("ios");
});

afterAll(() => {
  setOS(originalOS);
});

describe("nextStreakReminder", () => {
  it("hoy a las 19:00 si aún no practica y no ha pasado la hora", () => {
    const at = nextStreakReminder(new Date(2026, 10, 26, 10, 0), false);
    expect(at).toEqual(new Date(2026, 10, 26, 19, 0));
  });

  it("mañana si ya practicó hoy", () => {
    const at = nextStreakReminder(new Date(2026, 10, 26, 10, 0), true);
    expect(at).toEqual(new Date(2026, 10, 27, 19, 0));
  });

  it("mañana si ya pasó la hora", () => {
    const at = nextStreakReminder(new Date(2026, 10, 26, 21, 30), false);
    expect(at).toEqual(new Date(2026, 10, 27, 19, 0));
  });
});

describe("remindersService", () => {
  it("reemplaza los avisos programados por los del plan", async () => {
    const at = new Date(2026, 10, 26, 19, 0);

    await remindersService.apply({
      streak: { at, title: "T", body: "B" },
      challenges: { hour: 9, title: "C", body: "D" },
    });

    expect(mockCancel).toHaveBeenCalledTimes(1);
    expect(mockSchedule).toHaveBeenCalledWith({
      content: { title: "T", body: "B" },
      trigger: { type: "date", date: at },
    });
    expect(mockSchedule).toHaveBeenCalledWith({
      content: { title: "C", body: "D" },
      trigger: { type: "daily", hour: 9, minute: 0 },
    });
  });

  it("pide permiso solo si se le indica y si todavía se puede", async () => {
    mockGetPermissions.mockResolvedValue({ granted: false, canAskAgain: true });
    mockRequestPermissions.mockResolvedValue({ granted: true });

    expect(await remindersService.permission(false)).toBe("undetermined");
    expect(mockRequestPermissions).not.toHaveBeenCalled();
    expect(await remindersService.permission(true)).toBe("granted");

    mockGetPermissions.mockResolvedValue({ granted: false, canAskAgain: false });
    expect(await remindersService.permission(true)).toBe("denied");
  });

  it("en la web no hace nada", async () => {
    setOS("web");

    expect(remindersService.supported()).toBe(false);
    expect(await remindersService.permission(true)).toBe("unsupported");
    await remindersService.apply({ streak: null, challenges: null });
    await remindersService.clear();
    expect(mockCancel).not.toHaveBeenCalled();
  });
});
