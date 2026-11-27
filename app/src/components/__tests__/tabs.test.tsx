import { readdirSync } from "node:fs";
import { join } from "node:path";


import { TAB_ROUTES } from "@/components/tab-routes";
import i18n from "@/i18n";

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
});
