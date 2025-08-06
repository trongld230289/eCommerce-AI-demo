import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFacebookF, faGoogle } from '@fortawesome/free-brands-svg-icons';
import { useAuth } from '../AuthContext';
import './LoginDialog.css';

interface LoginDialogProps {
  isVisible: boolean;
  onClose: () => void;
}

const LoginDialog: React.FC<LoginDialogProps> = ({ isVisible, onClose }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await login(email, password);
      onClose();
      setEmail('');
      setPassword('');
    } catch (error: any) {
      setError(error.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = (provider: 'google' | 'facebook') => {
    // Placeholder for social login
    alert(`${provider} login will be implemented soon!`);
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className={`login-dialog-backdrop ${isVisible ? 'visible' : ''}`}
        onClick={onClose}
      />
      
      {/* Dialog */}
      <div className={`login-dialog ${isVisible ? 'visible' : ''}`}>
        {/* Header */}
        <div className="login-dialog-header">
          <h2 className="login-dialog-title">
            Welcome Back!
          </h2>
          <button
            onClick={onClose}
            className="login-dialog-close"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="login-dialog-content">
          <p className="login-dialog-subtitle">
            Login to manage your account.
          </p>

          {error && (
            <div className="login-dialog-error">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="login-dialog-field">
              <div className="login-dialog-input-wrapper">
                <span className="login-dialog-input-icon">
                  👤
                </span>
                <input
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="login-dialog-input"
                />
              </div>
            </div>

            <div className="login-dialog-field">
              <div className="login-dialog-input-wrapper">
                <span className="login-dialog-input-icon">
                  🔒
                </span>
                <input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="login-dialog-input"
                />
              </div>
            </div>

            <div className="login-dialog-forgot">
              <button
                className="login-dialog-forgot-link"
                onClick={() => {
                  alert('Forgot password functionality will be implemented soon!');
                }}
              >
                Forgot Password?
              </button>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="login-dialog-submit"
            >
              {isLoading ? 'Signing in...' : 'Login'}
            </button>
          </form>

          <div className="login-dialog-signup">
            Do not have an account?{' '}
            <button
              className="login-dialog-signup-link"
              onClick={() => {
                onClose();
                // Navigate to signup - you can implement this
                alert('Signup functionality will be implemented soon!');
              }}
            >
              Signup
            </button>
          </div>

          <div className="login-dialog-divider">
            <div className="login-dialog-divider-line" />
            <span className="login-dialog-divider-text">
              OR
            </span>
            <div className="login-dialog-divider-line" />
          </div>

          {/* Social Login Buttons */}
          <div className="login-dialog-social">
            <button
              onClick={() => handleSocialLogin('google')}
              className="login-dialog-social-button google"
            >
              <FontAwesomeIcon icon={faGoogle} />
              Google
            </button>

             <button
              onClick={() => handleSocialLogin('facebook')}
              className="login-dialog-social-button facebook"
            >
              <FontAwesomeIcon icon={faFacebookF} />
              Facebook
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default LoginDialog;
