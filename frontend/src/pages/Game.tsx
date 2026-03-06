import { useState, useEffect } from 'react';
import {
  GamePublic, F1SessionPublic, Driver, MemberScore, PredictionPublic, ResultPublic,
  getSessions, getDrivers, getSessionResults, predict, deletePrediction, getLeaderboard,
  getMyPrediction, getMembers, getGamePredictions, setFirstDnf,
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

export default function GamePage({ token, game, currentUserId }: Props) {
  const [tab, setTab] = useState<Tab>('sessions');

  // Countdown
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);

  // Sessions
  const [allSessions, setAllSessions] = useState<F1SessionPublic[]>([]);
  const [sessions, setSessions] = useState<F1SessionPublic[]>([]);
  const [selectedSession, setSelectedSession] = useState<F1SessionPublic | null>(null);
  const [loadingSessions, setLoadingSessions] = useState(false);

  // Predict
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [results, setResults] = useState<ResultPublic[]>([]);
  const [sessionPredictions, setSessionPredictions] = useState<PredictionPublic[]>([]);
  const [loadingDrivers, setLoadingDrivers] = useState(false);
  const [posDriverId, setPosDriverId] = useState('');
  const [dnfDriverId, setDnfDriverId] = useState('');
  const [existingPrediction, setExistingPrediction] = useState<PredictionPublic | null>(null);
  const [predicting, setPredicting] = useState(false);
  const [predictError, setPredictError] = useState('');
  const [predictSuccess, setPredictSuccess] = useState(false);

  // DNF override (owner only)
  const [dnfOverrideDriverId, setDnfOverrideDriverId] = useState('');
  const [settingDnf, setSettingDnf] = useState(false);
  const [dnfOverrideSuccess, setDnfOverrideSuccess] = useState(false);
  const [dnfOverrideError, setDnfOverrideError] = useState('');

  // Predicted sessions (for session list indicators)
  const [predictedSessionIds, setPredictedSessionIds] = useState<Set<string>>(new Set());

  // Leaderboard
  const [leaderboard, setLeaderboard] = useState<MemberScore[]>([]);
  const [loadingLeaderboard, setLoadingLeaderboard] = useState(false);
  const [memberNames, setMemberNames] = useState<Record<string, string>>({});
  const [predictionCounts, setPredictionCounts] = useState<Record<string, number>>({});

  // Load sessions for the game's season on mount
  useEffect(() => {
    setLoadingSessions(true);
    setSessions([]);
    setSelectedSession(null);
    getSessions(token, game.season)
      .then(all => {
        setAllSessions(all);
        const races = all.filter(s => s.type === 'Race');
        setSessions(races);
        const savedId = localStorage.getItem(`pitwall_session_${game.id}`);
        if (savedId) {
          const saved = races.find(s => s.id === savedId);
          if (saved) setSelectedSession(saved);
        }
      })
      .catch(() => {})
      .finally(() => setLoadingSessions(false));
  }, [token, game.id, game.season]);

  // Load drivers + existing prediction when a session is selected
  useEffect(() => {
    if (!selectedSession) return;
    setLoadingDrivers(true);
    setDrivers([]);
    setPosDriverId('');
    setDnfDriverId('');
    setExistingPrediction(null);
    setResults([]);
    setSessionPredictions([]);
    setDnfOverrideDriverId('');
    setDnfOverrideSuccess(false);
    setDnfOverrideError('');

    const loadDrivers = getDrivers(token, selectedSession.id)
      .then(setDrivers)
      .catch(() => {});

    const loadPrediction = getMyPrediction(token, game.id, selectedSession.id)
      .then(pred => {
        if (pred) {
          setExistingPrediction(pred);
          setPosDriverId(pred.position_driver_id);
          setDnfDriverId(pred.dnf_driver_id);
        }
      });

    const loadResults = getSessionResults(token, selectedSession.id)
      .then(setResults)
      .catch(() => {});

    const sessionId = selectedSession.id;
    const loadSessionPredictions = getGamePredictions(token, game.id)
      .then(all => setSessionPredictions(all.filter(p => p.f1session_id === sessionId)))
      .catch(() => {});

    Promise.all([loadDrivers, loadPrediction, loadResults, loadSessionPredictions]).finally(() => setLoadingDrivers(false));
  }, [token, selectedSession, game.id]);

  // Load which sessions the current user has predicted + member names
  useEffect(() => {
    getGamePredictions(token, game.id).then(predictions => {
      const ids = new Set(predictions.filter(p => p.user_id === currentUserId).map(p => p.f1session_id));
      setPredictedSessionIds(ids);
    }).catch(() => {});
    getMembers(token, game.id).then(members => {
      const names: Record<string, string> = {};
      members.forEach(m => { names[m.id] = m.name; });
      setMemberNames(names);
    }).catch(() => {});
  }, [token, game.id, currentUserId]);

  // Load leaderboard + member names when switching to that tab
  useEffect(() => {
    if (tab !== 'leaderboard') return;
    setLoadingLeaderboard(true);

    Promise.all([
      getLeaderboard(token, game.id),
      getMembers(token, game.id),
      getGamePredictions(token, game.id),
    ]).then(([scores, members, predictions]) => {
      setLeaderboard(scores);
      const names: Record<string, string> = {};
      members.forEach(m => { names[m.id] = m.name; });
      setMemberNames(names);
      const counts: Record<string, number> = {};
      predictions.forEach(p => { counts[p.user_id] = (counts[p.user_id] ?? 0) + 1; });
      setPredictionCounts(counts);
    }).catch(() => {}).finally(() => setLoadingLeaderboard(false));
  }, [tab, token, game.id]);

  function handleSelectSession(session: F1SessionPublic) {
    setSelectedSession(session);
    localStorage.setItem(`pitwall_session_${game.id}`, session.id);
    setPredictSuccess(false);
    setPredictError('');
    setTab('predict');
  }

  async function handleSetDnf() {
    if (!selectedSession || !dnfOverrideDriverId) return;
    setSettingDnf(true);
    setDnfOverrideSuccess(false);
    setDnfOverrideError('');
    try {
      await setFirstDnf(token, game.id, selectedSession.id, dnfOverrideDriverId);
      setDnfOverrideSuccess(true);
      const refreshed = await getSessionResults(token, selectedSession.id);
      setResults(refreshed);
    } catch (err: unknown) {
      setDnfOverrideError(err instanceof Error ? err.message : 'Failed to set DNF');
    } finally {
      setSettingDnf(false);
    }
  }

  async function handleClearPrediction() {
    if (!selectedSession || !existingPrediction) return;
    try {
      await deletePrediction(token, game.id, selectedSession.id);
      setExistingPrediction(null);
      setPosDriverId('');
      setDnfDriverId('');
      setPredictedSessionIds(prev => { const s = new Set(prev); s.delete(selectedSession.id); return s; });
      const allPreds = await getGamePredictions(token, game.id);
      setSessionPredictions(allPreds.filter(p => p.f1session_id === selectedSession.id));
    } catch (err: unknown) {
      setPredictError(err instanceof Error ? err.message : 'Failed to clear prediction');
    }
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
      setPredictedSessionIds(prev => new Set([...prev, selectedSession.id]));
      const [pred, allPreds] = await Promise.all([
        getMyPrediction(token, game.id, selectedSession.id),
        getGamePredictions(token, game.id),
      ]);
      if (pred) setExistingPrediction(pred);
      setSessionPredictions(allPreds.filter(p => p.f1session_id === selectedSession.id));
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

      {/* Countdown */}
      {(() => {
        const upcoming = allSessions
          .filter(s => new Date(s.date).getTime() > now)
          .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
        const nextRace = upcoming.find(s => s.type === 'Race');
        const nextQuali = upcoming.find(s => s.type === 'Qualifying');
        if (!nextRace && !nextQuali) return null;
        return (
          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem' }}>
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
        );
      })()}

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
          {loadingSessions ? (
            <p className="empty">Loading sessions…</p>
          ) : sessions.length === 0 ? (
            <p className="empty">No sessions found for {game.season}. Make sure the backend has ingested F1 data.</p>
          ) : (
            sessions.map(session => {
              const predicted = predictedSessionIds.has(session.id);
              return (
                <div
                  key={session.id}
                  className={`list-item ${selectedSession?.id === session.id ? 'selected' : ''}`}
                  onClick={() => handleSelectSession(session)}
                >
                  <div>
                    <div className="list-item-title">{sessionLabel(session)}</div>
                    <div className="list-item-sub">{new Date(session.date).toLocaleDateString()}</div>
                  </div>
                  {predicted
                    ? <span style={{ color: '#51cf66', fontSize: '0.75rem' }}>✓ Predicted</span>
                    : <span style={{ color: '#555', fontSize: '0.75rem' }}>Predict →</span>}
                </div>
              );
            })
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
              {existingPrediction && (
                <p style={{ fontSize: '0.8rem', color: '#51cf66', marginBottom: '1.25rem' }}>
                  You've already predicted this session — your picks are shown below. Submitting will update them.
                </p>
              )}
              {(() => {
                const others = sessionPredictions.filter(p => p.user_id !== currentUserId);
                const posByDriver = new Map(others.map(p => [p.position_driver_id, p.user_id]));
                const dnfByDriver = new Map(others.map(p => [p.dnf_driver_id, p.user_id]));
                return (
                  <>
                    <div className="predict-section">
                      <h3>Who finishes 10th?</h3>
                      <div className="driver-grid">
                        {drivers.map(d => {
                          const takenBy = posByDriver.get(d.id);
                          return (
                            <div
                              key={d.id}
                              className={`driver-card ${posDriverId === d.id ? 'selected' : ''}`}
                              onClick={() => !takenBy && setPosDriverId(d.id)}
                              style={takenBy ? { opacity: 0.35, cursor: 'not-allowed' } : undefined}
                            >
                              <div className="driver-code">{d.code}</div>
                              <div className="driver-name">{d.first_name} {d.last_name}</div>
                              {takenBy && <div style={{ fontSize: '0.55rem', color: '#777', marginTop: '2px' }}>
                                {memberNames[takenBy] ?? 'Taken'}
                              </div>}
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    <div className="predict-section">
                      <h3>Who DNFs first?</h3>
                      <div className="driver-grid">
                        {drivers.map(d => {
                          const takenBy = dnfByDriver.get(d.id);
                          return (
                            <div
                              key={d.id}
                              className={`driver-card ${dnfDriverId === d.id ? 'selected' : ''}`}
                              onClick={() => !takenBy && setDnfDriverId(d.id)}
                              style={takenBy ? { opacity: 0.35, cursor: 'not-allowed' } : undefined}
                            >
                              <div className="driver-code">{d.code}</div>
                              <div className="driver-name">{d.first_name} {d.last_name}</div>
                              {takenBy && <div style={{ fontSize: '0.55rem', color: '#777', marginTop: '2px' }}>
                                {memberNames[takenBy] ?? 'Taken'}
                              </div>}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </>
                );
              })()}

              {predictError && <p className="error" style={{ marginBottom: '1rem' }}>{predictError}</p>}
              {predictSuccess && <p className="success" style={{ marginBottom: '1rem' }}>Prediction saved!</p>}

              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <button
                  className="btn-primary"
                  onClick={handlePredict}
                  disabled={predicting || !posDriverId || !dnfDriverId}
                >
                  {predicting ? 'Saving…' : 'Submit prediction'}
                </button>
                {existingPrediction && (
                  <button
                    className="btn-sm"
                    onClick={handleClearPrediction}
                    style={{ color: '#888', background: 'transparent', border: '1px solid #333' }}
                  >
                    Clear
                  </button>
                )}
              </div>

              {posDriverId && dnfDriverId && (
                <p style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: '#888' }}>
                  10th: <strong style={{ color: '#e8e8e8' }}>{drivers.find(d => d.id === posDriverId)?.code}</strong>
                  {' · '}
                  DNF: <strong style={{ color: '#e8e8e8' }}>{drivers.find(d => d.id === dnfDriverId)?.code}</strong>
                </p>
              )}

              {currentUserId === game.created_by && (
                <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid #2a2a2a' }}>
                  <p style={{ fontSize: '0.75rem', color: '#666', marginBottom: '0.75rem' }}>Override first DNF result</p>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <select
                      value={dnfOverrideDriverId}
                      onChange={e => setDnfOverrideDriverId(e.target.value)}
                      style={{ flex: 1 }}
                    >
                      <option value="">Select driver…</option>
                      {drivers.map(d => (
                        <option key={d.id} value={d.id}>{d.code} — {d.first_name} {d.last_name}</option>
                      ))}
                    </select>
                    <button
                      className="btn-primary btn-sm"
                      disabled={!dnfOverrideDriverId || settingDnf}
                      onClick={handleSetDnf}
                    >
                      {settingDnf ? 'Saving…' : 'Set DNF'}
                    </button>
                  </div>
                  {dnfOverrideSuccess && <p className="success" style={{ marginTop: '0.5rem', fontSize: '0.8rem' }}>DNF override saved.</p>}
                  {dnfOverrideError && <p className="error" style={{ marginTop: '0.5rem', fontSize: '0.8rem' }}>{dnfOverrideError}</p>}
                </div>
              )}

              {existingPrediction && results.length > 0 && (
                <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid #2a2a2a' }}>
                  <p style={{ fontSize: '0.75rem', color: '#666', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.75rem' }}>Race Results</p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                    {results.map(r => {
                      const isP10 = r.position === 10;
                      const isDnf = r.is_first_dnf;
                      const isMyPos = r.driver_id === existingPrediction.position_driver_id;
                      const isMyDnf = r.driver_id === existingPrediction.dnf_driver_id;

                      let rowBg = 'transparent';
                      let borderColor = 'transparent';
                      if (isP10) { rowBg = 'rgba(212, 175, 55, 0.08)'; borderColor = 'rgba(212, 175, 55, 0.4)'; }
                      if (isDnf) { rowBg = 'rgba(225, 6, 0, 0.08)'; borderColor = 'rgba(225, 6, 0, 0.4)'; }

                      return (
                        <div
                          key={r.driver_id}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.75rem',
                            padding: '0.35rem 0.6rem',
                            borderRadius: '4px',
                            background: rowBg,
                            border: `1px solid ${borderColor}`,
                          }}
                        >
                          <span style={{ width: '1.5rem', textAlign: 'right', fontSize: '0.75rem', color: '#555', fontFamily: 'monospace' }}>
                            {r.position_text ?? r.position}
                          </span>
                          <span style={{ width: '2.5rem', fontSize: '0.8rem', fontWeight: 600, color: isP10 ? '#d4af37' : isDnf ? '#e10600' : '#ccc', fontFamily: 'monospace' }}>
                            {r.driver_code}
                          </span>
                          <span style={{ flex: 1, fontSize: '0.75rem', color: '#888' }}>
                            {r.driver_first_name} {r.driver_last_name}
                          </span>
                          <div style={{ display: 'flex', gap: '0.35rem', alignItems: 'center' }}>
                            {isMyPos && (
                              <span style={{ fontSize: '0.6rem', padding: '1px 5px', borderRadius: '3px', background: 'rgba(212,175,55,0.15)', color: '#d4af37', border: '1px solid rgba(212,175,55,0.3)' }}>
                                10th pick
                              </span>
                            )}
                            {isMyDnf && (
                              <span style={{ fontSize: '0.6rem', padding: '1px 5px', borderRadius: '3px', background: 'rgba(225,6,0,0.15)', color: '#e10600', border: '1px solid rgba(225,6,0,0.3)' }}>
                                DNF pick
                              </span>
                            )}
                            {isDnf && (
                              <span style={{ fontSize: '0.6rem', color: '#e10600' }}>DNF</span>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
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
                  <th>Predictions</th>
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
                        {memberNames[row.user_id] ?? shortId(row.user_id)}
                        {isMe && <span className="you-badge">YOU</span>}
                        {row.user_id === game.created_by && <span className="owner-badge">OWNER</span>}
                      </td>
                      <td style={{ color: '#888' }}>{predictionCounts[row.user_id] ?? 0}</td>
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
