import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { mockUsers } from '../utils/mockUsers';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faLock, faInfoCircle } from '@fortawesome/free-solid-svg-icons';
import './AuthDialog.css';

interface MockAuthDialogProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'login' | 'register';
}

const MockAuthDialog: React.FC<MockAuthDialogProps> = ({ isOpen, onClose, initialMode = 'login' }) => {
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);
  const [showTestCredentials, setShowTestCredentials] = useState(false);
  const { login, register } = useAuth();

  // Sync internal mode state with initialMode prop
  useEffect(() => {
    setMode(initialMode);
  }, [initialMode]);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (mode === 'register') {
      if (password !== confirmPassword) {
        setError('Passwords do not match');
        return;
      }

      if (password.length < 6) {
        setError('Password must be at least 6 characters long');
        return;
      }
    }

    setLoading(true);
    setError('');
    
    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await register(email, password);
      }
      onClose();
      // Reset form
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      setError('');
    } catch (error: any) {
      console.error('Authentication error:', error);
      setError(error.message || (mode === 'login' ? 'Failed to sign in' : 'Failed to create account'));
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async (credentials: { email: string; password: string }) => {
    setEmail(credentials.email);
    setPassword(credentials.password);
    setError('');
    
    try {
      setLoading(true);
      await login(credentials.email, credentials.password);
      onClose();
      // Reset form
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      setError('');
    } catch (error: any) {
      setError('Quick login failed');
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
    setError('');
    setEmail('');
    setPassword('');
    setConfirmPassword('');
  };

  if (!isOpen) return null;

  return (
    <div className="auth-dialog-overlay" onClick={onClose}>
      <div className="auth-dialog-container" onClick={(e) => e.stopPropagation()}>
        <button className="auth-dialog-close" onClick={onClose}>
          ×
        </button>
        
        <div className="auth-dialog-header">
          <h2 className="auth-dialog-title">
            {mode === 'login' ? 'Welcome Back!' : 'Create Account'}
          </h2>
          <p className="auth-dialog-subtitle">
            {mode === 'login' 
              ? 'Login to manage your account and get personalized recommendations.' 
              : 'Join us and start shopping today!'
            }
          </p>
        </div>

        {/* Test Credentials Section */}
        <div className="test-credentials-section">
          <button
            type="button"
            onClick={() => setShowTestCredentials(!showTestCredentials)}
            className="test-credentials-toggle"
          >
            <FontAwesomeIcon icon={faInfoCircle} />
            {showTestCredentials ? 'Hide' : 'Show'} Test Accounts
          </button>
          
          {showTestCredentials && (
            <div className="test-credentials-list">
              <h4>Quick Login Options:</h4>
              <div className="test-credentials-grid">
                {mockUsers.slice(0, 3).map((user, index) => (
                  <div key={index} className="test-credential-item">
                    <strong>{user.displayName}</strong>
                    <p>{user.description}</p>
                    <button
                      onClick={() => handleQuickLogin({ email: user.email, password: user.password })}
                      className="quick-login-btn"
                      disabled={loading}
                    >
                      Quick Login
                    </button>
                  </div>
                ))}
              </div>
              
              <div className="manual-credentials">
                <h4>Manual Login Credentials:</h4>
                <div className="credentials-info">
                  <p><strong>Email:</strong> {mockUsers[0].email}</p>
                  <p><strong>Password:</strong> {mockUsers[0].password}</p>
                  <p><em>Or use any of the other test accounts listed above</em></p>
                </div>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="auth-dialog-error">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-dialog-form">
          <div className="auth-dialog-form-group">
            <div className="auth-dialog-input-wrapper">
              <FontAwesomeIcon icon={faUser} className="auth-dialog-input-icon" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="auth-dialog-input"
                placeholder="Email"
              />
            </div>
          </div>

          <div className="auth-dialog-form-group">
            <div className="auth-dialog-input-wrapper">
              <FontAwesomeIcon icon={faLock} className="auth-dialog-input-icon" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="auth-dialog-input"
                placeholder="Password"
              />
            </div>
          </div>

          {mode === 'register' && (
            <div className="auth-dialog-form-group">
              <div className="auth-dialog-input-wrapper">
                <FontAwesomeIcon icon={faLock} className="auth-dialog-input-icon" />
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  className="auth-dialog-input"
                  placeholder="Confirm Password"
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className={`auth-dialog-submit ${loading ? 'auth-dialog-submit-loading' : ''}`}
          >
            {loading 
              ? (mode === 'login' ? 'Signing In...' : 'Creating Account...') 
              : (mode === 'login' ? 'Login' : 'Create Account')
            }
          </button>
        </form>

        <div className="auth-dialog-switch">
          <span className="auth-dialog-switch-text">
            {mode === 'login' 
              ? "Don't have an account? " 
              : "Already have an account? "
            }
          </span>
          <button 
            onClick={switchMode}
            className="auth-dialog-switch-button"
            type="button"
          >
            {mode === 'login' ? 'Sign Up' : 'Sign In'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default MockAuthDialog;
