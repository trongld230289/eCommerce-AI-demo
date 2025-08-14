export interface PriceAlert {
  id: string;
  productId: number;
  productName: string;
  productImage: string;
  targetPrice: number;
  currentPrice: number;
  isActive: boolean;
  createdAt: Date;
}

export interface StockAlert {
  id: string;
  productId: number;
  productName: string;
  productImage: string;
  isActive: boolean;
  createdAt: Date;
}

export interface NotificationSettings {
  emailNotifications: boolean;
  priceAlerts: boolean;
  stockAlerts: boolean;
  promotionalEmails: boolean;
}

export class NotificationService {
  private static instance: NotificationService;
  private checkInterval: NodeJS.Timeout | null = null;

  public static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  // Start periodic checking for price and stock changes
  public startMonitoring(userId: string): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
    }

    // Check every 30 seconds (in production, this would be much longer)
    this.checkInterval = setInterval(() => {
      this.checkPriceAlerts(userId);
      this.checkStockAlerts(userId);
    }, 30000);
  }

  public stopMonitoring(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
  }

  // Check for price drops
  private async checkPriceAlerts(userId: string): Promise<void> {
    try {
      const priceAlertsKey = `price_alerts_${userId}`;
      const settingsKey = `notification_settings_${userId}`;
      
      const savedAlerts = localStorage.getItem(priceAlertsKey);
      const savedSettings = localStorage.getItem(settingsKey);
      
      if (!savedAlerts || !savedSettings) return;

      const priceAlerts: PriceAlert[] = JSON.parse(savedAlerts);
      const settings: NotificationSettings = JSON.parse(savedSettings);

      if (!settings.priceAlerts) return;

      const activeAlerts = priceAlerts.filter(alert => alert.isActive);

      for (const alert of activeAlerts) {
        // Simulate price changes (in real app, this would fetch from API)
        const newPrice = this.simulatePriceChange(alert.currentPrice);
        
        if (newPrice <= alert.targetPrice) {
          this.showPriceAlert(alert, newPrice);
          // Update the alert to mark it as triggered (optional)
          // this.deactivateAlert(userId, alert.id);
        }
      }
    } catch (error) {
      console.error('Error checking price alerts:', error);
    }
  }

  // Check for stock availability
  private async checkStockAlerts(userId: string): Promise<void> {
    try {
      const stockAlertsKey = `stock_alerts_${userId}`;
      const settingsKey = `notification_settings_${userId}`;
      
      const savedAlerts = localStorage.getItem(stockAlertsKey);
      const savedSettings = localStorage.getItem(settingsKey);
      
      if (!savedAlerts || !savedSettings) return;

      const stockAlerts: StockAlert[] = JSON.parse(savedAlerts);
      const settings: NotificationSettings = JSON.parse(savedSettings);

      if (!settings.stockAlerts) return;

      const activeAlerts = stockAlerts.filter(alert => alert.isActive);

      for (const alert of activeAlerts) {
        // Simulate stock becoming available (in real app, this would check inventory API)
        const isInStock = this.simulateStockChange();
        
        if (isInStock) {
          this.showStockAlert(alert);
          // Update the alert to mark it as triggered (optional)
          // this.deactivateStockAlert(userId, alert.id);
        }
      }
    } catch (error) {
      console.error('Error checking stock alerts:', error);
    }
  }

  // Simulate price changes (random fluctuations)
  private simulatePriceChange(currentPrice: number): number {
    // Random price change between -10% and +5%
    const changePercent = (Math.random() * 0.15) - 0.1;
    const newPrice = currentPrice * (1 + changePercent);
    return Math.round(newPrice * 100) / 100;
  }

  // Simulate stock becoming available (random chance)
  private simulateStockChange(): boolean {
    // 5% chance of coming back in stock each check
    return Math.random() < 0.05;
  }

  // Show browser notification for price alert
  private showPriceAlert(alert: PriceAlert, newPrice: number): void {
    this.showNotification(
      '🎉 Price Drop Alert!',
      `${alert.productName} is now $${newPrice} (Target: $${alert.targetPrice})`,
      alert.productImage
    );
  }

  // Show browser notification for stock alert
  private showStockAlert(alert: StockAlert): void {
    this.showNotification(
      '📦 Back in Stock!',
      `${alert.productName} is now available`,
      alert.productImage
    );
  }

  // Generic notification display
  private showNotification(title: string, body: string, icon?: string): void {
    // Check if browser supports notifications
    if ('Notification' in window) {
      // Request permission if not granted
      if (Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
          if (permission === 'granted') {
            this.createNotification(title, body, icon);
          }
        });
      } else if (Notification.permission === 'granted') {
        this.createNotification(title, body, icon);
      }
    }

    // Also log to console for development
    console.log(`Notification: ${title} - ${body}`);
  }

  // Create the actual notification
  private createNotification(title: string, body: string, icon?: string): void {
    const notification = new Notification(title, {
      body,
      icon: icon || '/favicon.ico',
      badge: '/favicon.ico',
      tag: 'electro-notification',
      requireInteraction: true
    });

    notification.onclick = () => {
      window.focus();
      notification.close();
    };

    // Auto close after 5 seconds
    setTimeout(() => {
      notification.close();
    }, 5000);
  }

  // Request notification permission
  public async requestPermission(): Promise<boolean> {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }
    return false;
  }

  // Check if notifications are supported and enabled
  public isNotificationSupported(): boolean {
    return 'Notification' in window;
  }

  public isNotificationEnabled(): boolean {
    return 'Notification' in window && Notification.permission === 'granted';
  }

  // Send promotional email notification (simulated)
  public sendPromotionalEmail(userId: string, promotion: {
    title: string;
    description: string;
    discountPercent: number;
  }): void {
    const settingsKey = `notification_settings_${userId}`;
    const savedSettings = localStorage.getItem(settingsKey);
    
    if (!savedSettings) return;

    const settings: NotificationSettings = JSON.parse(savedSettings);

    if (settings.emailNotifications && settings.promotionalEmails) {
      console.log(`📧 Promotional Email Sent: ${promotion.title} - ${promotion.discountPercent}% OFF`);
      // In real app, this would call an email service API
    }
  }
}

// Export singleton instance
export const notificationService = NotificationService.getInstance();
