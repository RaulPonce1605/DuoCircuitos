import { createInstance } from "i18next";
import { initReactI18next } from "react-i18next";

import { applyDocumentLanguage } from "./document-language";
import es from "./es.json";

export const defaultNS = "translation";
export const resources = { es: { translation: es } } as const;

const i18n = createInstance();

void i18n.use(initReactI18next).init({
  resources,
  lng: "es",
  fallbackLng: "es",
  defaultNS,
  interpolation: { escapeValue: false }, // React ya escapa
  returnNull: false,
});

applyDocumentLanguage("es");

export default i18n;
