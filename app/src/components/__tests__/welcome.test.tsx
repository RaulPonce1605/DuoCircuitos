import { render, screen } from "@testing-library/react-native";

import { AppProviders } from "@/components/app-providers";
import { Welcome } from "@/components/welcome";
import es from "@/i18n/es.json";

describe("Welcome", () => {
  it("muestra el nombre y el lema desde i18n", async () => {
    await render(
      <AppProviders>
        <Welcome />
      </AppProviders>,
    );

    expect(screen.getByText(es.app.name)).toBeOnTheScreen();
    expect(screen.getByText(es.app.tagline)).toBeOnTheScreen();
  });
});
