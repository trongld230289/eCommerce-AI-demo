import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useShop } from '../contexts/ShopContext';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faBell, 
  faHeart, 
  faShoppingCart, 
  faTrash, 
  faEdit,
  faSave,
  faTimes,
  faPlus
} from '@fortawesome/free-solid-svg-icons';
import type { Product } from '../contexts/ShopContext';
import { notificationService } from '../services/notificationService';

interface PriceAlert {
  id: string;
  productId: number;
  productName: string;
  productImage: string;
  targetPrice: number;
  currentPrice: number;
  isActive: boolean;
  createdAt: Date;
}

interface StockAlert {
  id: string;
  productId: number;
  productName: string;
  productImage: string;
  isActive: boolean;
  createdAt: Date;
}

interface NotificationSettings {
  emailNotifications: boolean;
  priceAlerts: boolean;
  stockAlerts: boolean;
  promotionalEmails: boolean;
}

const Settings: React.FC = () => {
  const { state } = useShop();
  const { currentUser } = useAuth();
  const { showSuccess, showError, showWarning } = useToast();

  // Settings state
  const [priceAlerts, setPriceAlerts] = useState<PriceAlert[]>([]);
  const [stockAlerts, setStockAlerts] = useState<StockAlert[]>([]);
  const [notificationSettings, setNotificationSettings] = useState<NotificationSettings>({
    emailNotifications: true,
    priceAlerts: true,
    stockAlerts: true,
    promotionalEmails: false
  });
  const [notificationPermission, setNotificationPermission] = useState<string>('default');

  // Form states
  const [selectedPriceProduct, setSelectedPriceProduct] = useState<Product | null>(null);
  const [targetPrice, setTargetPrice] = useState<string>('');
  const [selectedStockProduct, setSelectedStockProduct] = useState<Product | null>(null);
  const [editingAlert, setEditingAlert] = useState<string | null>(null);
  const [editPrice, setEditPrice] = useState<string>('');

  // Load settings from localStorage
  useEffect(() => {
    if (currentUser) {
      const settingsKey = `notification_settings_${currentUser.uid}`;
      const priceAlertsKey = `price_alerts_${currentUser.uid}`;
      const stockAlertsKey = `stock_alerts_${currentUser.uid}`;

      const savedSettings = localStorage.getItem(settingsKey);
      const savedPriceAlerts = localStorage.getItem(priceAlertsKey);
      const savedStockAlerts = localStorage.getItem(stockAlertsKey);

      if (savedSettings) {
        setNotificationSettings(JSON.parse(savedSettings));
      }
      if (savedPriceAlerts) {
        setPriceAlerts(JSON.parse(savedPriceAlerts));
      }
      if (savedStockAlerts) {
        setStockAlerts(JSON.parse(savedStockAlerts));
      }

      // Check notification permission
      if (notificationService.isNotificationSupported()) {
        setNotificationPermission(Notification.permission);
      }

      // Start monitoring for this user
      notificationService.startMonitoring(currentUser.uid);
    }

    // Cleanup monitoring when component unmounts or user changes
    return () => {
      notificationService.stopMonitoring();
    };
  }, [currentUser]);

  // Save settings to localStorage
  const saveSettings = useCallback(() => {
    if (currentUser) {
      const settingsKey = `notification_settings_${currentUser.uid}`;
      const priceAlertsKey = `price_alerts_${currentUser.uid}`;
      const stockAlertsKey = `stock_alerts_${currentUser.uid}`;

      localStorage.setItem(settingsKey, JSON.stringify(notificationSettings));
      localStorage.setItem(priceAlertsKey, JSON.stringify(priceAlerts));
      localStorage.setItem(stockAlertsKey, JSON.stringify(stockAlerts));
    }
  }, [currentUser, notificationSettings, priceAlerts, stockAlerts]);

  // Auto-save when settings change
  useEffect(() => {
    saveSettings();
  }, [saveSettings]);

  const handleAddPriceAlert = () => {
    if (!selectedPriceProduct || !targetPrice) {
      showWarning('Please select a product and enter target price');
      return;
    }

    const price = parseFloat(targetPrice);
    if (isNaN(price) || price <= 0) {
      showError('Please enter a valid price');
      return;
    }

    if (price >= selectedPriceProduct.price) {
      showWarning('Target price should be lower than current price');
      return;
    }

    // Check if alert already exists for this product
    const existingAlert = priceAlerts.find(alert => alert.productId === selectedPriceProduct.id);
    if (existingAlert) {
      showWarning('Price alert already exists for this product');
      return;
    }

    const newAlert: PriceAlert = {
      id: Date.now().toString(),
      productId: selectedPriceProduct.id,
      productName: selectedPriceProduct.name,
      productImage: selectedPriceProduct.imageUrl,
      targetPrice: price,
      currentPrice: selectedPriceProduct.price,
      isActive: true,
      createdAt: new Date()
    };

    setPriceAlerts(prev => [...prev, newAlert]);
    setSelectedPriceProduct(null);
    setTargetPrice('');
    showSuccess('Price alert created!', `You'll be notified when ${selectedPriceProduct.name} drops to $${price}`);
  };

  const handleAddStockAlert = () => {
    if (!selectedStockProduct) {
      showWarning('Please select a product');
      return;
    }

    // Check if alert already exists for this product
    const existingAlert = stockAlerts.find(alert => alert.productId === selectedStockProduct.id);
    if (existingAlert) {
      showWarning('Stock alert already exists for this product');
      return;
    }

    const newAlert: StockAlert = {
      id: Date.now().toString(),
      productId: selectedStockProduct.id,
      productName: selectedStockProduct.name,
      productImage: selectedStockProduct.imageUrl,
      isActive: true,
      createdAt: new Date()
    };

    setStockAlerts(prev => [...prev, newAlert]);
    setSelectedStockProduct(null);
    showSuccess('Stock alert created!', `You'll be notified when ${selectedStockProduct.name} is back in stock`);
  };

  const handleDeletePriceAlert = (alertId: string) => {
    setPriceAlerts(prev => prev.filter(alert => alert.id !== alertId));
    showSuccess('Price alert deleted');
  };

  const handleDeleteStockAlert = (alertId: string) => {
    setStockAlerts(prev => prev.filter(alert => alert.id !== alertId));
    showSuccess('Stock alert deleted');
  };

  const handleEditPriceAlert = (alertId: string) => {
    const alert = priceAlerts.find(a => a.id === alertId);
    if (alert) {
      setEditingAlert(alertId);
      setEditPrice(alert.targetPrice.toString());
    }
  };

  const handleSaveEditPrice = (alertId: string) => {
    const price = parseFloat(editPrice);
    if (isNaN(price) || price <= 0) {
      showError('Please enter a valid price');
      return;
    }

    setPriceAlerts(prev => prev.map(alert => 
      alert.id === alertId 
        ? { ...alert, targetPrice: price }
        : alert
    ));
    setEditingAlert(null);
    setEditPrice('');
    showSuccess('Price alert updated');
  };

  const togglePriceAlert = (alertId: string) => {
    setPriceAlerts(prev => prev.map(alert => 
      alert.id === alertId 
        ? { ...alert, isActive: !alert.isActive }
        : alert
    ));
  };

  const toggleStockAlert = (alertId: string) => {
    setStockAlerts(prev => prev.map(alert => 
      alert.id === alertId 
        ? { ...alert, isActive: !alert.isActive }
        : alert
    ));
  };

  const requestNotificationPermission = async () => {
    const granted = await notificationService.requestPermission();
    if (granted) {
      setNotificationPermission('granted');
      showSuccess('Notifications enabled!', 'You will now receive browser notifications for price and stock alerts.');
    } else {
      showError('Permission denied', 'Please enable notifications in your browser settings to receive alerts.');
    }
  };

  // Styles
  const styles = {
    container: {
      maxWidth: '1430px',
      margin: '0 auto',
      padding: '2rem',
      backgroundColor: '#f8fafc',
      minHeight: '100vh'
    },
    breadcrumb: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      marginBottom: '2rem',
      fontSize: '0.875rem',
      color: '#6b7280'
    },
    breadcrumbLink: {
      color: 'rgb(44, 62, 80)',
      textDecoration: 'none'
    },
    header: {
      marginBottom: '2rem'
    },
    title: {
      fontSize: '2rem',
      fontWeight: 'bold',
      color: '#1f2937',
      marginBottom: '0.5rem'
    },
    subtitle: {
      color: '#6b7280',
      fontSize: '1rem'
    },
    section: {
      backgroundColor: 'white',
      borderRadius: '8px',
      padding: '2rem',
      marginBottom: '2rem',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
    },
    sectionTitle: {
      fontSize: '1.25rem',
      fontWeight: '600',
      color: '#1f2937',
      marginBottom: '1rem',
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem'
    },
    formGroup: {
      marginBottom: '1.5rem'
    },
    label: {
      display: 'block',
      fontSize: '0.875rem',
      fontWeight: '500',
      color: '#374151',
      marginBottom: '0.5rem'
    },
    select: {
      width: '100%',
      padding: '0.75rem',
      border: '1px solid #d1d5db',
      borderRadius: '6px',
      fontSize: '0.875rem',
      backgroundColor: 'white'
    },
    input: {
      width: '100%',
      padding: '0.75rem',
      border: '1px solid #d1d5db',
      borderRadius: '6px',
      fontSize: '0.875rem'
    },
    button: {
      backgroundColor: 'rgb(44, 62, 80)',
      color: 'white',
      border: 'none',
      padding: '0.75rem 1.5rem',
      borderRadius: '6px',
      fontSize: '0.875rem',
      fontWeight: '500',
      cursor: 'pointer',
      transition: 'background-color 0.2s',
      boxShadow: '0 2px 4px rgba(44, 62, 80, 0.2)'
    },
    buttonSecondary: {
      backgroundColor: 'rgba(44, 62, 80, 0.8)',
      color: 'white',
      border: 'none',
      padding: '0.5rem 1rem',
      borderRadius: '4px',
      fontSize: '0.75rem',
      fontWeight: '500',
      cursor: 'pointer',
      transition: 'background-color 0.2s',
      boxShadow: '0 1px 3px rgba(44, 62, 80, 0.2)'
    },
    buttonDanger: {
      backgroundColor: '#dc2626',
      color: 'white',
      border: 'none',
      padding: '0.5rem 1rem',
      borderRadius: '4px',
      fontSize: '0.75rem',
      fontWeight: '500',
      cursor: 'pointer',
      transition: 'background-color 0.2s'
    },
    alertCard: {
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '1rem',
      marginBottom: '1rem',
      display: 'flex',
      alignItems: 'center',
      gap: '1rem'
    },
    alertImage: {
      width: '60px',
      height: '60px',
      objectFit: 'cover' as const,
      borderRadius: '6px'
    },
    alertInfo: {
      flex: 1
    },
    alertName: {
      fontWeight: '500',
      color: '#1f2937',
      marginBottom: '0.25rem'
    },
    alertPrice: {
      fontSize: '0.875rem',
      color: '#6b7280'
    },
    alertActions: {
      display: 'flex',
      gap: '0.5rem',
      alignItems: 'center'
    },
    toggleSwitch: {
      position: 'relative' as const,
      display: 'inline-block',
      width: '52px',
      height: '28px'
    },
    toggleInput: {
      opacity: 0,
      width: 0,
      height: 0
    },
    toggleSlider: {
      position: 'absolute' as const,
      cursor: 'pointer',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: '#ccc',
      transition: '.4s',
      borderRadius: '28px',
      border: '2px solid #e0e0e0',
      boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.1)'
    },
    checkboxGroup: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      marginBottom: '1rem'
    },
    checkbox: {
      width: '18px',
      height: '18px',
      accentColor: 'rgb(44, 62, 80)'
    },
    grid2: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '2rem'
    }
  };

  if (!currentUser) {
    return (
      <div style={styles.container}>
        <div style={styles.breadcrumb}>
          <Link to="/" style={styles.breadcrumbLink}>Home</Link>
          <span>›</span>
          <span>Settings</span>
        </div>
        
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>
            <FontAwesomeIcon icon={faBell} />
            Notification Settings
          </h2>
          <p style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>
            Please log in to manage your notification settings
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.breadcrumb}>
        <Link to="/" style={styles.breadcrumbLink}>Home</Link>
        <span>›</span>
        <span>Settings</span>
      </div>

      <div style={styles.header}>
        <h1 style={styles.title}>Notification Settings</h1>
        <p style={styles.subtitle}>
          Manage your price alerts, stock notifications, and email preferences
        </p>
      </div>

      {/* General Notification Settings */}
      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>
          <FontAwesomeIcon icon={faBell} />
          General Settings
        </h2>
        
        {/* Browser Notification Permission */}
        {notificationService.isNotificationSupported() && (
          <div style={{ ...styles.formGroup, backgroundColor: '#f3f4f6', padding: '1rem', borderRadius: '6px', marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <strong>Browser Notifications</strong>
                <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: '0.25rem 0 0 0' }}>
                  {notificationPermission === 'granted' 
                    ? '✅ Enabled - You will receive browser notifications'
                    : notificationPermission === 'denied'
                    ? '❌ Blocked - Please enable in browser settings'
                    : '⚠️ Not enabled - Click to enable notifications'
                  }
                </p>
              </div>
              {notificationPermission !== 'granted' && (
                <button
                  style={styles.button}
                  onClick={requestNotificationPermission}
                >
                  Enable Notifications
                </button>
              )}
            </div>
          </div>
        )}
        
        <div style={styles.checkboxGroup}>
          <input
            type="checkbox"
            id="emailNotifications"
            style={styles.checkbox}
            checked={notificationSettings.emailNotifications}
            onChange={(e) => setNotificationSettings(prev => ({
              ...prev,
              emailNotifications: e.target.checked
            }))}
          />
          <label htmlFor="emailNotifications">Enable email notifications</label>
        </div>

        <div style={styles.checkboxGroup}>
          <input
            type="checkbox"
            id="priceAlerts"
            style={styles.checkbox}
            checked={notificationSettings.priceAlerts}
            onChange={(e) => setNotificationSettings(prev => ({
              ...prev,
              priceAlerts: e.target.checked
            }))}
          />
          <label htmlFor="priceAlerts">Enable price drop alerts</label>
        </div>

        <div style={styles.checkboxGroup}>
          <input
            type="checkbox"
            id="stockAlerts"
            style={styles.checkbox}
            checked={notificationSettings.stockAlerts}
            onChange={(e) => setNotificationSettings(prev => ({
              ...prev,
              stockAlerts: e.target.checked
            }))}
          />
          <label htmlFor="stockAlerts">Enable stock availability alerts</label>
        </div>

        <div style={styles.checkboxGroup}>
          <input
            type="checkbox"
            id="promotionalEmails"
            style={styles.checkbox}
            checked={notificationSettings.promotionalEmails}
            onChange={(e) => setNotificationSettings(prev => ({
              ...prev,
              promotionalEmails: e.target.checked
            }))}
          />
          <label htmlFor="promotionalEmails">Receive promotional emails and offers</label>
        </div>
      </div>

      <div style={styles.grid2}>
        {/* Price Alerts Section */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>
            <FontAwesomeIcon icon={faHeart} />
            Price Alerts ({priceAlerts.length})
          </h2>
          <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '1.5rem' }}>
            Get notified when products in your wishlist drop to your target price
          </p>

          {/* Add Price Alert Form */}
          <div style={styles.formGroup}>
            <label style={styles.label}>Select Product from Wishlist</label>
            <select
              style={styles.select}
              value={selectedPriceProduct?.id || ''}
              onChange={(e) => {
                const product = state.wishlist.find(p => p.id === parseInt(e.target.value));
                setSelectedPriceProduct(product || null);
              }}
            >
              <option value="">Choose a product...</option>
              {state.wishlist.map(product => (
                <option key={product.id} value={product.id}>
                  {product.name} - Current: ${product.price}
                </option>
              ))}
            </select>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Target Price ($)</label>
            <input
              type="number"
              style={styles.input}
              value={targetPrice}
              onChange={(e) => setTargetPrice(e.target.value)}
              placeholder="Enter your target price"
              min="0"
              step="0.01"
            />
          </div>

          <button
            style={styles.button}
            onClick={handleAddPriceAlert}
            disabled={!selectedPriceProduct || !targetPrice}
          >
            <FontAwesomeIcon icon={faPlus} style={{ marginRight: '0.5rem' }} />
            Add Price Alert
          </button>

          {/* Price Alerts List */}
          <div style={{ marginTop: '2rem' }}>
            {priceAlerts.length === 0 ? (
              <p style={{ color: '#6b7280', textAlign: 'center', padding: '1rem' }}>
                No price alerts set. Add products to your wishlist and set price alerts!
              </p>
            ) : (
              priceAlerts.map(alert => (
                <div key={alert.id} style={{
                  ...styles.alertCard,
                  opacity: alert.isActive ? 1 : 0.6
                }}>
                  <img src={alert.productImage} alt={alert.productName} style={styles.alertImage} />
                  <div style={styles.alertInfo}>
                    <div style={styles.alertName}>{alert.productName}</div>
                    <div style={styles.alertPrice}>
                      Current: ${alert.currentPrice} → Target: ${alert.targetPrice}
                    </div>
                  </div>
                  <div style={styles.alertActions}>
                    <label style={styles.toggleSwitch}>
                      <input
                        type="checkbox"
                        style={styles.toggleInput}
                        checked={alert.isActive}
                        onChange={() => togglePriceAlert(alert.id)}
                      />
                      <span style={{
                        ...styles.toggleSlider,
                        backgroundColor: alert.isActive ? 'rgb(44, 62, 80)' : '#ccc',
                        border: alert.isActive ? '2px solid rgb(44, 62, 80)' : '2px solid #e0e0e0'
                      }}>
                        <span style={{
                          position: 'absolute',
                          content: '',
                          height: '20px',
                          width: '20px',
                          left: alert.isActive ? '26px' : '2px',
                          bottom: '2px',
                          backgroundColor: 'white',
                          transition: '.4s',
                          borderRadius: '50%',
                          boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                        }}></span>
                      </span>
                    </label>
                    
                    {editingAlert === alert.id ? (
                      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <input
                          type="number"
                          value={editPrice}
                          onChange={(e) => setEditPrice(e.target.value)}
                          style={{ width: '80px', padding: '0.25rem', fontSize: '0.75rem' }}
                          min="0"
                          step="0.01"
                        />
                        <button
                          style={styles.buttonSecondary}
                          onClick={() => handleSaveEditPrice(alert.id)}
                        >
                          <FontAwesomeIcon icon={faSave} />
                        </button>
                        <button
                          style={styles.buttonSecondary}
                          onClick={() => {
                            setEditingAlert(null);
                            setEditPrice('');
                          }}
                        >
                          <FontAwesomeIcon icon={faTimes} />
                        </button>
                      </div>
                    ) : (
                      <>
                        <button
                          style={styles.buttonSecondary}
                          onClick={() => handleEditPriceAlert(alert.id)}
                        >
                          <FontAwesomeIcon icon={faEdit} />
                        </button>
                        <button
                          style={styles.buttonDanger}
                          onClick={() => handleDeletePriceAlert(alert.id)}
                        >
                          <FontAwesomeIcon icon={faTrash} />
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Stock Alerts Section */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>
            <FontAwesomeIcon icon={faShoppingCart} />
            Stock Alerts ({stockAlerts.length})
          </h2>
          <p style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '1.5rem' }}>
            Get notified when products in your cart are back in stock
          </p>

          {/* Add Stock Alert Form */}
          <div style={styles.formGroup}>
            <label style={styles.label}>Select Product from Cart</label>
            <select
              style={styles.select}
              value={selectedStockProduct?.id || ''}
              onChange={(e) => {
                const product = state.cart.find(item => item.id === parseInt(e.target.value));
                setSelectedStockProduct(product || null);
              }}
            >
              <option value="">Choose a product...</option>
              {state.cart.map(item => (
                <option key={item.id} value={item.id}>
                  {item.name} - Qty: {item.quantity}
                </option>
              ))}
            </select>
          </div>

          <button
            style={styles.button}
            onClick={handleAddStockAlert}
            disabled={!selectedStockProduct}
          >
            <FontAwesomeIcon icon={faPlus} style={{ marginRight: '0.5rem' }} />
            Add Stock Alert
          </button>

          {/* Stock Alerts List */}
          <div style={{ marginTop: '2rem' }}>
            {stockAlerts.length === 0 ? (
              <p style={{ color: '#6b7280', textAlign: 'center', padding: '1rem' }}>
                No stock alerts set. Add products to your cart and set stock alerts!
              </p>
            ) : (
              stockAlerts.map(alert => (
                <div key={alert.id} style={{
                  ...styles.alertCard,
                  opacity: alert.isActive ? 1 : 0.6
                }}>
                  <img src={alert.productImage} alt={alert.productName} style={styles.alertImage} />
                  <div style={styles.alertInfo}>
                    <div style={styles.alertName}>{alert.productName}</div>
                    <div style={styles.alertPrice}>
                      Notify when back in stock
                    </div>
                  </div>
                  <div style={styles.alertActions}>
                    <label style={styles.toggleSwitch}>
                      <input
                        type="checkbox"
                        style={styles.toggleInput}
                        checked={alert.isActive}
                        onChange={() => toggleStockAlert(alert.id)}
                      />
                      <span style={{
                        ...styles.toggleSlider,
                        backgroundColor: alert.isActive ? 'rgb(44, 62, 80)' : '#ccc',
                        border: alert.isActive ? '2px solid rgb(44, 62, 80)' : '2px solid #e0e0e0'
                      }}>
                        <span style={{
                          position: 'absolute',
                          content: '',
                          height: '20px',
                          width: '20px',
                          left: alert.isActive ? '26px' : '2px',
                          bottom: '2px',
                          backgroundColor: 'white',
                          transition: '.4s',
                          borderRadius: '50%',
                          boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                        }}></span>
                      </span>
                    </label>
                    
                    <button
                      style={styles.buttonDanger}
                      onClick={() => handleDeleteStockAlert(alert.id)}
                    >
                      <FontAwesomeIcon icon={faTrash} />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
