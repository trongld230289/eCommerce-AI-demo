import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import './Auth.css';

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
      await register(email, password, email.split('@')[0]);
      navigate('/');
    } catch (error) {
      setError('Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h2 className="auth-title">
        Create Account
      </h2>
      
      {error && (
        <div className="auth-error">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="auth-field">
          <label className="auth-label">
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="auth-input"
            required
          />
        </div>

        <div className="auth-field">
          <label className="auth-label">
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="auth-input"
            required
          />
        </div>

        <div className="auth-field-last">
          <label className="auth-label">
            Confirm Password
          </label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="auth-input"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="auth-button"
        >
          {loading ? 'Creating Account...' : 'Create Account'}
        </button>
      </form>

      <div className="auth-footer">
        <span className="auth-footer-text">Already have an account? </span>
        <Link
          to="/login"
          className="auth-footer-link"
        >
          Sign In
        </Link>
      </div>
    </div>
  );
};

export default Register;
