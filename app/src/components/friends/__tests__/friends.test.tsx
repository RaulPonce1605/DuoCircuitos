import { fireEvent, render, screen } from "@testing-library/react-native";

import { AppProviders } from "@/components/app-providers";
import { FriendsView } from "@/components/friends/friends-view";
import es from "@/i18n/es.json";
import type { Friends, UserCard } from "@/services/social-service";

const mockFriends = jest.fn();
const mockSearch = jest.fn();
const mockFollow = jest.fn();
const mockUnfollow = jest.fn();

jest.mock("@/services/social-service", () => ({
  socialService: {
    friends: (...args: unknown[]) => mockFriends(...args),
    search: (...args: unknown[]) => mockSearch(...args),
    follow: (...args: unknown[]) => mockFollow(...args),
    unfollow: (...args: unknown[]) => mockUnfollow(...args),
  },
}));

const LUIS: UserCard = {
  id: "u-luis",
  display_name: "Luis",
  xp_total: 320,
  streak: 4,
  league_tier: 1,
  league_tier_id: "capacitor",
  is_following: true,
  follows_me: true,
};
const PRIVATE: UserCard = { ...LUIS, id: "u-priv", display_name: null, is_following: false, follows_me: true };
const FRIENDS: Friends = { following: [LUIS], followers: [LUIS, PRIVATE] };

beforeEach(() => {
  jest.clearAllMocks();
  mockFriends.mockResolvedValue(FRIENDS);
});

async function renderView() {
  await render(
    <AppProviders>
      <FriendsView />
    </AppProviders>,
  );
  await screen.findByText(es.friends.following);
}

describe("FriendsView", () => {
  it("muestra a quién sigue y quién lo sigue; los privados sin nombre ni botón", async () => {
    await renderView();

    expect(screen.getAllByText("Luis")).toHaveLength(2);
    expect(screen.getAllByText(es.friends.mutual)).toHaveLength(2);
    expect(screen.getAllByText("320 EXP · racha de 4 · Liga Capacitor")).toHaveLength(3);
    expect(screen.getByText(es.leagues.anonymous)).toBeOnTheScreen();
    expect(screen.getAllByRole("button", { name: es.friends.unfollow })).toHaveLength(2);
    expect(screen.queryByRole("button", { name: es.friends.follow })).toBeNull();
  });

  it("busca con 2 letras o más y deja seguir", async () => {
    const ana: UserCard = { ...LUIS, id: "u-ana", display_name: "Ana", is_following: false, follows_me: false };
    mockSearch.mockResolvedValue([ana]);
    mockFollow.mockResolvedValue({ ...ana, is_following: true });
    await renderView();

    await fireEvent.changeText(screen.getByLabelText(es.friends.searchLabel), "a");
    expect(mockSearch).not.toHaveBeenCalled();
    await fireEvent.changeText(screen.getByLabelText(es.friends.searchLabel), "an");
    await fireEvent.press(await screen.findByRole("button", { name: es.friends.follow }));

    expect(mockSearch).toHaveBeenCalledWith("an");
    expect(mockFollow).toHaveBeenCalledWith("u-ana");
  });

  it("sin resultados lo dice", async () => {
    mockSearch.mockResolvedValue([]);
    await renderView();

    await fireEvent.changeText(screen.getByLabelText(es.friends.searchLabel), "zz");

    expect(await screen.findByText(es.friends.noResults)).toBeOnTheScreen();
  });
});
