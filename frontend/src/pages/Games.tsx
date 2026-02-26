import { useState, useEffect, FormEvent } from 'react';
import { getGames, createGame, joinGame, getSeasons, getSessions, GamePublic, F1SessionPublic } from '../api';

function formatCountdown(targetMs: number, nowMs: number): string {
  const diff = targetMs - nowMs;
  if (diff <= 0) return 'Live';
  const d = Math.floor(diff / 86400000);
  const h = Math.floor((diff % 86400000) / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  const s = Math.floor((diff % 60000) / 1000);
  if (d > 0) return `${d}d ${h}h ${m}m`;
  if (h > 0) return `${h}h ${m}m ${s}s`;
  return `${m}m ${s}s`;
}

interface Props {
  token: string;
  onSelectGame: (game: GamePublic) => void;
}

export default function GamesPage({ token, onSelectGame }: Props) {
  const [games, setGames] = useState<GamePublic[]>([]);
  const [loading, setLoading] = useState(true);

  // Countdown
  const [upcomingSessions, setUpcomingSessions] = useState<F1SessionPublic[]>([]);
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);

  // Create game
  const [createName, setCreateName] = useState('');
  const [createSeason, setCreateSeason] = useState<number>(2026);
  const [availableSeasons, setAvailableSeasons] = useState<number[]>([2026]);
  const [createError, setCreateError] = useState('');
  const [creating, setCreating] = useState(false);

  // Join game
  const [inviteCode, setInviteCode] = useState('');
  const [joinError, setJoinError] = useState('');
  const [joining, setJoining] = useState(false);

  useEffect(() => {
    getGames(token)
      .then(setGames)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  useEffect(() => {
    getSeasons(token).then(s => {
      setAvailableSeasons(s);
      if (s.length > 0) {
        const latest = s[s.length - 1];
        setCreateSeason(latest);
        getSessions(token, latest).then(setUpcomingSessions).catch(() => {});
      }
    }).catch(() => {});
  }, [token]);

  const upcoming = upcomingSessions
    .filter(s => new Date(s.date).getTime() > now)
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  const nextRace = upcoming.find(s => s.type === 'Race');
  const nextQuali = upcoming.find(s => s.type === 'Qualifying');

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setCreateError('');
    setCreating(true);
    try {
      const game = await createGame(token, createName, createSeason);
      setGames(prev => [game, ...prev]);
      setCreateName('');
    } catch (err: unknown) {
      setCreateError(err instanceof Error ? err.message : 'Failed to create game');
    } finally {
      setCreating(false);
    }
  }

  async function handleJoin(e: FormEvent) {
    e.preventDefault();
    setJoinError('');
    setJoining(true);
    try {
      const game = await joinGame(token, inviteCode.trim().toUpperCase());
      setGames(prev => prev.some(g => g.id === game.id) ? prev : [game, ...prev]);
      setInviteCode('');
    } catch (err: unknown) {
      setJoinError(err instanceof Error ? err.message : 'Failed to join game');
    } finally {
      setJoining(false);
    }
  }

  return (
    <>
      {/* Countdown panels */}
      {(nextQuali || nextRace) && (
        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '2rem' }}>
          {nextQuali && (
            <div style={{ flex: 1, background: '#111', border: '1px solid #2a2a2a', borderRadius: '8px', padding: '0.875rem 1rem' }}>
              <div style={{ fontSize: '0.65rem', color: '#666', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.25rem' }}>Next Qualifying</div>
              <div style={{ fontSize: '0.85rem', color: '#ccc', marginBottom: '0.35rem' }}>{nextQuali.race_name}</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#e10600', fontFamily: 'monospace' }}>
                {formatCountdown(new Date(nextQuali.date).getTime(), now)}
              </div>
            </div>
          )}
          {nextRace && (
            <div style={{ flex: 1, background: '#111', border: '1px solid #2a2a2a', borderRadius: '8px', padding: '0.875rem 1rem' }}>
              <div style={{ fontSize: '0.65rem', color: '#666', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.25rem' }}>Next Race</div>
              <div style={{ fontSize: '0.85rem', color: '#ccc', marginBottom: '0.35rem' }}>{nextRace.race_name}</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#e10600', fontFamily: 'monospace' }}>
                {formatCountdown(new Date(nextRace.date).getTime(), now)}
              </div>
            </div>
          )}
        </div>
      )}

      <h2 style={{ marginBottom: '1.5rem', fontSize: '1.1rem', color: '#ccc' }}>Your Games</h2>

      {/* Games list */}
      {loading ? (
        <p className="empty">Loading…</p>
      ) : games.length === 0 ? (
        <p className="empty">No games yet — create or join one below.</p>
      ) : (
        <div style={{ marginBottom: '2rem' }}>
          {games.map(game => (
            <div key={game.id} className="list-item" onClick={() => onSelectGame(game)}>
              <div>
                <div className="list-item-title">{game.name}</div>
                <div className="list-item-sub">
                  {game.season} · Invite code: <span className="invite-code" style={{ fontSize: '0.8rem' }}>{game.invite_code}</span>
                </div>
              </div>
              <span style={{ color: '#555', fontSize: '0.75rem' }}>Open →</span>
            </div>
          ))}
        </div>
      )}

      {/* Create + Join side by side */}
      <div className="row">
        <div className="card">
          <h2>Create Game</h2>
          <form onSubmit={handleCreate}>
            <div className="form-group">
              <label>Game name</label>
              <input
                type="text"
                value={createName}
                onChange={e => setCreateName(e.target.value)}
                required
                placeholder="My F1 League"
              />
            </div>
            <div className="form-group">
              <label>Season</label>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {availableSeasons.map(s => (
                  <button
                    key={s}
                    type="button"
                    className={createSeason === s ? 'btn-primary btn-sm' : 'btn-secondary btn-sm'}
                    onClick={() => setCreateSeason(s)}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
            {createError && <p className="error">{createError}</p>}
            <button type="submit" className="btn-primary" disabled={creating}>
              {creating ? 'Creating…' : 'Create'}
            </button>
          </form>
        </div>

        <div className="card">
          <h2>Join Game</h2>
          <form onSubmit={handleJoin}>
            <div className="form-group">
              <label>Invite code</label>
              <input
                type="text"
                value={inviteCode}
                onChange={e => setInviteCode(e.target.value)}
                required
                placeholder="ABC123"
                maxLength={6}
                style={{ textTransform: 'uppercase', letterSpacing: '0.1em', fontFamily: 'monospace' }}
              />
            </div>
            {joinError && <p className="error">{joinError}</p>}
            <button type="submit" className="btn-primary" disabled={joining}>
              {joining ? 'Joining…' : 'Join'}
            </button>
          </form>
        </div>
      </div>
    </>
  );
}
