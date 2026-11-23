import { readdirSync } from "node:fs";
import { join } from "node:path";

import { render, screen } from "@testing-library/react-native";
import type { ComponentType } from "react";

import ChallengesScreen from "@/app/(tabs)/desafios";
import HomeScreen from "@/app/(tabs)/index";
import LeaguesScreen from "@/app/(tabs)/ligas";
import MoreScreen from "@/app/(tabs)/mas";
import ProfileScreen from "@/app/(tabs)/perfil";
import { AppProviders } from "@/components/app-providers";
import { TAB_ROUTES } from "@/components/tab-routes";
import i18n from "@/i18n";
import es from "@/i18n/es.json";

jest.mock("@/hooks/use-session", () => ({
  useSession: () => ({
    status: "signedIn",
    user: { display_name: "Ana" },
    signIn: jest.fn(),
    signUp: jest.fn(),
    signOut: jest.fn(),
  }),
}));

describe("pestañas", () => {
  it("son las 5 del producto, en orden", () => {
    expect(TAB_ROUTES.map((tab) => i18n.t(tab.titleKey))).toEqual([
      "Inicio",
      "Desafíos",
      "Ligas",
      "Perfil",
      "Más",
    ]);
  });

  it("cada pestaña tiene su archivo de ruta y no sobra ninguno", () => {
    const dir = join(__dirname, "..", "..", "app", "(tabs)");
    const routeFiles = readdirSync(dir)
      .filter((file) => file.endsWith(".tsx") && !file.startsWith("_"))
      .map((file) => file.replace(/\.tsx$/, ""))
      .sort();
    expect(routeFiles).toEqual(TAB_ROUTES.map((tab) => tab.name).sort());
  });

  it.each<[string, ComponentType, keyof typeof es]>([
    ["Inicio", HomeScreen, "home"],
    ["Desafíos", ChallengesScreen, "challenges"],
    ["Ligas", LeaguesScreen, "leagues"],
    ["Perfil", ProfileScreen, "profile"],
    ["Más", MoreScreen, "more"],
  ])("la pantalla %s muestra su título y su estado vacío", async (_, ScreenComponent, key) => {
    await render(
      <AppProviders>
        <ScreenComponent />
      </AppProviders>,
    );
    const section = es[key] as { title: string; empty: string };
    expect(screen.getByRole("header", { name: section.title })).toBeOnTheScreen();
    expect(screen.getByText(section.empty)).toBeOnTheScreen();
  });
});
