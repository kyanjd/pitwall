import { useState, useEffect } from 'react';
import { getMe, UserPublic, GamePublic } from './api';
import AuthPage from './pages/Auth';
import GamesPage from './pages/Games';
import GamePage from './pages/Game';

type View = 'auth' | 'games' | 'game';

export default function App() {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'));
  const [user, setUser] = useState<UserPublic | null>(null);
  const [view, setView] = useState<View>(token ? 'games' : 'auth');
  const [selectedGame, setSelectedGame] = useState<GamePublic | null>(null);

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
    </>
  );
}
