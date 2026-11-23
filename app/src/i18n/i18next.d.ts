import "i18next";

import type { defaultNS, resources } from "./index";

// Tipa las claves: t("home.streak") falla al compilar si la clave no existe en es.json.
declare module "i18next" {
  interface CustomTypeOptions {
    defaultNS: typeof defaultNS;
    resources: (typeof resources)["es"];
  }
}
