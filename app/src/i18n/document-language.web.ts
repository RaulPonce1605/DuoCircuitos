/**
 * Web: el HTML de Expo sale con `lang="en"` y el navegador ofrece traducir la app. Una
 * traducción automática cambiaría enunciados, opciones y unidades ("Volt" → "Voltio"), así que
 * se declara el idioma y se pide no traducir. (Una plantilla `+html.tsx` haría lo mismo, pero en
 * Expo SDK 58 impide que se inserten los scripts de la app.)
 */
export function applyDocumentLanguage(lang: string): void {
  if (typeof document === "undefined") {
    return;
  }
  document.documentElement.lang = lang;
  document.documentElement.setAttribute("translate", "no");
}
