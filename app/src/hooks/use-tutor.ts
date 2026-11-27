import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { type TutorReply, tutorService } from "@/services/tutor-service";

export type TutorChatMessage =
  | { id: number; role: "student"; text: string }
  | { id: number; role: "tutor"; text: string; source: TutorReply["source"] };

/**
 * Conversación con el tutor sobre UNA instancia de ejercicio. Al cambiar de ejercicio se monta un
 * componente nuevo (con `key`), así que la conversación empieza vacía.
 */
export function useTutor(instanceId: string) {
  const [messages, setMessages] = useState<TutorChatMessage[]>([]);
  const [remaining, setRemaining] = useState<number | null>(null);

  const ask = useMutation({
    mutationFn: (message: string | null) => tutorService.ask(instanceId, message),
    onMutate: (message) => {
      if (message) {
        setMessages((previous) => [...previous, { id: previous.length, role: "student", text: message }]);
      }
    },
    onSuccess: (reply) => {
      setRemaining(reply.remaining_requests);
      setMessages((previous) => [
        ...previous,
        { id: previous.length, role: "tutor", text: reply.reply, source: reply.source },
      ]);
    },
  });

  return {
    messages,
    remaining,
    error: ask.error,
    isAsking: ask.isPending,
    canAsk: !ask.isPending && remaining !== 0,
    ask: (message: string) => {
      if (!ask.isPending && remaining !== 0) {
        const trimmed = message.trim();
        ask.mutate(trimmed === "" ? null : trimmed);
      }
    },
  };
}
