import { Product } from '../contexts/ShopContext';

// Mock data has been migrated to Firebase Firestore
// This file is kept for legacy compatibility but exports empty arrays
export const mockProducts: Product[] = [];

// Categories and brands are now fetched from the API
// Use these API endpoints to fetch real data:
// - /products - Get all products
// - /products/featured - Get featured products  
// - /products/top-this-week - Get top products this week
// - /recommendations - Get personalized recommendations
// - /categories - Get all categories
// - /brands - Get all brands

export const categories: string[] = [];

export const brands: string[] = [];
