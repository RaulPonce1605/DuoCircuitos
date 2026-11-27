import { fireEvent, render, screen } from "@testing-library/react-native";

import { AppProviders } from "@/components/app-providers";
import { LessonView } from "@/components/lesson/lesson-view";
import { SummaryView } from "@/components/lesson/summary-view";
import es from "@/i18n/es.json";
import { ApiError } from "@/services/api-client";
import type { CheckResult, LessonAttempt, LessonSummary } from "@/services/lesson-service";

const mockRouter = { replace: jest.fn(), back: jest.fn(), canGoBack: jest.fn(() => true) };
const mockStart = jest.fn();
const mockCheck = jest.fn();
const mockSummary = jest.fn();

jest.mock("expo-router", () => ({ useRouter: () => mockRouter }));
jest.mock("@/services/lesson-service", () => ({
  lessonService: {
    start: (...args: unknown[]) => mockStart(...args),
    check: (...args: unknown[]) => mockCheck(...args),
    summary: (...args: unknown[]) => mockSummary(...args),
  },
}));

const MC = {
  instance_id: "i-1",
  exercise: { type: "multiple_choice" as const, prompt: "¿Unidad de la resistencia?", options: ["Volt", "Ohm"] },
};
const NUM = {
  instance_id: "i-2",
  exercise: { type: "numeric" as const, prompt: "Un resistor de 220 Ω a 5 V. ¿Corriente?", unit: "A" },
};
const ATTEMPT: LessonAttempt = {
  attempt_id: "a-1",
  lesson: { slug: "ohm-01", title: "Voltaje, corriente y resistencia" },
  progress: { completed: 0, total: 2 },
  current_exercise: MC,
  energy: { current: 5, max: 5, next_refill_at: null },
};

function result(overrides: Partial<CheckResult>): CheckResult {
  return {
    correct: true,
    correct_answer: "Ohm",
    explanation: "La resistencia se mide en ohms.",
    progress: { completed: 1, total: 2 },
    next_exercise: NUM,
    attempt_completed: false,
    energy: { current: 5, max: 5, next_refill_at: null },
    ...overrides,
  };
}

beforeEach(() => {
  jest.clearAllMocks();
  mockStart.mockResolvedValue(ATTEMPT);
});

async function renderLesson() {
  await render(
    <AppProviders>
      <LessonView lessonSlug="ohm-01" />
    </AppProviders>,
  );
  await screen.findByText(MC.exercise.prompt);
}

describe("LessonView", () => {
  it("inicia la lección y no deja Comprobar sin respuesta", async () => {
    await renderLesson();

    expect(mockStart).toHaveBeenCalledWith("ohm-01");
    expect(screen.getByRole("progressbar")).toHaveAccessibilityValue({ now: 0 });
    expect(screen.getByRole("button", { name: es.lesson.check })).toBeDisabled();
  });

  it("Comprobar manda la respuesta al backend y muestra la retroalimentación correcta", async () => {
    mockCheck.mockResolvedValue(result({}));
    await renderLesson();

    await fireEvent.press(screen.getByRole("radio", { name: "Ohm" }));
    await fireEvent.press(screen.getByRole("button", { name: es.lesson.check }));

    expect(mockCheck).toHaveBeenCalledWith("i-1", { type: "multiple_choice", option: 1 });
    expect(await screen.findByText(es.lesson.correct)).toBeOnTheScreen();
    expect(screen.getByText("La resistencia se mide en ohms.")).toBeOnTheScreen();
    expect(screen.getByRole("progressbar")).toHaveAccessibilityValue({ now: 50 });
    // Después de Comprobar ya no se puede cambiar la respuesta.
    expect(screen.getByRole("radio", { name: "Volt" })).toBeDisabled();
  });

  it("si falla, muestra la respuesta correcta y avisa que se repetirá", async () => {
    mockCheck.mockResolvedValue(
      result({ correct: false, progress: { completed: 0, total: 2 }, next_exercise: NUM }),
    );
    await renderLesson();

    await fireEvent.press(screen.getByRole("radio", { name: "Volt" }));
    await fireEvent.press(screen.getByRole("button", { name: es.lesson.check }));

    expect(await screen.findByText(es.lesson.incorrect)).toBeOnTheScreen();
    expect(screen.getByText("Respuesta correcta: Ohm")).toBeOnTheScreen();
    expect(screen.getByText(es.lesson.willRepeat)).toBeOnTheScreen();
  });

  it("Continuar pasa al siguiente ejercicio con la respuesta en blanco", async () => {
    mockCheck.mockResolvedValue(result({}));
    await renderLesson();

    await fireEvent.press(screen.getByRole("radio", { name: "Ohm" }));
    await fireEvent.press(screen.getByRole("button", { name: es.lesson.check }));
    await fireEvent.press(await screen.findByRole("button", { name: es.lesson.continue }));

    expect(screen.getByText(NUM.exercise.prompt)).toBeOnTheScreen();
    expect(screen.queryByTestId("feedback-panel")).toBeNull();
    expect(screen.getByRole("button", { name: es.lesson.check })).toBeDisabled();
  });

  it("al terminar la lección va al resumen", async () => {
    mockCheck.mockResolvedValue(
      result({ progress: { completed: 2, total: 2 }, next_exercise: null, attempt_completed: true }),
    );
    await renderLesson();

    await fireEvent.press(screen.getByRole("radio", { name: "Ohm" }));
    await fireEvent.press(screen.getByRole("button", { name: es.lesson.check }));
    await fireEvent.press(await screen.findByRole("button", { name: es.lesson.continue }));

    expect(mockRouter.replace).toHaveBeenCalledWith({
      pathname: "/leccion/resumen/[attemptId]",
      params: { attemptId: "a-1" },
    });
  });

  it("muestra el error del backend traducido si la lección está bloqueada", async () => {
    mockStart.mockRejectedValue(new ApiError("node_locked", 409));
    await render(
      <AppProviders>
        <LessonView lessonSlug="ohm-02" />
      </AppProviders>,
    );

    expect(await screen.findByRole("alert")).toHaveTextContent(es.errors.node_locked);
  });

  it("el botón de cerrar regresa", async () => {
    await renderLesson();
    await fireEvent.press(screen.getByRole("button", { name: es.lesson.exit }));
    expect(mockRouter.back).toHaveBeenCalled();
  });
});

const SUMMARY: LessonSummary = {
  attempt_id: "a-1",
  lesson: { slug: "ohm-01", title: "Voltaje, corriente y resistencia" },
  exercise_count: 5,
  first_try_correct: 4,
  accuracy: 80,
  xp_awarded: 45,
  concepts: ["Voltaje", "Corriente eléctrica"],
  streak: 3,
  streak_extended: true,
};

describe("SummaryView", () => {
  it("muestra EXP, precisión, conceptos y racha del backend", async () => {
    mockSummary.mockResolvedValue(SUMMARY);
    await render(
      <AppProviders>
        <SummaryView attemptId="a-1" />
      </AppProviders>,
    );

    expect(await screen.findByText(es.summary.title)).toBeOnTheScreen();
    expect(screen.getByLabelText("EXP ganada: +45")).toBeOnTheScreen();
    expect(screen.getByLabelText("Precisión: 80 %")).toBeOnTheScreen();
    expect(screen.getByText("Al primer intento: 4 de 5")).toBeOnTheScreen();
    expect(screen.getByText("Voltaje")).toBeOnTheScreen();
    expect(screen.getByText("Corriente eléctrica")).toBeOnTheScreen();
    expect(screen.getByText("Racha de 3 días")).toBeOnTheScreen();
    expect(screen.getByText(es.summary.streakUp)).toBeOnTheScreen();

    await fireEvent.press(screen.getByRole("button", { name: es.summary.continue }));
    expect(mockRouter.replace).toHaveBeenCalledWith("/");
  });

  it("si la racha no subió lo dice, en singular", async () => {
    mockSummary.mockResolvedValue({ ...SUMMARY, streak: 1, streak_extended: false });
    await render(
      <AppProviders>
        <SummaryView attemptId="a-1" />
      </AppProviders>,
    );

    expect(await screen.findByText("Racha de 1 día")).toBeOnTheScreen();
    expect(screen.getByText(es.summary.streakKept)).toBeOnTheScreen();
  });
});
