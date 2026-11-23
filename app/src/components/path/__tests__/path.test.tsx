import { fireEvent, render, screen } from "@testing-library/react-native";

import { AppProviders } from "@/components/app-providers";
import { PathView } from "@/components/path/path-view";
import { UnitCard } from "@/components/path/unit-card";
import es from "@/i18n/es.json";
import type { LearningPath, PathUnit } from "@/services/path-service";

const mockPush = jest.fn();
const mockUsePath = jest.fn();
const mockUseCurrentUser = jest.fn();

jest.mock("expo-router", () => ({ useRouter: () => ({ push: mockPush }) }));
jest.mock("@/hooks/use-path", () => ({ usePath: () => mockUsePath() }));
jest.mock("@/hooks/use-current-user", () => ({ useCurrentUser: () => mockUseCurrentUser() }));

const UNIT: PathUnit = {
  slug: "u01-ley-de-ohm",
  title: "Ley de Ohm",
  nodes: [
    {
      key: "ohm-01",
      type: "lesson",
      status: "completed",
      is_current: false,
      lesson: { slug: "ohm-01", title: "Voltaje, corriente y resistencia" },
    },
    {
      key: "ohm-02",
      type: "lesson",
      status: "available",
      is_current: true,
      lesson: { slug: "ohm-02", title: "Ley de Ohm y potencia" },
    },
    { key: "u01:review:1", type: "review", status: "locked", is_current: false, lesson: null },
    { key: "u01:chest:1", type: "chest", status: "available", is_current: false, lesson: null },
  ],
};

const PATH: LearningPath = {
  stages: [{ slug: "e1", title: "Fundamentos", sections: [{ slug: "s1", title: "S", units: [UNIT] }] }],
};

beforeEach(() => {
  mockPush.mockReset();
  mockUseCurrentUser.mockReturnValue({ data: { streak_current: 3, xp_total: 120 } });
});

async function renderUnit(onOpenLesson = jest.fn()) {
  await render(
    <AppProviders>
      <UnitCard unit={UNIT} onOpenLesson={onOpenLesson} />
    </AppProviders>,
  );
  return onOpenLesson;
}

describe("UnitCard", () => {
  it("abre una lección disponible o completada", async () => {
    const onOpenLesson = await renderUnit();

    await fireEvent.press(screen.getByRole("button", { name: /Ley de Ohm y potencia/ }));
    await fireEvent.press(screen.getByRole("button", { name: /Voltaje, corriente/ }));

    expect(onOpenLesson.mock.calls).toEqual([["ohm-02"], ["ohm-01"]]);
  });

  it("los nodos bloqueados y los que aún no se juegan no responden", async () => {
    const onOpenLesson = await renderUnit();

    const locked = screen.getByRole("button", { name: `${es.path.nodeType.review}, ${es.path.status.locked}` });
    const chest = screen.getByRole("button", { name: `${es.path.nodeType.chest}, ${es.common.comingSoon}` });
    expect(locked).toBeDisabled();
    expect(chest).toBeDisabled();
    await fireEvent.press(locked);
    await fireEvent.press(chest);
    expect(onOpenLesson).not.toHaveBeenCalled();
  });

  it("marca la lección actual", async () => {
    await renderUnit();

    expect(screen.getByRole("button", { name: /Ley de Ohm y potencia/ })).toBeSelected();
    expect(screen.getByText(es.path.status.current)).toBeOnTheScreen();
  });
});

describe("PathView", () => {
  it("muestra los contadores, las unidades y navega a la lección", async () => {
    mockUsePath.mockReturnValue({ isPending: false, isError: false, data: PATH });
    await render(
      <AppProviders>
        <PathView />
      </AppProviders>,
    );

    expect(screen.getByLabelText("Racha de 3 días")).toBeOnTheScreen();
    expect(screen.getByLabelText("120 puntos de EXP")).toBeOnTheScreen();
    expect(screen.getByRole("header", { name: "Ley de Ohm" })).toBeOnTheScreen();

    await fireEvent.press(screen.getByRole("button", { name: /Ley de Ohm y potencia/ }));
    expect(mockPush).toHaveBeenCalledWith({ pathname: "/leccion/[slug]", params: { slug: "ohm-02" } });
  });

  it("usa singular con 1 día de racha", async () => {
    mockUsePath.mockReturnValue({ isPending: false, isError: false, data: PATH });
    mockUseCurrentUser.mockReturnValue({ data: { streak_current: 1, xp_total: 1 } });
    await render(
      <AppProviders>
        <PathView />
      </AppProviders>,
    );

    expect(screen.getByLabelText("Racha de 1 día")).toBeOnTheScreen();
    expect(screen.getByLabelText("1 punto de EXP")).toBeOnTheScreen();
  });

  it("muestra carga y error con reintento", async () => {
    mockUsePath.mockReturnValue({ isPending: true, isError: false });
    const { rerender } = await render(
      <AppProviders>
        <PathView />
      </AppProviders>,
    );
    expect(screen.getByLabelText(es.home.loading)).toBeOnTheScreen();

    const refetch = jest.fn();
    mockUsePath.mockReturnValue({ isPending: false, isError: true, error: new Error("x"), refetch });
    await rerender(
      <AppProviders>
        <PathView />
      </AppProviders>,
    );
    expect(screen.getByRole("alert")).toHaveTextContent(es.errors.unknown);
    await fireEvent.press(screen.getByRole("button", { name: es.common.retry }));
    expect(refetch).toHaveBeenCalled();
  });
});
