#!/usr/bin/env python3
"""
Shared product keyword generation utilities
"""

from typing import List, Dict, Any

def get_product_keywords(product_name: str, product_category: str) -> List[str]:
    """Generate enhanced keywords for better semantic search"""
    keywords = []
    name_lower = product_name.lower()
    category_lower = product_category.lower()
    
    # Phone keywords with features - only if category is phone OR name clearly indicates phone
    if ('phone' in category_lower or 
        any(word in name_lower for word in ['iphone', 'smartphone', 'mobile']) or
        ('galaxy' in name_lower and any(word in name_lower for word in ['s24', 's23', 's22', 'note', 'a55', 'a54']) and 'watch' not in name_lower) or
        ('xiaomi' in name_lower and any(word in name_lower for word in ['13t', '14', 'poco', 'redmi', 'note']) and 'watch' not in name_lower)):
        
        keywords.extend(['smartphone', 'mobile phone', 'cell phone', 'handset', 'communication device'])
        
        # Camera-related keywords for phones
        if any(word in name_lower for word in ['ultra', 'pro', 'max', 'plus']):
            keywords.extend(['camera phone', 'photography phone', 'high-quality camera', 'professional camera', 'photo quality', 'camera quality'])
        
        # 5G and connectivity
        if any(word in name_lower for word in ['5g', '15', '14', '13', 'galaxy s24', 'galaxy s23']):
            keywords.extend(['5g phone', 'fast connectivity', 'modern smartphone', 'latest technology'])
    
    # Laptop keywords with features  
    if 'laptop' in category_lower or any(word in name_lower for word in ['laptop', 'macbook', 'thinkpad', 'inspiron', 'xps']):
        keywords.extend(['computer', 'notebook', 'portable computer', 'pc', 'laptop computer'])
        
        # Gaming laptops
        if any(word in name_lower for word in ['gaming', 'omen', 'legion', 'g15', 'alienware']):
            keywords.extend(['gaming laptop', 'gaming computer', 'high-performance laptop', 'powerful laptop', 'gaming pc'])
        
        # Lightweight/portable
        if any(word in name_lower for word in ['air', 'ultrabook', 'slim', 'thin', 'x1', 'spectre']):
            keywords.extend(['lightweight laptop', 'thin laptop', 'portable laptop', 'ultrabook', 'slim laptop', 'lightweight computer'])
        
        # Professional/business
        if any(word in name_lower for word in ['thinkpad', 'business', 'pro']):
            keywords.extend(['business laptop', 'professional laptop', 'work laptop', 'office laptop'])
    
    # Camera keywords with features
    if 'camera' in category_lower or any(word in name_lower for word in ['canon', 'sony', 'fujifilm', 'nikon']):
        keywords.extend(['digital camera', 'photography equipment', 'photo camera', 'imaging device'])
        
        # Professional cameras
        if any(word in name_lower for word in ['r5', 'r6', 'a7', 'fx30', 'professional', 'pro']):
            keywords.extend(['professional camera', 'high-end camera', 'advanced camera', 'pro camera'])
        
        # 4K and video capabilities
        if any(word in name_lower for word in ['4k', 'video', 'cinema', 'fx30', 'a7']):
            keywords.extend(['4k camera', 'video recording', '4k video', 'video camera', 'cinema camera', 'recording device'])
        
        # Mirrorless and compact
        if any(word in name_lower for word in ['mirrorless', 'compact', 'x100', 'powershot']):
            keywords.extend(['mirrorless camera', 'compact camera', 'portable camera', 'lightweight camera'])
    
    # Watch keywords with features
    if 'watch' in category_lower or any(word in name_lower for word in ['watch', 'garmin', 'apple watch', 'galaxy watch']):
        keywords.extend(['smartwatch', 'wearable', 'fitness tracker', 'smart device', 'wrist device'])
        
        # Fitness and sports features
        if any(word in name_lower for word in ['forerunner', 'fenix', 'venu', 'fitness', 'sport']):
            keywords.extend(['fitness watch', 'sports watch', 'running watch', 'fitness tracker', 'activity tracker', 'exercise tracker'])
        
        # GPS and tracking
        if any(word in name_lower for word in ['garmin', 'forerunner', 'fenix', 'instinct', 'gps']):
            keywords.extend(['gps watch', 'gps tracker', 'navigation watch', 'outdoor watch', 'tracking device'])
        
        # Waterproof and durability
        if any(word in name_lower for word in ['ultra', 'instinct', 'fenix', 'pro']):
            keywords.extend(['waterproof watch', 'durable watch', 'rugged watch', 'outdoor watch', 'swimming watch'])
        
        # Health monitoring
        if any(word in name_lower for word in ['health', 'heart', 'ultra', 'series']):
            keywords.extend(['health monitor', 'heart rate monitor', 'health tracker', 'medical device'])
    
    # Camping Gear keywords with features
    if 'camping' in category_lower or any(word in name_lower for word in ['tent', 'sleeping', 'coleman', 'nature hike', 'backpack']):
        keywords.extend(['outdoor equipment', 'camping equipment', 'outdoor gear', 'adventure gear'])
        
        # Lightweight and portable
        if any(word in name_lower for word in ['ultralight', 'lightweight', 'compact', 'nature hike']):
            keywords.extend(['lightweight gear', 'ultralight equipment', 'portable gear', 'compact equipment', 'backpacking gear'])
        
        # Tents and shelter
        if 'tent' in name_lower:
            keywords.extend(['shelter', 'camping shelter', 'outdoor shelter', 'portable shelter'])
            
            # Capacity-specific
            if any(word in name_lower for word in ['2', 'two', 'couple']):
                keywords.extend(['2-person tent', 'couple tent', 'small tent', 'compact tent'])
            if any(word in name_lower for word in ['4', 'family', '6']):
                keywords.extend(['family tent', 'large tent', 'group tent', 'multi-person tent'])
        
        # Sleeping gear
        if any(word in name_lower for word in ['sleeping', 'pad', 'bag']):
            keywords.extend(['sleeping gear', 'comfort gear', 'rest equipment'])
        
        # Cooking and utilities
        if any(word in name_lower for word in ['stove', 'lantern', 'cooler']):
            keywords.extend(['camping utilities', 'outdoor cooking', 'camping accessories'])
    
    return keywords

def get_product_keywords_from_dict(product_data: Dict[str, Any]) -> List[str]:
    """Wrapper function for dictionary input (for migration script)"""
    return get_product_keywords(product_data['name'], product_data['category'])

def get_product_keywords_from_product(product) -> List[str]:
    """Wrapper function for Product object input (for AI service)"""
    return get_product_keywords(product.name, product.category)
