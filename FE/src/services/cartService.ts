class CartService {
<<<<<<< HEAD
  private baseURL = 'http://localhost:8000/api/cart';
=======
  private baseURL = `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/cart`;
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e

  private async makeRequest(url: string, options: RequestInit = {}): Promise<any> {
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Cart API request failed:', error);
      throw error;
    }
  }

  async getCart(userId: string) {
    const url = `${this.baseURL}?user_id=${encodeURIComponent(userId)}`;
    return this.makeRequest(url);
  }

<<<<<<< HEAD
  async addItemToCart(userId: string, productId: number, quantity: number = 1) {
    const url = `${this.baseURL}/add?user_id=${encodeURIComponent(userId)}`;
    return this.makeRequest(url, {
      method: 'POST',
      body: JSON.stringify({
        product_id: productId,
        quantity: quantity,
      }),
=======
  async addItemToCart(userId: string, productId: number, quantity: number = 1, productDetails?: any) {
    const url = `${this.baseURL}/add?user_id=${encodeURIComponent(userId)}`;
    
    // If we have product details, send them, otherwise just send product_id
    const payload = productDetails ? {
      product_id: productId,
      quantity: quantity,
      product_details: {
        id: productDetails.id || productId,
        name: productDetails.name,
        price: productDetails.price,
        original_price: productDetails.original_price,
        imageUrl: productDetails.imageUrl,
        category: productDetails.category,
        description: productDetails.description,
        rating: productDetails.rating,
        discount: productDetails.discount
      }
    } : {
      product_id: productId,
      quantity: quantity,
    };
    
    return this.makeRequest(url, {
      method: 'POST',
      body: JSON.stringify(payload),
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
    });
  }

  async updateItemQuantity(userId: string, productId: number, quantity: number) {
    const url = `${this.baseURL}/update?user_id=${encodeURIComponent(userId)}`;
    return this.makeRequest(url, {
      method: 'PUT',
      body: JSON.stringify({
        product_id: productId,
        quantity: quantity,
      }),
    });
  }

  async removeItemFromCart(userId: string, productId: number) {
    const url = `${this.baseURL}/remove?user_id=${encodeURIComponent(userId)}`;
    return this.makeRequest(url, {
      method: 'DELETE',
      body: JSON.stringify({
        product_id: productId,
      }),
    });
  }

  async clearCart(userId: string) {
    const url = `${this.baseURL}/clear?user_id=${encodeURIComponent(userId)}`;
    return this.makeRequest(url, {
      method: 'DELETE',
    });
  }

  async syncCartFromLocalStorage(userId: string, frontendCart: any[]) {
    const url = `${this.baseURL}/sync?user_id=${encodeURIComponent(userId)}`;
    return this.makeRequest(url, {
      method: 'POST',
      body: JSON.stringify(frontendCart),
    });
  }
}

export const cartService = new CartService();
