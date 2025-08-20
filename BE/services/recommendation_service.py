import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from firebase_config import get_firestore_db
from models import UserEvent, UserEventCreate, RecommendationRequest, RecommendationResponse, EventType, RecommendationSourceEnum
from product_service import product_service
import random

class RecommendationService:
    def __init__(self):
        self.db = get_firestore_db()
        self.collection_name = 'user_events'
        
        if self.db is None:
            raise ConnectionError("Firebase connection failed. Please check your configuration.")
    
    def _get_collection(self):
        """Get Firestore collection reference"""
        return self.db.collection(self.collection_name)
    
    async def track_user_event(self, event_data: UserEventCreate) -> bool:
        """Track a user event for recommendation system"""
        try:
            collection = self._get_collection()
            
            # Create event document
            event_doc = {
                "user_id": event_data.user_id,
                "event_type": event_data.event_type.value,
                "product_id": event_data.product_id,
                "session_id": event_data.session_id or f"session_{int(time.time())}",
                "timestamp": time.time(),
                "metadata": event_data.metadata or {}
            }
            
            # Add to Firestore
            collection.add(event_doc)
            
            print(f"✅ Tracked {event_data.event_type} event for user {event_data.user_id} on product {event_data.product_id}")
            return True
            
        except Exception as e:
            print(f"Error tracking user event: {e}")
            return False
    
    async def get_user_events(self, user_id: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """Get user events from the last N days"""
        try:
            collection = self._get_collection()
            
            # Calculate timestamp threshold
            cutoff_time = time.time() - (days_back * 24 * 60 * 60)
            
            # Query events for user
            query = collection.where("user_id", "==", user_id).where("timestamp", ">=", cutoff_time)
            docs = query.get()
            
            events = []
            for doc in docs:
                event_data = doc.to_dict()
                events.append(event_data)
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            
            return events
            
        except Exception as e:
            print(f"Error getting user events: {e}")
            return []
    
    async def get_personalized_recommendations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get personalized recommendations based on user behavior"""
        try:
            # Get user events
            events = await self.get_user_events(user_id, days_back=30)
            
            if not events:
                return []
            
            # Analyze user preferences
            category_scores = defaultdict(float)
            product_interactions = defaultdict(float)
            
            # Weight different event types
            event_weights = {
                EventType.VIEW: 1.0,
                EventType.ADD_TO_CART: 3.0,
                EventType.ADD_TO_WISHLIST: 2.0,
                EventType.REMOVE_FROM_CART: -1.0,
                EventType.REMOVE_FROM_WISHLIST: -0.5
            }
            
            # Get all products for category analysis
            all_products = product_service.get_all_products()
            product_map = {p['id']: p for p in all_products}
            
            # Analyze user behavior
            for event in events:
                event_type = event.get('event_type')
                product_id = event.get('product_id')
                weight = event_weights.get(EventType(event_type), 1.0)
                
                # Age factor (recent events more important)
                age_days = (time.time() - event.get('timestamp', 0)) / (24 * 60 * 60)
                age_factor = max(0.1, 1.0 - (age_days / 30))  # Decay over 30 days
                
                final_weight = weight * age_factor
                
                # Score the product
                product_interactions[product_id] += final_weight
                
                # Score the category
                if product_id in product_map:
                    category = product_map[product_id].get('category')
                    if category:
                        category_scores[category] += final_weight
            
            # Get viewed/purchased products to exclude
            interacted_products = set(product_interactions.keys())
            
            # Find products in preferred categories
            preferred_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            
            recommendations = []
            
            # Strategy 1: Similar products in preferred categories
            for category, score in preferred_categories[:2]:
                category_products = [p for p in all_products 
                                   if p.get('category') == category 
                                   and p['id'] not in interacted_products]
                
                # Sort by rating and add some randomness
                category_products.sort(key=lambda x: (x.get('rating', 0) * random.uniform(0.8, 1.2)), reverse=True)
                
                recommendations.extend(category_products[:limit//3])
            
            # Strategy 2: High-rated products in any category user might like
            remaining_products = [p for p in all_products 
                                if p['id'] not in interacted_products 
                                and p not in recommendations
                                and p.get('rating', 0) >= 4.0]
            
            remaining_products.sort(key=lambda x: x.get('rating', 0), reverse=True)
            recommendations.extend(remaining_products[:limit//3])
            
            # Remove duplicates and limit
            seen_ids = set()
            unique_recommendations = []
            for product in recommendations:
                if product['id'] not in seen_ids:
                    unique_recommendations.append(product)
                    seen_ids.add(product['id'])
                    if len(unique_recommendations) >= limit:
                        break
            
            return unique_recommendations
            
        except Exception as e:
            print(f"Error generating personalized recommendations: {e}")
            return []
    
    async def get_trending_recommendations(self, limit: int = 10, days_back: int = 7) -> List[Dict[str, Any]]:
        """Get trending products based on recent user activity"""
        try:
            collection = self._get_collection()
            
            # Get recent events
            cutoff_time = time.time() - (days_back * 24 * 60 * 60)
            query = collection.where("timestamp", ">=", cutoff_time)
            docs = query.get()
            
            # Count interactions per product
            product_popularity = defaultdict(float)
            
            for doc in docs:
                event_data = doc.to_dict()
                event_type = event_data.get('event_type')
                product_id = event_data.get('product_id')
                
                # Weight different events
                if event_type == EventType.VIEW.value:
                    product_popularity[product_id] += 1.0
                elif event_type == EventType.ADD_TO_CART.value:
                    product_popularity[product_id] += 5.0
                elif event_type == EventType.ADD_TO_WISHLIST.value:
                    product_popularity[product_id] += 3.0
            
            # Get top trending products
            trending_product_ids = sorted(product_popularity.items(), 
                                        key=lambda x: x[1], reverse=True)[:limit*2]
            
            # Get product details
            all_products = product_service.get_all_products()
            product_map = {p['id']: p for p in all_products}
            
            trending_products = []
            for product_id, score in trending_product_ids:
                if product_id in product_map:
                    product = product_map[product_id].copy()
                    product['trending_score'] = score
                    trending_products.append(product)
                    if len(trending_products) >= limit:
                        break
            
            return trending_products
            
        except Exception as e:
            print(f"Error getting trending recommendations: {e}")
            return []
    
    async def get_category_recommendations(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top products in a specific category"""
        try:
            all_products = product_service.get_all_products()
            category_products = [p for p in all_products if p.get('category') == category]
            
            # Sort by rating and some randomness
            category_products.sort(key=lambda x: (x.get('rating', 0) * random.uniform(0.9, 1.1)), reverse=True)
            
            return category_products[:limit]
            
        except Exception as e:
            print(f"Error getting category recommendations: {e}")
            return []
    
    async def get_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """Main recommendation endpoint"""
        try:
            recommendations = []
            source = RecommendationSourceEnum.RATING.value  # Default fallback
            
            # Strategy 1: Personalized recommendations for logged-in users
            if request.user_id:
                personalized = await self.get_personalized_recommendations(request.user_id, request.limit)
                if personalized:
                    recommendations = personalized
                    source = RecommendationSourceEnum.PERSONALIZED.value
                    # Add rec_source to each product
                    for product in recommendations:
                        product['rec_source'] = RecommendationSourceEnum.PERSONALIZED.value
            
            # Strategy 2: Category-based recommendations
            if not recommendations and request.category:
                category_recs = await self.get_category_recommendations(request.category, request.limit)
                if category_recs:
                    recommendations = category_recs
                    source = RecommendationSourceEnum.CATEGORY.value
                    # Add rec_source to each product
                    for product in recommendations:
                        product['rec_source'] = RecommendationSourceEnum.CATEGORY.value
            
            # Strategy 3: Trending recommendations
            if not recommendations:
                trending = await self.get_trending_recommendations(request.limit)
                if trending and len(trending) >= request.limit:
                    recommendations = trending
                    source = RecommendationSourceEnum.TRENDING.value
                    # Add rec_source to each product
                    for product in recommendations:
                        product['rec_source'] = RecommendationSourceEnum.TRENDING.value
                elif trending:  # If we have some but not enough, mix with other products
                    recommendations = trending
                    source = RecommendationSourceEnum.TRENDING.value  # Keep as trending since it's the primary source
                    
                    # Add rec_source to trending products
                    for product in recommendations:
                        product['rec_source'] = RecommendationSourceEnum.TRENDING.value
                    
                    # Fill remaining with top-rated products
                    needed = request.limit - len(trending)
                    all_products = product_service.get_all_products()
                    all_products.sort(key=lambda x: x.get('rating', 0), reverse=True)
                    
                    # Exclude products already in trending
                    trending_ids = {p['id'] for p in trending}
                    additional_products = [p for p in all_products if p['id'] not in trending_ids][:needed]
                    
                    # Add rec_source to additional products
                    for product in additional_products:
                        product['rec_source'] = RecommendationSourceEnum.RATING.value
                    
                    recommendations.extend(additional_products)
            
            # Strategy 4: Fallback to top-rated products
            if not recommendations:
                all_products = product_service.get_all_products()
                all_products.sort(key=lambda x: x.get('rating', 0), reverse=True)
                recommendations = all_products[:request.limit]
                source = RecommendationSourceEnum.RATING.value
                # Add rec_source to each product
                for product in recommendations:
                    product['rec_source'] = RecommendationSourceEnum.RATING.value
            
            return RecommendationResponse(
                recommendations=recommendations,
                user_id=request.user_id,
                source=source,
                context=request.context,
                total_count=len(recommendations),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            # Return fallback recommendations
            try:
                all_products = product_service.get_all_products()
                fallback_recs = all_products[:request.limit] if all_products else []
                
                # Add rec_source to fallback products
                for product in fallback_recs:
                    product['rec_source'] = RecommendationSourceEnum.RATING.value
                
                return RecommendationResponse(
                    recommendations=fallback_recs,
                    user_id=request.user_id,
                    source=RecommendationSourceEnum.RATING.value,  # Use enum for error fallback
                    context=request.context,
                    total_count=len(fallback_recs),
                    timestamp=datetime.now()
                )
            except:
                return RecommendationResponse(
                    recommendations=[],
                    user_id=request.user_id,
                    source="error",
                    context=request.context,
                    total_count=0,
                    timestamp=datetime.now()
                )

# Initialize service instance
recommendation_service = RecommendationService()
