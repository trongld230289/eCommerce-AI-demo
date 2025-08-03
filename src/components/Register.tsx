import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { Link, useNavigate } from 'react-router-dom';

const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password || !confirmPassword) {
      setError('Please fill in all fields');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    try {
      setError('');
      setLoading(true);
      await register(email, password);
      navigate('/');
    } catch (error) {
      setError('Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      maxWidth: '400px',
      margin: '4rem auto',
      padding: '2rem',
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      fontFamily: 'Open Sans, Arial, sans-serif'
    }}>
      <h2 style={{
        textAlign: 'center',
        marginBottom: '2rem',
        color: '#2c3e50',
        fontFamily: 'Open Sans, Arial, sans-serif'
      }}>
        Create Account
      </h2>
      
      {error && (
        <div style={{
          backgroundColor: '#f8d7da',
          color: '#721c24',
          padding: '0.75rem',
          borderRadius: '4px',
          marginBottom: '1rem',
          border: '1px solid #f5c6cb',
          fontFamily: 'Open Sans, Arial, sans-serif'
        }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '1rem' }}>
          <label style={{
            display: 'block',
            marginBottom: '0.5rem',
            fontWeight: '500',
            color: '#2c3e50',
            fontFamily: 'Open Sans, Arial, sans-serif'
          }}>
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem',
              fontFamily: 'Open Sans, Arial, sans-serif'
            }}
            required
          />
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label style={{
            display: 'block',
            marginBottom: '0.5rem',
            fontWeight: '500',
            color: '#2c3e50',
            fontFamily: 'Open Sans, Arial, sans-serif'
          }}>
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem',
              fontFamily: 'Open Sans, Arial, sans-serif'
            }}
            required
          />
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{
            display: 'block',
            marginBottom: '0.5rem',
            fontWeight: '500',
            color: '#2c3e50',
            fontFamily: 'Open Sans, Arial, sans-serif'
          }}>
            Confirm Password
          </label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem',
              fontFamily: 'Open Sans, Arial, sans-serif'
            }}
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            backgroundColor: '#fed700',
            color: '#333333',
            padding: '0.75rem',
            border: 'none',
            borderRadius: '4px',
            fontSize: '1rem',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1,
            fontFamily: 'Open Sans, Arial, sans-serif'
          }}
        >
          {loading ? 'Creating Account...' : 'Create Account'}
        </button>
      </form>

      <div style={{
        textAlign: 'center',
        marginTop: '1.5rem',
        fontFamily: 'Open Sans, Arial, sans-serif'
      }}>
        <span style={{ color: '#6c757d' }}>Already have an account? </span>
        <Link
          to="/login"
          style={{
            color: '#fed700',
            textDecoration: 'none',
            fontWeight: '500'
          }}
        >
          Sign In
        </Link>
      </div>
    </div>
  );
};

export default Register;
