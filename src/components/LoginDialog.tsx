import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFacebookF, faGoogle } from '@fortawesome/free-brands-svg-icons';
import { useAuth } from '../contexts/AuthContext';

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
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          zIndex: 9998,
          opacity: isVisible ? 1 : 0,
          visibility: isVisible ? 'visible' : 'hidden',
          transition: 'opacity 0.3s ease-in-out, visibility 0.3s ease-in-out'
        }}
        onClick={onClose}
      />
      
      {/* Dialog */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          right: 0,
          bottom: 0,
          width: '400px',
          backgroundColor: 'white',
          zIndex: 9999,
          transform: isVisible ? 'translateX(0)' : 'translateX(100%)',
          transition: 'transform 0.3s ease-in-out',
          boxShadow: '-4px 0 20px rgba(0, 0, 0, 0.15)',
          display: 'flex',
          flexDirection: 'column' as const
        }}
      >
        {/* Header */}
        <div style={{
          padding: '1.5rem',
          borderBottom: '1px solid #e5e7eb',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h2 style={{
            margin: 0,
            fontSize: '1.5rem',
            fontWeight: '600',
            color: '#1f2937'
          }}>
            Welcome Back!
          </h2>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '1.5rem',
              color: '#6b7280',
              cursor: 'pointer',
              padding: '0.25rem',
              borderRadius: '4px',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div style={{
          flex: 1,
          padding: '2rem 1.5rem',
          overflowY: 'auto' as const
        }}>
          <p style={{
            color: '#6b7280',
            marginBottom: '2rem',
            fontSize: '0.875rem'
          }}>
            Login to manage your account.
          </p>

          {error && (
            <div style={{
              backgroundColor: '#fee2e2',
              border: '1px solid #fecaca',
              borderRadius: '6px',
              padding: '0.75rem',
              marginBottom: '1rem',
              color: '#dc2626',
              fontSize: '0.875rem'
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1rem' }}>
              <div style={{
                position: 'relative',
                display: 'flex',
                alignItems: 'center'
              }}>
                <span style={{
                  position: 'absolute',
                  left: '12px',
                  color: '#9ca3af',
                  fontSize: '1rem'
                }}>
                  👤
                </span>
                <input
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem 0.75rem 0.75rem 2.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem',
                    transition: 'border-color 0.2s',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.currentTarget.style.borderColor = '#3b82f6'}
                  onBlur={(e) => e.currentTarget.style.borderColor = '#d1d5db'}
                />
              </div>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <div style={{
                position: 'relative',
                display: 'flex',
                alignItems: 'center'
              }}>
                <span style={{
                  position: 'absolute',
                  left: '12px',
                  color: '#9ca3af',
                  fontSize: '1rem'
                }}>
                  🔒
                </span>
                <input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem 0.75rem 0.75rem 2.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '0.875rem',
                    transition: 'border-color 0.2s',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.currentTarget.style.borderColor = '#3b82f6'}
                  onBlur={(e) => e.currentTarget.style.borderColor = '#d1d5db'}
                />
              </div>
            </div>

            <div style={{
              textAlign: 'right' as const,
              marginBottom: '1.5rem'
            }}>
              <button
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#6b7280',
                  fontSize: '0.875rem',
                  textDecoration: 'none',
                  cursor: 'pointer'
                }}
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
              style={{
                width: '100%',
                backgroundColor: isLoading ? '#fed700' : '#fed700',
                color: '#000',
                border: 'none',
                padding: '0.875rem',
                borderRadius: '25px',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.2s',
                opacity: isLoading ? 0.7 : 1
              }}
              onMouseOver={(e) => {
                if (!isLoading) {
                  e.currentTarget.style.backgroundColor = '#fbbf24';
                }
              }}
              onMouseOut={(e) => {
                if (!isLoading) {
                  e.currentTarget.style.backgroundColor = '#fed700';
                }
              }}
            >
              {isLoading ? 'Signing in...' : 'Login'}
            </button>
          </form>

          <div style={{
            textAlign: 'center' as const,
            margin: '1.5rem 0',
            fontSize: '0.875rem',
            color: '#6b7280'
          }}>
            Do not have an account?{' '}
            <button
              style={{
                background: 'none',
                border: 'none',
                color: '#3b82f6',
                textDecoration: 'none',
                fontWeight: '500',
                cursor: 'pointer'
              }}
              onClick={() => {
                onClose();
                // Navigate to signup - you can implement this
                alert('Signup functionality will be implemented soon!');
              }}
            >
              Signup
            </button>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            margin: '1.5rem 0'
          }}>
            <div style={{
              flex: 1,
              height: '1px',
              backgroundColor: '#e5e7eb'
            }} />
            <span style={{
              padding: '0 1rem',
              color: '#6b7280',
              fontSize: '0.875rem'
            }}>
              OR
            </span>
            <div style={{
              flex: 1,
              height: '1px',
              backgroundColor: '#e5e7eb'
            }} />
          </div>

          {/* Social Login Buttons */}
          <div style={{
            display: 'flex',
            gap: '0.75rem'
          }}>
            <button
              onClick={() => handleSocialLogin('facebook')}
              style={{
                flex: 1,
                backgroundColor: '#4267B2',
                color: 'white',
                border: 'none',
                padding: '0.75rem 1rem',
                borderRadius: '6px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'background-color 0.2s',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem'
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#365899'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#4267B2'}
            >
              <FontAwesomeIcon icon={faFacebookF} />
              Facebook
            </button>

            <button
              onClick={() => handleSocialLogin('google')}
              style={{
                flex: 1,
                backgroundColor: '#db4437',
                color: 'white',
                border: 'none',
                padding: '0.75rem 1rem',
                borderRadius: '6px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'background-color 0.2s',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem'
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#c23321'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#db4437'}
            >
              <FontAwesomeIcon icon={faGoogle} />
              Google
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default LoginDialog;
