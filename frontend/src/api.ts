const BASE = import.meta.env.VITE_API_URL ?? '/api';

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
  season: number;
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

export interface ResultPublic {
  driver_id: string;
  driver_code: string;
  driver_first_name: string;
  driver_last_name: string;
  position: number;
  position_text: string | null;
  status: string | null;
  laps: number | null;
  is_first_dnf: boolean;
}

export interface MemberScore {
  user_id: string;
  position_score: number;
  dnf_score: number;
  total_score: number;
}

export interface PredictionPublic {
  id: string;
  game_id: string;
  user_id: string;
  f1session_id: string;
  position: number;
  position_driver_id: string;
  dnf_driver_id: string;
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
  const res = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
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

export async function createGame(token: string, name: string, season: number): Promise<GamePublic> {
  const res = await fetch(`${BASE}/game/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...auth(token) },
    body: JSON.stringify({ name, season }),
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

export async function getSessionResults(token: string, sessionId: string): Promise<ResultPublic[]> {
  const res = await fetch(`${BASE}/f1/session/${sessionId}/results`, { headers: auth(token) });
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

export async function getGamePredictions(token: string, gameId: string): Promise<PredictionPublic[]> {
  const res = await fetch(`${BASE}/game/${gameId}/predictions`, { headers: auth(token) });
  return handle(res);
}

export async function getMyPrediction(token: string, gameId: string, sessionId: string): Promise<PredictionPublic | null> {
  const res = await fetch(`${BASE}/game/${gameId}/f1session/${sessionId}/me`, { headers: auth(token) });
  if (!res.ok) return null;
  return res.json();
}

export async function updateName(token: string, name: string): Promise<UserPublic> {
  const res = await fetch(`${BASE}/user/me`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...auth(token) },
    body: JSON.stringify({ name }),
  });
  return handle(res);
}

export async function changePassword(token: string, current_password: string, new_password: string): Promise<void> {
  const res = await fetch(`${BASE}/user/me/password`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...auth(token) },
    body: JSON.stringify({ current_password, new_password }),
  });
  if (!res.ok) await handle(res); // handle throws on error; 204 has no body to parse
}

export async function getMembers(token: string, gameId: string): Promise<UserPublic[]> {
  const res = await fetch(`${BASE}/game/${gameId}/members/users`, { headers: auth(token) });
  return handle(res);
}

// --- Leaderboard ---

export async function getLeaderboard(token: string, gameId: string): Promise<MemberScore[]> {
  const res = await fetch(`${BASE}/game/${gameId}/scores`, { headers: auth(token) });
  return handle(res);
}

export async function deletePrediction(token: string, gameId: string, sessionId: string): Promise<void> {
  const res = await fetch(`${BASE}/game/${gameId}/f1session/${sessionId}/predict`, {
    method: 'DELETE',
    headers: auth(token),
  });
  if (!res.ok) await handle(res);
}

export async function setFirstDnf(token: string, gameId: string, sessionId: string, driverId: string): Promise<void> {
  const res = await fetch(`${BASE}/game/${gameId}/f1session/${sessionId}/dnf`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...auth(token) },
    body: JSON.stringify({ driver_id: driverId }),
  });
  if (!res.ok) await handle(res);
}
