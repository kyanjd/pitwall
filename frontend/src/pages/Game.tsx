import { useState, useEffect } from 'react';
import {
  GamePublic, F1SessionPublic, Driver, MemberScore,
  getSeasons, getSessions, getDrivers, predict, getLeaderboard,
} from '../api';

interface Props {
  token: string;
  game: GamePublic;
  currentUserId: string;
}

type Tab = 'sessions' | 'predict' | 'leaderboard';

function shortId(id: string) {
  return id.slice(0, 8);
}

export default function GamePage({ token, game, currentUserId }: Props) {
  const [tab, setTab] = useState<Tab>('sessions');

  // Sessions
  const [seasons, setSeasons] = useState<number[]>([]);
  const [selectedSeason, setSelectedSeason] = useState<number | null>(null);
  const [sessions, setSessions] = useState<F1SessionPublic[]>([]);
  const [selectedSession, setSelectedSession] = useState<F1SessionPublic | null>(null);
  const [loadingSessions, setLoadingSessions] = useState(false);

  // Predict
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [loadingDrivers, setLoadingDrivers] = useState(false);
  const [posDriverId, setPosDriverId] = useState('');
  const [dnfDriverId, setDnfDriverId] = useState('');
  const [predicting, setPredicting] = useState(false);
  const [predictError, setPredictError] = useState('');
  const [predictSuccess, setPredictSuccess] = useState(false);

  // Leaderboard
  const [leaderboard, setLeaderboard] = useState<MemberScore[]>([]);
  const [loadingLeaderboard, setLoadingLeaderboard] = useState(false);

  // Load seasons on mount
  useEffect(() => {
    getSeasons(token).then(s => {
      setSeasons(s);
      if (s.length > 0) setSelectedSeason(s[s.length - 1]); // latest season
    }).catch(() => {});
  }, [token]);

  // Load sessions when season changes
  useEffect(() => {
    if (!selectedSeason) return;
    setLoadingSessions(true);
    setSessions([]);
    setSelectedSession(null);
    getSessions(token, selectedSeason)
      .then(setSessions)
      .catch(() => {})
      .finally(() => setLoadingSessions(false));
  }, [token, selectedSeason]);

  // Load drivers when a session is selected and we go to predict tab
  useEffect(() => {
    if (!selectedSession) return;
    setLoadingDrivers(true);
    setDrivers([]);
    setPosDriverId('');
    setDnfDriverId('');
    getDrivers(token, selectedSession.id)
      .then(setDrivers)
      .catch(() => {})
      .finally(() => setLoadingDrivers(false));
  }, [token, selectedSession]);

  // Load leaderboard when switching to that tab
  useEffect(() => {
    if (tab !== 'leaderboard') return;
    setLoadingLeaderboard(true);
    getLeaderboard(token, game.id)
      .then(setLeaderboard)
      .catch(() => {})
      .finally(() => setLoadingLeaderboard(false));
  }, [tab, token, game.id]);

  function handleSelectSession(session: F1SessionPublic) {
    setSelectedSession(session);
    setPredictSuccess(false);
    setPredictError('');
    setTab('predict');
  }

  async function handlePredict() {
    if (!selectedSession || !posDriverId || !dnfDriverId) return;
    if (posDriverId === dnfDriverId) {
      setPredictError('Position driver and DNF driver must be different.');
      return;
    }
    setPredicting(true);
    setPredictError('');
    setPredictSuccess(false);
    try {
      await predict(token, game.id, selectedSession.id, posDriverId, dnfDriverId);
      setPredictSuccess(true);
    } catch (err: unknown) {
      setPredictError(err instanceof Error ? err.message : 'Failed to submit prediction');
    } finally {
      setPredicting(false);
    }
  }

  const sessionLabel = (s: F1SessionPublic) =>
    `${s.race_name} — ${s.type} (R${s.race_round})`;

  return (
    <>
      {/* Game header */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.25rem', marginBottom: '0.25rem' }}>{game.name}</h2>
        <span style={{ fontSize: '0.8rem', color: '#666' }}>
          Invite code: <span className="invite-code" style={{ fontSize: '0.85rem' }}>{game.invite_code}</span>
        </span>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button className={`tab ${tab === 'sessions' ? 'active' : ''}`} onClick={() => setTab('sessions')}>
          Sessions
        </button>
        <button className={`tab ${tab === 'predict' ? 'active' : ''}`} onClick={() => setTab('predict')} disabled={!selectedSession}>
          Predict{selectedSession ? `: ${selectedSession.type}` : ''}
        </button>
        <button className={`tab ${tab === 'leaderboard' ? 'active' : ''}`} onClick={() => setTab('leaderboard')}>
          Leaderboard
        </button>
      </div>

      {/* Sessions tab */}
      {tab === 'sessions' && (
        <div>
          {/* Season picker */}
          {seasons.length > 1 && (
            <div style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem' }}>
              {seasons.map(s => (
                <button
                  key={s}
                  className={selectedSeason === s ? 'btn-primary btn-sm' : 'btn-secondary btn-sm'}
                  onClick={() => setSelectedSeason(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          {loadingSessions ? (
            <p className="empty">Loading sessions…</p>
          ) : sessions.length === 0 ? (
            <p className="empty">No sessions found for {selectedSeason}. Make sure the backend has ingested F1 data.</p>
          ) : (
            sessions.map(session => (
              <div
                key={session.id}
                className={`list-item ${selectedSession?.id === session.id ? 'selected' : ''}`}
                onClick={() => handleSelectSession(session)}
              >
                <div>
                  <div className="list-item-title">{sessionLabel(session)}</div>
                  <div className="list-item-sub">{new Date(session.date).toLocaleDateString()}</div>
                </div>
                <span style={{ color: '#555', fontSize: '0.75rem' }}>Predict →</span>
              </div>
            ))
          )}
        </div>
      )}

      {/* Predict tab */}
      {tab === 'predict' && selectedSession && (
        <div>
          <p style={{ color: '#888', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
            {sessionLabel(selectedSession)} · {new Date(selectedSession.date).toLocaleDateString()}
          </p>

          {loadingDrivers ? (
            <p className="empty">Loading drivers…</p>
          ) : drivers.length === 0 ? (
            <p className="empty">No drivers found for this session. Results may not be ingested yet.</p>
          ) : (
            <>
              <div className="predict-section">
                <h3>Who finishes 10th?</h3>
                <div className="driver-grid">
                  {drivers.map(d => (
                    <div
                      key={d.id}
                      className={`driver-card ${posDriverId === d.id ? 'selected' : ''}`}
                      onClick={() => setPosDriverId(d.id)}
                    >
                      <div className="driver-code">{d.code}</div>
                      <div className="driver-name">{d.first_name} {d.last_name}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="predict-section">
                <h3>Who DNFs first?</h3>
                <div className="driver-grid">
                  {drivers.map(d => (
                    <div
                      key={d.id}
                      className={`driver-card ${dnfDriverId === d.id ? 'selected' : ''}`}
                      onClick={() => setDnfDriverId(d.id)}
                    >
                      <div className="driver-code">{d.code}</div>
                      <div className="driver-name">{d.first_name} {d.last_name}</div>
                    </div>
                  ))}
                </div>
              </div>

              {predictError && <p className="error" style={{ marginBottom: '1rem' }}>{predictError}</p>}
              {predictSuccess && <p className="success" style={{ marginBottom: '1rem' }}>Prediction saved!</p>}

              <button
                className="btn-primary"
                onClick={handlePredict}
                disabled={predicting || !posDriverId || !dnfDriverId}
              >
                {predicting ? 'Saving…' : 'Submit prediction'}
              </button>

              {posDriverId && dnfDriverId && (
                <p style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: '#888' }}>
                  10th: <strong style={{ color: '#e8e8e8' }}>{drivers.find(d => d.id === posDriverId)?.code}</strong>
                  {' · '}
                  DNF: <strong style={{ color: '#e8e8e8' }}>{drivers.find(d => d.id === dnfDriverId)?.code}</strong>
                </p>
              )}
            </>
          )}
        </div>
      )}

      {/* Leaderboard tab */}
      {tab === 'leaderboard' && (
        <div>
          {loadingLeaderboard ? (
            <p className="empty">Loading…</p>
          ) : leaderboard.length === 0 ? (
            <p className="empty">No scores yet. Scores appear after race results are ingested.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Player</th>
                  <th>Position pts</th>
                  <th>DNF pts</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.map((row, i) => {
                  const isMe = row.user_id === currentUserId;
                  return (
                    <tr key={row.user_id}>
                      <td className="rank">{i + 1}</td>
                      <td>
                        {isMe ? (
                          <>You <span className="you-badge">YOU</span></>
                        ) : (
                          <span style={{ color: '#aaa', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                            {shortId(row.user_id)}…
                          </span>
                        )}
                      </td>
                      <td>{row.position_score}</td>
                      <td>{row.dnf_score}</td>
                      <td className="score-highlight">{row.total_score}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      )}
    </>
  );
}
