import { useState, useEffect, FormEvent } from 'react';
import { getGames, createGame, joinGame, GamePublic } from '../api';

interface Props {
  token: string;
  onSelectGame: (game: GamePublic) => void;
}

export default function GamesPage({ token, onSelectGame }: Props) {
  const [games, setGames] = useState<GamePublic[]>([]);
  const [loading, setLoading] = useState(true);

  // Create game
  const [createName, setCreateName] = useState('');
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

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setCreateError('');
    setCreating(true);
    try {
      const game = await createGame(token, createName);
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
                  Invite code: <span className="invite-code" style={{ fontSize: '0.8rem' }}>{game.invite_code}</span>
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
