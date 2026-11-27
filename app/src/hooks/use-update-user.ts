import { useMutation, useQueryClient } from "@tanstack/react-query";

import { CHALLENGES_QUERY_KEY } from "@/hooks/use-challenges";
import { CURRENT_USER_QUERY_KEY } from "@/hooks/use-current-user";
import { userService, type UserUpdate } from "@/services/user-service";

/** Guarda un cambio de Configuración y deja el usuario actualizado en la caché. */
export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (changes: UserUpdate) => userService.update(changes),
    onSuccess: (user, changes) => {
      queryClient.setQueryData(CURRENT_USER_QUERY_KEY, user);
      if (changes.timezone) {
        // Otra zona horaria puede cambiar el "día" de los desafíos.
        void queryClient.invalidateQueries({ queryKey: CHALLENGES_QUERY_KEY });
      }
    },
  });
}
