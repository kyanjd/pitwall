import { useState, useEffect, FormEvent } from 'react';
import { getMe, updateName, changePassword, UserPublic, GamePublic } from './api';
import AuthPage from './pages/Auth';
import GamesPage from './pages/Games';
import GamePage from './pages/Game';

type View = 'auth' | 'games' | 'game';

export default function App() {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'));
  const [user, setUser] = useState<UserPublic | null>(null);
  const [view, setView] = useState<View>(token ? 'games' : 'auth');
  const [selectedGame, setSelectedGame] = useState<GamePublic | null>(null);
  const [showAccount, setShowAccount] = useState(false);

  // Name
  const [name, setName] = useState('');
  const [nameError, setNameError] = useState('');
  const [nameSuccess, setNameSuccess] = useState(false);
  const [nameLoading, setNameLoading] = useState(false);

  // Password
  const [currentPw, setCurrentPw] = useState('');
  const [newPw, setNewPw] = useState('');
  const [confirmPw, setConfirmPw] = useState('');
  const [pwError, setPwError] = useState('');
  const [pwSuccess, setPwSuccess] = useState(false);
  const [pwLoading, setPwLoading] = useState(false);

  useEffect(() => {
    if (!token) return;
    getMe(token).then(setUser).catch(() => handleLogout());
  }, [token]);

  function handleLogin(newToken: string) {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setView('games');
  }

  function handleLogout() {
    localStorage.removeItem('token');
    setToken(null); setUser(null);
    setView('auth'); setSelectedGame(null);
  }

  function openAccount() {
    setName(user?.name ?? '');
    setNameError(''); setNameSuccess(false);
    setCurrentPw(''); setNewPw(''); setConfirmPw('');
    setPwError(''); setPwSuccess(false);
    setShowAccount(true);
  }

  async function handleUpdateName(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setNameLoading(true); setNameError(''); setNameSuccess(false);
    try {
      const updated = await updateName(token, name);
      setUser(updated);
      setNameSuccess(true);
    } catch (err: unknown) {
      setNameError(err instanceof Error ? err.message : 'Failed to update name');
    } finally {
      setNameLoading(false);
    }
  }

  async function handleChangePassword(e: FormEvent) {
    e.preventDefault();
    if (newPw !== confirmPw) { setPwError('Passwords do not match.'); return; }
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
            <button className="btn-secondary btn-sm" onClick={() => setView('games')}>← Games</button>
          )}
          <span>{user?.name ?? user?.email}</span>
          <button className="btn-secondary btn-sm" onClick={openAccount}>Account</button>
          <button className="btn-secondary btn-sm" onClick={handleLogout}>Log out</button>
        </div>
      </header>

      <main className="container">
        {view === 'games' && <GamesPage token={token} onSelectGame={g => { setSelectedGame(g); setView('game'); }} />}
        {view === 'game' && selectedGame && (
          <GamePage token={token} game={selectedGame} currentUserId={user?.id ?? ''} />
        )}
      </main>

      {showAccount && (
        <div className="modal-backdrop" onClick={() => setShowAccount(false)}>
          <div className="modal" style={{ maxWidth: 420 }} onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1rem' }}>Account</h2>
              <button className="btn-secondary btn-sm" onClick={() => setShowAccount(false)}>✕</button>
            </div>

            {/* Name */}
            <p style={{ fontSize: '0.7rem', color: '#666', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>Display name</p>
            <form onSubmit={handleUpdateName} style={{ marginBottom: '1.75rem' }}>
              <div className="form-group">
                <input type="text" value={name} onChange={e => setName(e.target.value)} required placeholder="Your name" />
              </div>
              {nameError && <p className="error">{nameError}</p>}
              {nameSuccess && <p className="success">Name updated.</p>}
              <button type="submit" className="btn-primary btn-sm" disabled={nameLoading}>
                {nameLoading ? 'Saving…' : 'Update name'}
              </button>
            </form>

            <hr style={{ border: 'none', borderTop: '1px solid #2a2a2a', marginBottom: '1.75rem' }} />

            {/* Password */}
            <p style={{ fontSize: '0.7rem', color: '#666', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>Change password</p>
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
              <button type="submit" className="btn-primary btn-sm" disabled={pwLoading}>
                {pwLoading ? 'Saving…' : 'Update password'}
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
