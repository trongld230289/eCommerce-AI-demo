import React, { useState, useEffect } from 'react';
import { signInWithEmailAndPassword, createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../utils/firebase';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFacebookF, faGoogle } from '@fortawesome/free-brands-svg-icons';
import { faUser, faLock } from '@fortawesome/free-solid-svg-icons';
import './AuthDialog.css';

interface AuthDialogProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'login' | 'register';
}

const AuthDialog: React.FC<AuthDialogProps> = ({ isOpen, onClose, initialMode = 'login' }) => {
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);

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
        await signInWithEmailAndPassword(auth, email, password);
      } else {
        await createUserWithEmailAndPassword(auth, email, password);
      }
      onClose();
      // Reset form
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      setError('');
    } catch (error: any) {
      console.error('Authentication error:', error);
      switch (error.code) {
        case 'auth/user-not-found':
        case 'auth/wrong-password':
        case 'auth/invalid-credential':
          setError('Invalid email or password');
          break;
        case 'auth/email-already-in-use':
          setError('This email is already registered');
          break;
        case 'auth/invalid-email':
          setError('Invalid email address');
          break;
        case 'auth/weak-password':
          setError('Password is too weak');
          break;
        case 'auth/too-many-requests':
          setError('Too many failed attempts. Please try again later');
          break;
        default:
          setError(mode === 'login' ? 'Failed to sign in' : 'Failed to create account');
      }
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
              ? 'Login to manage your account.' 
              : 'Join us and start shopping today!'
            }
          </p>
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

          {mode === 'login' && (
            <div className="auth-dialog-forgot">
              <button 
                type="button"
                className="auth-dialog-forgot-link"
                onClick={() => alert('Password reset functionality will be implemented soon!')}
              >
                Forgot Password?
              </button>
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
              ? "Do not have an account? " 
              : "Already have an account? "
            }
          </span>
          <button 
            onClick={switchMode}
            className="auth-dialog-switch-button"
            type="button"
          >
            {mode === 'login' ? 'Signup' : 'Sign In'}
          </button>
        </div>

        <div className="auth-dialog-divider">
          <span>OR</span>
        </div>

        <div className="auth-dialog-social">
          <button className="auth-dialog-social-button auth-dialog-facebook">
            <FontAwesomeIcon icon={faFacebookF} className="auth-dialog-social-icon" />
            Facebook
          </button>
          <button className="auth-dialog-social-button auth-dialog-google">
            <FontAwesomeIcon icon={faGoogle} className="auth-dialog-social-icon" />
            Google
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthDialog;
