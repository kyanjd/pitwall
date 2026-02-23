import { useState, FormEvent } from 'react';
import { login, register } from '../api';

interface Props {
  onLogin: (token: string) => void;
}

export default function AuthPage({ onLogin }: Props) {
  const [tab, setTab] = useState<'login' | 'register'>('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (tab === 'register') {
        await register(name, email, password);
      }
      const token = await login(email, password);
      onLogin(token.access_token);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }

  function switchTab(next: 'login' | 'register') {
    setTab(next);
    setError('');
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <div style={{ width: '100%', maxWidth: '380px', padding: '1rem' }}>
        <h1 style={{ textAlign: 'center', color: '#e10600', marginBottom: '2rem', letterSpacing: '0.1em' }}>
          PITWALL
        </h1>

        <div className="card">
          <div className="auth-tabs">
            <button
              className={`auth-tab ${tab === 'login' ? 'active' : ''}`}
              style={{ flex: 1 }}
              onClick={() => switchTab('login')}
            >
              Log in
            </button>
            <button
              className={`auth-tab ${tab === 'register' ? 'active' : ''}`}
              style={{ flex: 1 }}
              onClick={() => switchTab('register')}
            >
              Register
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            {tab === 'register' && (
              <div className="form-group">
                <label>Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  required
                  placeholder="Your name"
                />
              </div>
            )}
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                minLength={8}
                placeholder="••••••••"
              />
            </div>
            {error && <p className="error">{error}</p>}
            <button
              type="submit"
              className="btn-primary"
              style={{ width: '100%', marginTop: '0.5rem' }}
              disabled={loading}
            >
              {loading ? 'Please wait…' : tab === 'login' ? 'Log in' : 'Create account'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
