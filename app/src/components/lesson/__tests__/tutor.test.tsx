import { fireEvent, render, screen } from "@testing-library/react-native";

import { AppProviders } from "@/components/app-providers";
import { LessonView } from "@/components/lesson/lesson-view";
import es from "@/i18n/es.json";
import { ApiError } from "@/services/api-client";
import type { LessonAttempt } from "@/services/lesson-service";

const mockStart = jest.fn();
const mockCheck = jest.fn();
const mockAsk = jest.fn();

jest.mock("expo-router", () => ({
  useRouter: () => ({ replace: jest.fn(), back: jest.fn(), canGoBack: () => true }),
}));
jest.mock("@/services/lesson-service", () => ({
  lessonService: {
    start: (...args: unknown[]) => mockStart(...args),
    check: (...args: unknown[]) => mockCheck(...args),
  },
}));
jest.mock("@/services/tutor-service", () => ({
  tutorService: { ask: (...args: unknown[]) => mockAsk(...args) },
}));

const ATTEMPT: LessonAttempt = {
  attempt_id: "a-1",
  lesson: { slug: "ohm-01", title: "Voltaje, corriente y resistencia" },
  progress: { completed: 0, total: 1 },
  current_exercise: {
    instance_id: "i-1",
    exercise: { type: "numeric", prompt: "Un resistor de 220 Ω a 5 V. ¿Corriente?", unit: "A" },
  },
  energy: { current: 5, max: 5, next_refill_at: null },
};

beforeEach(() => {
  jest.clearAllMocks();
  mockStart.mockResolvedValue(ATTEMPT);
});

async function openTutor() {
  await render(
    <AppProviders>
      <LessonView lessonSlug="ohm-01" />
    </AppProviders>,
  );
  await fireEvent.press(await screen.findByRole("button", { name: es.lesson.help }));
  expect(screen.getByText(es.tutor.intro)).toBeOnTheScreen();
}

describe("Tutor en la lección", () => {
  it("pide una pista sin escribir nada y muestra la respuesta del tutor", async () => {
    mockAsk.mockResolvedValue({ reply: "Usa la Ley de Ohm.", source: "llm", help_level: 1, remaining_requests: 5 });
    await openTutor();

    await fireEvent.press(screen.getByRole("button", { name: es.tutor.ask }));

    expect(mockAsk).toHaveBeenCalledWith("i-1", null);
    expect(await screen.findByText("Usa la Ley de Ohm.")).toBeOnTheScreen();
    expect(screen.getByText(es.tutor.name)).toBeOnTheScreen();
    expect(screen.getByText("Puedes pedir ayuda 5 veces más.")).toBeOnTheScreen();
    expect(screen.getByRole("button", { name: es.tutor.askAgain })).toBeOnTheScreen();
  });

  it("manda la duda del alumno y marca cuando la respuesta es una pista del temario", async () => {
    mockAsk.mockResolvedValue({ reply: "Despeja I.", source: "hint", help_level: 1, remaining_requests: 1 });
    await openTutor();

    await fireEvent.changeText(screen.getByLabelText(es.tutor.questionLabel), "  ¿qué fórmula uso?  ");
    await fireEvent.press(screen.getByRole("button", { name: es.tutor.ask }));

    expect(mockAsk).toHaveBeenCalledWith("i-1", "¿qué fórmula uso?");
    expect(await screen.findByText("Despeja I.")).toBeOnTheScreen();
    expect(screen.getByText("¿qué fórmula uso?")).toBeOnTheScreen();
    expect(screen.getByText(es.tutor.fromSyllabus)).toBeOnTheScreen();
    expect(screen.getByText("Puedes pedir ayuda 1 vez más.")).toBeOnTheScreen();
  });

  it("cuando se acaba la ayuda ya no deja pedir más", async () => {
    mockAsk.mockResolvedValue({ reply: "Última pista.", source: "hint", help_level: 6, remaining_requests: 0 });
    await openTutor();

    await fireEvent.press(screen.getByRole("button", { name: es.tutor.ask }));

    expect(await screen.findByText(es.tutor.noMoreHelp)).toBeOnTheScreen();
    expect(screen.queryByRole("button", { name: es.tutor.askAgain })).toBeNull();
  });

  it("traduce el límite de peticiones del backend", async () => {
    mockAsk.mockRejectedValue(new ApiError("tutor_rate_limited", 429));
    await openTutor();

    await fireEvent.press(screen.getByRole("button", { name: es.tutor.ask }));

    expect(await screen.findByRole("alert")).toHaveTextContent(es.errors.tutor_rate_limited);
  });

  it("se puede cerrar y volver a abrir", async () => {
    await openTutor();
    await fireEvent.press(screen.getByRole("button", { name: es.tutor.close }));

    expect(screen.queryByTestId("tutor-panel")).toBeNull();
    expect(screen.getByRole("button", { name: es.lesson.help })).toBeOnTheScreen();
  });
});
