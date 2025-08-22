import json
from typing import List, Dict, Any, Optional

class ProductRelationshipService:
    def __init__(self):
        """Initialize with hardcoded product relationships"""
        # Hardcoded product relationships - no Neo4j needed
        self.relationships = {
            # Kịch bản 1: lều -> camping gear -> camera -> phone
            "camping gear": {
                "same_category": ["camping gear"],  # Gợi ý trong cùng category
                "next_category": ["camera"],        # Category tiếp theo
                "items": {
                    "lều": ["túi ngủ", "đèn", "bếp", "ba lô", "giày hiking"],
                    "túi ngủ": ["lều", "đèn", "bàn ghế", "bếp"],
                    "đèn": ["pin", "lều", "túi ngủ", "bếp"], 
                    "bếp": ["gas", "nồi", "đèn", "lều"]
                }
            },
            "camera": {
                "same_category": ["camera"],
                "next_category": ["phone"],
                "items": {
                    "máy ảnh": ["ống kính", "tripod", "thẻ nhớ", "pin sạc"],
                    "canon": ["ống kính canon", "túi đựng", "pin"],
                    "sony": ["ống kính sony", "túi đựng", "pin"]
                }
            },
            "phone": {
                "same_category": ["phone"],
                "next_category": [],  # Không có category tiếp theo
                "items": {
                    "điện thoại": ["ốp lưng", "sạc dự phòng", "tai nghe", "kính cường lực"],
                    "iphone": ["ốp iphone", "airpods", "sạc magsafe"],
                    "samsung": ["ốp samsung", "galaxy buds", "sạc nhanh"]
                }
            },
            
            # Kịch bản 2: watch -> phone (kết nối app)
            "watch": {
                "same_category": ["watch"], 
                "next_category": ["phone"],
                "items": {
                    "đồng hồ thể thao": ["dây đeo", "sạc đồng hồ", "miếng dán màn hình"],
                    "apple watch": ["dây apple watch", "sạc apple watch", "ốp bảo vệ"],
                    "samsung watch": ["dây samsung", "sạc galaxy watch"]
                }
            },
            
            "laptop": {
                "same_category": ["laptop"],
                "next_category": ["camera", "phone"],  # Có thể suggest cả 2
                "items": {
                    "laptop": ["chuột", "bàn phím", "túi laptop", "đế tản nhiệt"],
                    "macbook": ["chuột magic", "bàn phím apple", "hub usb-c"],
                    "gaming laptop": ["chuột gaming", "bàn phím cơ", "tai nghe gaming"]
                }
            }
        }
        
        # Context mapping - từ khóa -> category  
        self.context_keywords = {
            "camping": ["cắm trại", "camping", "du lịch", "outdoor", "lều", "túi ngủ", "leo núi"],
            "photography": ["chụp ảnh", "photography", "photo", "quay video", "vlog", "máy ảnh"],
            "fitness": ["thể thao", "fitness", "tập luyện", "gym", "chạy bộ", "đồng hồ thể thao"],
            "programming": ["lập trình", "programming", "coding", "code", "dev", "developer", "software", "phần mềm"],
            "work": ["làm việc", "work", "học tập", "office", "công việc", "văn phòng"],
            "study": ["học online", "study", "learning", "online class", "distance learning", "e-learning"],
            "entertainment": ["giải trí", "entertainment", "xem phim", "thư giãn", "relax", "binge watching"],
            "gaming": ["chơi game", "gaming", "game", "mobile game", "pc gaming", "gaming setup"],
            "creative": ["thiết kế", "design", "graphic design", "video editing", "content creation", "digital art", "sáng tạo"],
            "travel": ["du lịch", "travel", "vacation", "business trip", "trip", "journey"],
            "social": ["kết nối", "social media", "video call", "conference", "meeting", "livestream", "stream"],
            "communication": ["liên lạc", "gọi điện", "nhắn tin", "điện thoại", "phone"]
        }
        
        # 5 danh mục chính khi hết relationship
        self.all_categories = [
            {"name": "phone", "description": "Điện thoại - Liên lạc và giải trí"},
            {"name": "camera", "description": "Camera - Chụp ảnh và quay video"}, 
            {"name": "laptop", "description": "Laptop - Làm việc và học tập"},
            {"name": "watch", "description": "Đồng hồ - Thể thao và sức khỏe"},
            {"name": "camping gear", "description": "Đồ cắm trại - Du lịch và outdoor"}
        ]
        
        print("✅ ProductRelationshipService initialized with hardcoded relationships")
    def detect_context_from_query(self, user_query: str) -> Optional[str]:
        """Detect context from user query"""
        user_query = user_query.lower()
        
        for context, keywords in self.context_keywords.items():
            if any(keyword in user_query for keyword in keywords):
                if context == "camping":
                    return "camping gear"
                elif context == "photography": 
                    return "camera"
                elif context == "fitness":
                    return "watch"
                elif context == "programming":
                    return "laptop"  # Programming ALWAYS needs laptop
                elif context in ["work", "study"]:
                    return "laptop"  # Work and study need laptop
                elif context == "entertainment":
                    # Smart logic: if mentions "big screen/màn hình lớn" → laptop, else phone
                    return "laptop" if any(word in user_query for word in ["màn hình lớn", "big screen", "larger screen"]) else "phone"
                elif context == "gaming":
                    # Smart logic: mobile gaming → phone, pc gaming → laptop
                    return "phone" if any(word in user_query for word in ["mobile", "di động", "phone"]) else "laptop"
                elif context == "creative":
                    return "laptop"  # Creative work needs powerful laptop
                elif context == "travel":
                    # Business travel → laptop, leisure travel → phone/camera
                    if any(word in user_query for word in ["business", "công tác", "làm việc"]):
                        return "laptop"
                    elif any(word in user_query for word in ["chụp ảnh", "photo", "kỷ niệm"]):
                        return "camera"
                    else:
                        return "phone"  # Default travel device
                elif context == "social":
                    # Video calls → laptop for work, phone for personal
                    return "laptop" if any(word in user_query for word in ["meeting", "conference", "họp"]) else "phone"
                elif context == "communication":
                    return "phone"
                    
        return None
    
    def get_purchased_category(self, purchased_items: List[Dict[str, Any]]) -> Optional[str]:
        """Get category of purchased items"""
        if not purchased_items:
            return None
            
        # Lấy category của item đầu tiên
        first_item = purchased_items[0]
        return first_item.get("category")
    
    def get_same_category_suggestions(self, category: str, purchased_item_name: str = "") -> List[Dict[str, Any]]:
        """Get suggestions within the same category"""
        suggestions = []
        
        if category not in self.relationships:
            return suggestions
            
        category_data = self.relationships[category]
        
        # Tìm items liên quan dựa trên tên sản phẩm đã mua
        if purchased_item_name:
            purchased_name_lower = purchased_item_name.lower()
            found_items = False
            for key, related_items in category_data["items"].items():
                if key in purchased_name_lower or any(part in purchased_name_lower for part in key.split()):
                    for item in related_items[:3]:  # Chỉ lấy 3 items đầu
                        suggestions.append({
                            "category": category,
                            "item_name": item,
                            "relationship": "SAME_CATEGORY",
                            "reason": f"Bổ sung cho {purchased_item_name}",
                            "priority": 1
                        })
                    found_items = True
                    break  # Thoát khỏi loop sau khi tìm thấy match đầu tiên
            
            # Nếu tìm thấy items, return ngay
            if found_items:
                return suggestions
        
        # Nếu không tìm thấy specific items, trả về general items
        if not suggestions and category_data["items"]:
            first_key = list(category_data["items"].keys())[0]
            for item in category_data["items"][first_key][:3]:  # Lấy 3 items đầu
                suggestions.append({
                    "category": category,
                    "item_name": item, 
                    "relationship": "SAME_CATEGORY",
                    "reason": f"Sản phẩm {category} phổ biến",
                    "priority": 2
                })
        
        return suggestions[:4]  # Giới hạn 4 suggestions
    
    def get_next_category_suggestions(self, current_category: str) -> List[Dict[str, Any]]:
        """Get suggestions for next category"""
        suggestions = []
        
        if current_category not in self.relationships:
            return suggestions
            
        next_categories = self.relationships[current_category]["next_category"]
        
        for next_cat in next_categories:
            reason = self._get_transition_reason(current_category, next_cat)
            suggestions.append({
                "category": next_cat,
                "item_name": f"{next_cat} products",
                "relationship": "NEXT_CATEGORY",
                "reason": reason,
                "priority": 1
            })
            
        return suggestions
    
    def _get_transition_reason(self, from_category: str, to_category: str) -> str:
        """Get reason for category transition"""
        transitions = {
            ("camping gear", "camera"): "Chụp ảnh lưu kỷ niệm chuyến đi cắm trại",
            ("camera", "phone"): "Chụp nhanh và chỉnh sửa ảnh từ camera trên điện thoại",
            ("watch", "phone"): "Kết nối với app trên điện thoại để theo dõi sức khỏe",
            ("laptop", "camera"): "Chỉnh sửa video và ảnh chất lượng cao",
            ("laptop", "phone"): "Đồng bộ dữ liệu và làm việc di động"
        }
        
        return transitions.get((from_category, to_category), f"Kết hợp tốt với {from_category}")
    
    def detect_relationship_query(self, user_query: str) -> Optional[str]:
        """Detect if user is asking for complementary/related products using AI-powered detection"""
        user_query = user_query.lower()
        
        # Smart AI-powered detection - look for patterns indicating relationship queries
        relationship_patterns = [
            # Past tense + question about more items (any language)
            ("bought", "anything", "else"),
            ("have", "what", "else"), 
            ("got", "what", "more"),
            ("purchased", "need", "more"),
            ("already", "have", "need"),
            ("own", "what", "additional"),
            
            # Vietnamese patterns
            ("có", "rồi", "cần"),
            ("mua", "rồi", "thêm"),
            ("đã", "có", "gì"),
            ("thiếu", "gì"),
            
            # Generic relationship indicators
            ("what", "else"),
            ("anything", "else"), 
            ("something", "else"),
            ("need", "more"),
            ("buy", "more"),
            ("recommend", "more"),
            ("suggest", "more"),
            ("complement", "with"),
            ("go", "with"),
            ("pair", "with")
        ]
        
        # Check if query matches relationship patterns
        has_relationship_pattern = False
        for pattern in relationship_patterns:
            if all(word in user_query for word in pattern):
                has_relationship_pattern = True
                break
        
        # Also check single keywords that strongly indicate relationships
        single_relationship_keywords = [
            "accessories", "phụ kiện", "đồ đi kèm", "bổ sung", 
            "additional", "complement", "supplement", "enhance"
        ]
        
        has_single_keyword = any(keyword in user_query for keyword in single_relationship_keywords)
        
        if has_relationship_pattern or has_single_keyword:
            # Smart detection of what they already have (multi-language)
            product_mentions = {
                "camping": ["lều", "tent", "camping", "cắm trại", "outdoor", "hiking"],
                "photography": ["camera", "máy ảnh", "canon", "sony", "nikon", "photo", "chụp ảnh"],  
                "fitness": ["đồng hồ", "watch", "fitness", "thể thao", "apple watch", "galaxy watch"],
                "communication": ["phone", "điện thoại", "iphone", "samsung", "mobile"],
                "work": ["laptop", "máy tính", "macbook", "dell", "hp", "computer", "pc"]
            }
            
            # Find what product category is mentioned
            for context, keywords in product_mentions.items():
                if any(keyword in user_query for keyword in keywords):
                    return context
            
            # If no specific product mentioned, return general
            return "general"
                
        return None
        
    def get_smart_suggestions(self, user_query: str, purchased_products: List[Dict[str, Any]]) -> Dict[str, Any]:
        
        # Get purchased category first (more important than context)
        purchased_category = self.get_purchased_category(purchased_products)
        purchased_item_name = purchased_products[0].get("name", "") if purchased_products else ""
        
        # Check if this is a relationship query (asking for more after buying something)
        is_relationship_query = any(keyword in user_query.lower() 
            for keyword in ["mua gì thêm", "cần gì nữa", "what else", "what more", "còn thiếu gì", "cần thêm", "mua thêm", "cần mua thêm gì"])
        
        # Detect context from query (secondary priority)
        query_context = self.detect_context_from_query(user_query)
        
        suggestions = []
        explanation = ""
        
        # PRIORITY 1: User has purchased something AND asking for more (relationship flow)
        if purchased_category and is_relationship_query:
            
            # First: suggest same category items
            same_cat_suggestions = self.get_same_category_suggestions(purchased_category, purchased_item_name)
            suggestions.extend(same_cat_suggestions)
            
            # Then: suggest next category (this is the key part!)
            next_cat_suggestions = self.get_next_category_suggestions(purchased_category)
            suggestions.extend(next_cat_suggestions)
            
            explanation = f"Dựa trên {purchased_item_name} bạn đã mua, đây là những gợi ý bổ sung:"
        
        # PRIORITY 2: User asking for specific context but hasn't bought anything yet
        elif query_context and not purchased_category:
            # Direct category suggestion
            suggestions.append({
                "category": query_context,
                "item_name": f"{query_context} essentials",
                "relationship": "CONTEXT_MATCH",
                "reason": f"Sản phẩm phù hợp cho {self._get_context_description(query_context)}",
                "priority": 1
            })
            explanation = f"Dựa trên nhu cầu {self._get_context_description(query_context)}, đây là gợi ý phù hợp:"
            # Direct category suggestion
            suggestions.append({
                "category": query_context,
                "item_name": f"{query_context} essentials",
                "relationship": "CONTEXT_MATCH",
                "reason": f"Sản phẩm phù hợp cho {self._get_context_description(query_context)}",
                "priority": 1
            })
            explanation = f"Dựa trên nhu cầu {self._get_context_description(query_context)}, đây là gợi ý phù hợp:"
        
        # Case 3: No specific relationship found - show all categories
        else:
            for cat_info in self.all_categories:
                suggestions.append({
                    "category": cat_info["name"],
                    "item_name": cat_info["name"],
                    "relationship": "ALL_CATEGORIES", 
                    "reason": cat_info["description"],
                    "priority": 3
                })
            explanation = "Bạn có thể khám phá các danh mục sản phẩm sau:"
        
        return {
            "context": query_context,
            "purchased_categories": [purchased_category] if purchased_category else [],
            "suggestions": suggestions,
            "explanation": explanation
        }
    
    def _get_context_description(self, context: str) -> str:
        """Get description for context"""
        descriptions = {
            "camping gear": "cắm trại và outdoor",
            "camera": "chụp ảnh và quay video",
            "phone": "liên lạc và giải trí",
            "laptop": "làm việc và học tập", 
            "watch": "thể thao và sức khỏe"
        }
        return descriptions.get(context, context)
    
    def close(self):
        """Placeholder for consistency with Neo4j version"""
        pass


# Test scenarios
def create_test_scenarios():
    """Create test scenarios for the two main flows"""
    return {
        "scenario_1_camping_flow": [
            {
                "step": 1,
                "user_query": "mua gì để đi cắm trại",
                "purchased_items": [],
                "expected_category": "camping gear"
            },
            {
                "step": 2, 
                "user_query": "đã mua lều rồi, cần mua gì thêm để cắm trại",
                "purchased_items": [{"category": "camping gear", "name": "lều"}],
                "expected_suggestions": ["túi ngủ", "đèn", "bếp", "ba lô"]
            },
            {
                "step": 3,
                "user_query": "ngoài đồ camping ra còn cần gì khác không",
                "purchased_items": [{"category": "camping gear", "name": "lều"}],
                "expected_next_category": "camera"
            },
            {
                "step": 4,
                "user_query": "đã có camera rồi, mua gì nữa",
                "purchased_items": [{"category": "camera", "name": "máy ảnh"}],
                "expected_next_category": "phone"
            }
        ],
        
        "scenario_2_fitness_flow": [
            {
                "step": 1,
                "user_query": "mua gì để tập thể thao",
                "purchased_items": [],
                "expected_category": "watch"
            },
            {
                "step": 2,
                "user_query": "có đồng hồ thể thao rồi, cần mua thêm gì không",
                "purchased_items": [{"category": "watch", "name": "đồng hồ thể thao"}],
                "expected_next_category": "phone"
            },
            {
                "step": 3,
                "user_query": "mua gì nữa không có quan hệ",
                "purchased_items": [],
                "expected_all_categories": True
            }
        ]
    }


# Test function
def test_relationship_scenarios():
    """Test the relationship scenarios"""
    print("🧪 Testing Product Relationship Scenarios")
    print("=" * 50)
    
    service = ProductRelationshipService()
    test_scenarios = create_test_scenarios()
    
    # Test Scenario 1: Camping Flow
    print("\n📋 SCENARIO 1: CAMPING FLOW")
    print("lều -> camping gear -> camera -> phone")
    print("-" * 40)
    
    for test_case in test_scenarios["scenario_1_camping_flow"]:
        print(f"\nStep {test_case['step']}: {test_case['user_query']}")
        print(f"Purchased: {test_case['purchased_items']}")
        
        result = service.get_smart_suggestions(test_case['user_query'], test_case['purchased_items'])
        
        print(f"Context: {result['context']}")
        print(f"Explanation: {result['explanation']}")
        print("Suggestions:")
        for suggestion in result['suggestions'][:3]:  # Show top 3
            print(f"  - {suggestion['category']}: {suggestion['reason']}")
    
    # Test Scenario 2: Fitness Flow
    print("\n\n📋 SCENARIO 2: FITNESS FLOW")  
    print("watch -> phone -> all categories")
    print("-" * 40)
    
    for test_case in test_scenarios["scenario_2_fitness_flow"]:
        print(f"\nStep {test_case['step']}: {test_case['user_query']}")
        print(f"Purchased: {test_case['purchased_items']}")
        
        result = service.get_smart_suggestions(test_case['user_query'], test_case['purchased_items'])
        
        print(f"Context: {result['context']}")
        print(f"Explanation: {result['explanation']}")
        print("Suggestions:")
        for suggestion in result['suggestions'][:5]:  # Show top 5
            print(f"  - {suggestion['category']}: {suggestion['reason']}")
    
    service.close()
    print("\n✅ Test completed!")


# Initialize relationship data (no-op for hardcoded version)
def initialize_product_relationships():
    """Initialize the product relationship system"""
    print("✅ Product relationships initialized (hardcoded version)")
    return True

if __name__ == "__main__":
    # Run test scenarios
    test_relationship_scenarios()
