import { useState, useEffect, FormEvent } from 'react';
import { getMe, changePassword, UserPublic, GamePublic } from './api';
import AuthPage from './pages/Auth';
import GamesPage from './pages/Games';
import GamePage from './pages/Game';

type View = 'auth' | 'games' | 'game';

export default function App() {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'));
  const [user, setUser] = useState<UserPublic | null>(null);
  const [view, setView] = useState<View>(token ? 'games' : 'auth');
  const [selectedGame, setSelectedGame] = useState<GamePublic | null>(null);

  // Change password modal
  const [showPwModal, setShowPwModal] = useState(false);
  const [currentPw, setCurrentPw] = useState('');
  const [newPw, setNewPw] = useState('');
  const [confirmPw, setConfirmPw] = useState('');
  const [pwError, setPwError] = useState('');
  const [pwSuccess, setPwSuccess] = useState(false);
  const [pwLoading, setPwLoading] = useState(false);

  useEffect(() => {
    if (!token) return;
    getMe(token)
      .then(setUser)
      .catch(() => handleLogout());
  }, [token]);

  function handleLogin(newToken: string) {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setView('games');
  }

  function handleLogout() {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setView('auth');
    setSelectedGame(null);
  }

  function handleSelectGame(game: GamePublic) {
    setSelectedGame(game);
    setView('game');
  }

  function openPwModal() {
    setCurrentPw(''); setNewPw(''); setConfirmPw('');
    setPwError(''); setPwSuccess(false);
    setShowPwModal(true);
  }

  async function handleChangePassword(e: FormEvent) {
    e.preventDefault();
    if (newPw !== confirmPw) { setPwError('New passwords do not match.'); return; }
    if (!token) return;
    setPwLoading(true); setPwError(''); setPwSuccess(false);
    try {
      await changePassword(token, currentPw, newPw);
      setPwSuccess(true);
      setCurrentPw(''); setNewPw(''); setConfirmPw('');
    } catch (err: unknown) {
      setPwError(err instanceof Error ? err.message : 'Failed to change password');
    } finally {
      setPwLoading(false);
    }
  }

  if (view === 'auth' || !token) {
    return <AuthPage onLogin={handleLogin} />;
  }

  return (
    <>
      <header className="header">
        <h1>PITWALL</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {view === 'game' && (
            <button className="btn-secondary btn-sm" onClick={() => setView('games')}>
              ← Games
            </button>
          )}
          <span>{user?.name ?? user?.email}</span>
          <button className="btn-secondary btn-sm" onClick={openPwModal}>
            Password
          </button>
          <button className="btn-secondary btn-sm" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>

      <main className="container">
        {view === 'games' && (
          <GamesPage token={token} onSelectGame={handleSelectGame} />
        )}
        {view === 'game' && selectedGame && (
          <GamePage token={token} game={selectedGame} currentUserId={user?.id ?? ''} />
        )}
      </main>

      {showPwModal && (
        <div className="modal-backdrop" onClick={() => setShowPwModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2 style={{ marginBottom: '1.25rem', fontSize: '1rem' }}>Change password</h2>
            <form onSubmit={handleChangePassword}>
              <div className="form-group">
                <label>Current password</label>
                <input type="password" value={currentPw} onChange={e => setCurrentPw(e.target.value)} required />
              </div>
              <div className="form-group">
                <label>New password</label>
                <input type="password" value={newPw} onChange={e => setNewPw(e.target.value)} required minLength={8} />
              </div>
              <div className="form-group">
                <label>Confirm new password</label>
                <input type="password" value={confirmPw} onChange={e => setConfirmPw(e.target.value)} required minLength={8} />
              </div>
              {pwError && <p className="error">{pwError}</p>}
              {pwSuccess && <p className="success">Password updated.</p>}
              <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
                <button type="submit" className="btn-primary" disabled={pwLoading}>
                  {pwLoading ? 'Saving…' : 'Update'}
                </button>
                <button type="button" className="btn-secondary" onClick={() => setShowPwModal(false)}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
