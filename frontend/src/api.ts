const BASE = '/api';

// --- Types ---

export interface UserPublic {
  id: string;
  name: string;
  email: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface GamePublic {
  id: string;
  name: string;
  invite_code: string;
  created_at: string;
  created_by: string;
}

export interface F1SessionPublic {
  id: string;
  type: string;
  date: string;
  race_name: string;
  race_round: number;
  race_season: number;
}

export interface Driver {
  id: string;
  code: string;
  first_name: string;
  last_name: string;
  external_id: string;
}

export interface MemberScore {
  user_id: string;
  position_score: number;
  dnf_score: number;
  total_score: number;
}

// --- Helpers ---

function auth(token: string) {
  return { Authorization: `Bearer ${token}` };
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    // FastAPI 422 returns detail as an array of validation errors
    if (Array.isArray(body.detail)) {
      const msg = body.detail.map((e: { msg?: string; loc?: string[] }) =>
        `${e.loc?.slice(1).join('.')}: ${e.msg}`
      ).join(', ');
      throw new Error(msg || `Error ${res.status}`);
    }
    throw new Error(body.message || body.detail || `Error ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// --- Auth ---

export async function register(name: string, email: string, password: string): Promise<UserPublic> {
  const res = await fetch(`${BASE}/user/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  });
  return handle(res);
}

export async function login(email: string, password: string): Promise<Token> {
  const form = new URLSearchParams();
  form.append('username', email);
  form.append('password', password);
  const res = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form,
  });
  return handle(res);
}

export async function getMe(token: string): Promise<UserPublic> {
  const res = await fetch(`${BASE}/user/me`, { headers: auth(token) });
  return handle(res);
}

// --- Games ---

export async function getGames(token: string): Promise<GamePublic[]> {
  const res = await fetch(`${BASE}/game/`, { headers: auth(token) });
  return handle(res);
}

export async function createGame(token: string, name: string): Promise<GamePublic> {
  const res = await fetch(`${BASE}/game/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...auth(token) },
    body: JSON.stringify({ name }),
  });
  return handle(res);
}

export async function joinGame(token: string, invite_code: string): Promise<GamePublic> {
  const res = await fetch(`${BASE}/game/join`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...auth(token) },
    body: JSON.stringify({ invite_code }),
  });
  return handle(res);
}

// --- F1 ---

export async function getSeasons(token: string): Promise<number[]> {
  const res = await fetch(`${BASE}/f1/seasons`, { headers: auth(token) });
  const data = await handle<{ seasons: number[] }>(res);
  return data.seasons;
}

export async function getSessions(token: string, season: number): Promise<F1SessionPublic[]> {
  const res = await fetch(`${BASE}/f1/season/${season}/sessions`, { headers: auth(token) });
  return handle(res);
}

export async function getDrivers(token: string, sessionId: string): Promise<Driver[]> {
  const res = await fetch(`${BASE}/f1/session/${sessionId}/drivers`, { headers: auth(token) });
  return handle(res);
}

// --- Predictions ---

export async function predict(
  token: string,
  gameId: string,
  f1session_id: string,
  position_driver_id: string,
  dnf_driver_id: string
): Promise<void> {
  const res = await fetch(`${BASE}/game/${gameId}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...auth(token) },
    body: JSON.stringify({ f1session_id, position_driver_id, dnf_driver_id, position: 10 }),
  });
  await handle(res);
}

// --- Leaderboard ---

export async function getLeaderboard(token: string, gameId: string): Promise<MemberScore[]> {
  const res = await fetch(`${BASE}/game/${gameId}/scores`, { headers: auth(token) });
  return handle(res);
}
