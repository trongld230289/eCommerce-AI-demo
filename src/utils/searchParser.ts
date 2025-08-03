import { SearchIntent } from '../types';

export const parseNaturalLanguageSearch = (query: string): SearchIntent => {
  const intent: SearchIntent = {};
  const lowerQuery = query.toLowerCase();

  // Category mapping
  const categoryMap: { [key: string]: string } = {
    'laptop': 'Laptop',
    'máy tính': 'Laptop',
    'điện thoại': 'Điện thoại',
    'phone': 'Điện thoại',
    'smartphone': 'Điện thoại',
    'tai nghe': 'Tai nghe',
    'headphone': 'Tai nghe',
    'máy ảnh': 'Máy ảnh',
    'camera': 'Máy ảnh',
    'máy tính bảng': 'Máy tính bảng',
    'tablet': 'Máy tính bảng',
    'ipad': 'Máy tính bảng',
    'đồng hồ': 'Đồng hồ thông minh',
    'watch': 'Đồng hồ thông minh',
    'tv': 'TV',
    'tivi': 'TV',
    'máy chơi game': 'Máy chơi game',
    'game': 'Máy chơi game'
  };

  // Brand mapping
  const brandMap: { [key: string]: string } = {
    'apple': 'Apple',
    'iphone': 'Apple',
    'macbook': 'Apple',
    'samsung': 'Samsung',
    'galaxy': 'Samsung',
    'dell': 'Dell',
    'sony': 'Sony',
    'canon': 'Canon',
    'nintendo': 'Nintendo',
    'lg': 'LG'
  };

  // Extract category
  for (const [keyword, category] of Object.entries(categoryMap)) {
    if (lowerQuery.includes(keyword)) {
      intent.category = category;
      break;
    }
  }

  // Extract brand
  for (const [keyword, brand] of Object.entries(brandMap)) {
    if (lowerQuery.includes(keyword)) {
      intent.brand = brand;
      break;
    }
  }

  // Extract price range
  const pricePatterns = [
    // "giá dưới 20 triệu", "giá dưới 20000000"
    /(?:giá\s*)?(?:dưới|nhỏ hơn|<)\s*(\d+(?:\.\d+)?)\s*(?:triệu|tr|000000|000\.000)/i,
    // "giá trên 10 triệu", "giá trên 10000000"
    /(?:giá\s*)?(?:trên|lớn hơn|>)\s*(\d+(?:\.\d+)?)\s*(?:triệu|tr|000000|000\.000)/i,
    // "giá từ 5 đến 10 triệu"
    /(?:giá\s*)?(?:từ|from)\s*(\d+(?:\.\d+)?)\s*(?:triệu|tr|000000|000\.000)\s*(?:đến|to|-)\s*(\d+(?:\.\d+)?)\s*(?:triệu|tr|000000|000\.000)/i,
    // "5-10 triệu", "5 đến 10 triệu"
    /(\d+(?:\.\d+)?)\s*(?:triệu|tr|000000|000\.000)\s*(?:đến|to|-)\s*(\d+(?:\.\d+)?)\s*(?:triệu|tr|000000|000\.000)/i
  ];

  for (const pattern of pricePatterns) {
    const match = lowerQuery.match(pattern);
    if (match) {
      if (pattern.source.includes('dưới|nhỏ hơn|<')) {
        // Max price only
        const price = parseFloat(match[1]);
        intent.price_max = price >= 1000 ? price : price * 1000000;
      } else if (pattern.source.includes('trên|lớn hơn|>')) {
        // Min price only  
        const price = parseFloat(match[1]);
        intent.price_min = price >= 1000 ? price : price * 1000000;
      } else {
        // Price range
        const minPrice = parseFloat(match[1]);
        const maxPrice = parseFloat(match[2]);
        intent.price_min = minPrice >= 1000 ? minPrice : minPrice * 1000000;
        intent.price_max = maxPrice >= 1000 ? maxPrice : maxPrice * 1000000;
      }
      break;
    }
  }

  // Extract keywords for general search
  const words = lowerQuery.split(/\s+/);
  const meaningfulWords = words.filter(word => 
    word.length > 2 && 
    !['giá', 'dưới', 'trên', 'từ', 'đến', 'triệu', 'tôi', 'muốn', 'tìm', 'kiếm'].includes(word)
  );

  if (meaningfulWords.length > 0) {
    intent.keywords = meaningfulWords;
  }

  return intent;
};
