// Event tracking service for user interactions
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface UserEvent {
  event_type: 'view' | 'add_to_cart' | 'remove_from_cart' | 'add_to_wishlist' | 'remove_from_wishlist' | 'purchase';
  user_id: string;
  product_id: string | number; // Allow both string and number
  metadata?: {
    product_name?: string;
    product_category?: string;
    product_brand?: string;
    product_price?: number;
    quantity?: number;
    device?: string;
    source?: string;
    [key: string]: any;
  };
}

export interface UserEventResponse {
  success: boolean;
  message: string;
  event_id?: string;
}

export interface UserAnalytics {
  total_events: number;
  events_by_type: Record<string, number>;
  most_viewed_products: Record<string, number>;
  most_viewed_categories: Record<string, number>;
  cart_actions: number;
  wishlist_actions: number;
}

class EventTrackingService {
  private async makeRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Event tracking request failed:', error);
      throw error;
    }
  }

  /**
   * Track a user event
   */
  async trackEvent(event: UserEvent): Promise<UserEventResponse> {
    try {
      // Add default metadata
      const eventData = {
        ...event,
        metadata: {
          device: this.getDeviceType(),
          source: this.getSource(),
          timestamp: new Date().toISOString(),
          ...event.metadata,
        },
      };

      return await this.makeRequest('/api/recommendations/track', {
        method: 'POST',
        body: JSON.stringify(eventData),
      });
    } catch (error) {
      console.error('Failed to track event:', error);
      // Return a failed response but don't throw to avoid breaking user experience
      return {
        success: false,
        message: 'Failed to track event',
      };
    }
  }

  /**
   * Track product view
   */
  async trackProductView(userId: string, productId: string, productMetadata?: any): Promise<void> {
    await this.trackEvent({
      event_type: 'view',
      user_id: userId,
      product_id: productId,
      metadata: {
        source: 'product_detail',
        ...productMetadata,
      },
    });
  }

  /**
   * Track add to cart
   */
  async trackAddToCart(userId: string, productId: string, productMetadata?: any): Promise<void> {
    await this.trackEvent({
      event_type: 'add_to_cart',
      user_id: userId,
      product_id: productId,
      metadata: {
        source: 'product_card',
        ...productMetadata,
      },
    });
  }

  /**
   * Track remove from cart
   */
  async trackRemoveFromCart(userId: string, productId: string, productMetadata?: any): Promise<void> {
    await this.trackEvent({
      event_type: 'remove_from_cart',
      user_id: userId,
      product_id: productId,
      metadata: {
        source: 'cart',
        ...productMetadata,
      },
    });
  }

  /**
   * Track add to wishlist
   */
  async trackAddToWishlist(userId: string, productId: string, productMetadata?: any): Promise<void> {
    await this.trackEvent({
      event_type: 'add_to_wishlist',
      user_id: userId,
      product_id: productId,
      metadata: {
        source: 'product_card',
        ...productMetadata,
      },
    });
  }

  /**
   * Track remove from wishlist
   */
  async trackRemoveFromWishlist(userId: string, productId: string, productMetadata?: any): Promise<void> {
    await this.trackEvent({
      event_type: 'remove_from_wishlist',
      user_id: userId,
      product_id: productId,
      metadata: {
        source: 'wishlist',
        ...productMetadata,
      },
    });
  }

  /**
   * Get user events
   */
  async getUserEvents(userId: string, options?: { limit?: number; event_type?: string }): Promise<any> {
    const params = new URLSearchParams();
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.event_type) params.append('event_type', options.event_type);
    
    const queryString = params.toString();
    const endpoint = `/events/${userId}${queryString ? `?${queryString}` : ''}`;
    
    return await this.makeRequest(endpoint);
  }

  /**
   * Get user analytics
   */
  async getUserAnalytics(userId: string): Promise<{ success: boolean; analytics: UserAnalytics }> {
    return await this.makeRequest(`/events/analytics/${userId}`);
  }

  /**
   * Get device type
   */
  private getDeviceType(): string {
    const userAgent = navigator.userAgent;
    if (/tablet|ipad|playbook|silk/i.test(userAgent)) {
      return 'tablet';
    }
    if (/mobile|iphone|ipod|android|blackberry|opera|mini|windows\sce|palm|smartphone|iemobile/i.test(userAgent)) {
      return 'mobile';
    }
    return 'desktop';
  }

  /**
   * Get source information
   */
  private getSource(): string {
    // You can enhance this based on your routing or referrer information
    const pathname = window.location.pathname;
    if (pathname.includes('/products/')) return 'product_detail';
    if (pathname.includes('/search')) return 'search_results';
    if (pathname.includes('/category')) return 'category_page';
    if (pathname === '/') return 'home_page';
    return 'unknown';
  }
}

// Create and export a singleton instance
export const eventTrackingService = new EventTrackingService();

// Export the class for testing or custom instances
export default EventTrackingService;
