import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { Link, useNavigate } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    try {
      setError('');
      setLoading(true);
      await login(email, password);
      navigate('/');
    } catch (error) {
      setError('Failed to log in');
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
        Sign In
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

        <div style={{ marginBottom: '1.5rem' }}>
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
          {loading ? 'Signing In...' : 'Sign In'}
        </button>
      </form>

      <div style={{
        textAlign: 'center',
        marginTop: '1.5rem',
        fontFamily: 'Open Sans, Arial, sans-serif'
      }}>
        <span style={{ color: '#6c757d' }}>Don't have an account? </span>
        <Link
          to="/register"
          style={{
            color: '#fed700',
            textDecoration: 'none',
            fontWeight: '500'
          }}
        >
          Sign Up
        </Link>
      </div>
    </div>
  );
};

export default Login;
