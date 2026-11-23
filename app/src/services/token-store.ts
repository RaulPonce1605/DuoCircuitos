/** El access token vive SOLO en memoria (app/CLAUDE.md 4.7): nunca en disco ni en logs. */
let accessToken: string | null = null;

export const tokenStore = {
  get: (): string | null => accessToken,
  set: (token: string | null): void => {
    accessToken = token;
  },
};
