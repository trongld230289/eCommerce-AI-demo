import React, { useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheck, faExclamationTriangle, faInfoCircle, faTimes, faHeart } from '@fortawesome/free-solid-svg-icons';

export type ToastType = 'success' | 'error' | 'info' | 'warning' | 'wishlist';

export interface ToastProps {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  onClose: (id: string) => void;
}

const Toast: React.FC<ToastProps> = ({
  id,
  type,
  title,
  message,
  duration = 4000,
  onClose
}) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose(id);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [id, duration, onClose]);

  const getToastStyles = () => {
    const baseStyles = {
      position: 'relative' as const,
      display: 'flex',
      alignItems: 'flex-start',
      gap: '12px',
      padding: '16px',
      marginBottom: '12px',
      borderRadius: '8px',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
      border: '1px solid',
      backgroundColor: 'white',
      minWidth: '320px',
      maxWidth: '400px',
      animation: 'slideInRight 0.3s ease-out',
      transition: 'all 0.3s ease'
    };

    const typeStyles = {
      success: {
        borderColor: '#22c55e',
        borderLeftWidth: '4px',
        borderLeftColor: '#22c55e'
      },
      error: {
        borderColor: '#ef4444',
        borderLeftWidth: '4px',
        borderLeftColor: '#ef4444'
      },
      warning: {
        borderColor: '#f59e0b',
        borderLeftWidth: '4px',
        borderLeftColor: '#f59e0b'
      },
      info: {
        borderColor: '#3b82f6',
        borderLeftWidth: '4px',
        borderLeftColor: '#3b82f6'
      },
      wishlist: {
        borderColor: '#dc2626',
        borderLeftWidth: '4px',
        borderLeftColor: '#dc2626'
      }
    };

    return { ...baseStyles, ...typeStyles[type] };
  };

  const getIconConfig = () => {
    const configs = {
      success: { icon: faCheck, color: '#22c55e' },
      error: { icon: faTimes, color: '#ef4444' },
      warning: { icon: faExclamationTriangle, color: '#f59e0b' },
      info: { icon: faInfoCircle, color: '#3b82f6' },
      wishlist: { icon: faHeart, color: '#dc2626' }
    };
    return configs[type];
  };

  const iconConfig = getIconConfig();

  return (
    <div style={getToastStyles()}>
      {/* Icon */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '20px',
        height: '20px',
        marginTop: '2px'
      }}>
        <FontAwesomeIcon 
          icon={iconConfig.icon} 
          style={{ 
            color: iconConfig.color,
            fontSize: '16px'
          }} 
        />
      </div>

      {/* Content */}
      <div style={{ flex: 1 }}>
        <div style={{
          fontSize: '14px',
          fontWeight: '600',
          color: '#1f2937',
          marginBottom: message ? '4px' : '0'
        }}>
          {title}
        </div>
        {message && (
          <div style={{
            fontSize: '13px',
            color: '#6b7280',
            lineHeight: '1.4'
          }}>
            {message}
          </div>
        )}
      </div>

      {/* Close Button */}
      <button
        onClick={() => onClose(id)}
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          color: '#9ca3af',
          fontSize: '14px',
          padding: '2px',
          borderRadius: '4px',
          transition: 'color 0.2s ease'
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.color = '#6b7280';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.color = '#9ca3af';
        }}
        title="Close"
      >
        <FontAwesomeIcon icon={faTimes} />
      </button>

      <style>{`
        @keyframes slideInRight {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};

export default Toast;
