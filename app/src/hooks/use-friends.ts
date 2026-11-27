import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { socialService, type UserCard } from "@/services/social-service";

export const FRIENDS_QUERY_KEY = ["friends"] as const;
const MIN_QUERY = 2;

export function useFriends() {
  return useQuery({ queryKey: FRIENDS_QUERY_KEY, queryFn: socialService.friends });
}

/** Busca perfiles públicos; no pide nada con menos de 2 letras. */
export function useUserSearch(query: string) {
  const text = query.trim();
  return useQuery({
    queryKey: ["user-search", text],
    queryFn: () => socialService.search(text),
    enabled: text.length >= MIN_QUERY,
    staleTime: 30_000,
  });
}

/** Seguir o dejar de seguir; refresca la lista de amigos y la búsqueda. */
export function useToggleFollow() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (card: UserCard) => (card.is_following ? socialService.unfollow(card.id) : socialService.follow(card.id)),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: FRIENDS_QUERY_KEY });
      void queryClient.invalidateQueries({ queryKey: ["user-search"] });
    },
  });
}
