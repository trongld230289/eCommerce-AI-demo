import { Product } from '../types';

export const mockProducts: Product[] = [
  {
    id: '1',
    name: 'iPhone 15 Pro',
    description: 'Điện thoại thông minh cao cấp với chip A17 Pro',
    price: 25000000,
    image: 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=400',
    category: 'Điện thoại',
    brand: 'Apple',
    inStock: true,
    stock: 50,
    rating: 4.8,
    reviews: 245
  },
  {
    id: '2',
    name: 'Samsung Galaxy S24 Ultra',
    description: 'Smartphone Android flagship với S Pen',
    price: 22000000,
    image: 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400',
    category: 'Điện thoại',
    brand: 'Samsung',
    inStock: true,
    stock: 30,
    rating: 4.7,
    reviews: 189
  },
  {
    id: '3',
    name: 'Dell XPS 13',
    description: 'Laptop siêu mỏng với màn hình 13.3 inch',
    price: 18000000,
    image: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400',
    category: 'Laptop',
    brand: 'Dell',
    inStock: true,
    stock: 25,
    rating: 4.6,
    reviews: 156
  },
  {
    id: '4',
    name: 'MacBook Air M3',
    description: 'Laptop Apple với chip M3 hiệu năng cao',
    price: 24000000,
    image: 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400',
    category: 'Laptop',
    brand: 'Apple',
    inStock: true,
    stock: 40,
    rating: 4.9,
    reviews: 312
  },
  {
    id: '5',
    name: 'Sony WH-1000XM5',
    description: 'Tai nghe chống ồn cao cấp',
    price: 8500000,
    image: 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400',
    category: 'Tai nghe',
    brand: 'Sony',
    inStock: true,
    stock: 75,
    rating: 4.8,
    reviews: 423
  },
  {
    id: '6',
    name: 'iPad Pro 12.9"',
    description: 'Máy tính bảng chuyên nghiệp với chip M2',
    price: 20000000,
    image: 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400',
    category: 'Máy tính bảng',
    brand: 'Apple',
    inStock: false,
    stock: 0,
    rating: 4.7,
    reviews: 198
  },
  {
    id: '7',
    name: 'Samsung Galaxy Watch 6',
    description: 'Đồng hồ thông minh với tính năng sức khỏe',
    price: 6500000,
    image: 'https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=400',
    category: 'Đồng hồ thông minh',
    brand: 'Samsung',
    inStock: true,
    stock: 60,
    rating: 4.5,
    reviews: 267
  },
  {
    id: '8',
    name: 'Canon EOS R6 Mark II',
    description: 'Máy ảnh mirrorless chuyên nghiệp',
    price: 45000000,
    image: 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400',
    category: 'Máy ảnh',
    brand: 'Canon',
    inStock: true,
    stock: 15,
    rating: 4.9,
    reviews: 89
  },
  {
    id: '9',
    name: 'Nintendo Switch OLED',
    description: 'Máy chơi game cầm tay với màn hình OLED',
    price: 8000000,
    image: 'https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400',
    category: 'Máy chơi game',
    brand: 'Nintendo',
    inStock: true,
    stock: 35,
    rating: 4.6,
    reviews: 445
  },
  {
    id: '10',
    name: 'LG OLED C3 55"',
    description: 'Smart TV OLED 4K với AI ThinQ',
    price: 35000000,
    image: 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400',
    category: 'TV',
    brand: 'LG',
    inStock: true,
    stock: 20,
    rating: 4.8,
    reviews: 156
  }
];

export const categories = [
  'Tất cả',
  'Điện thoại',
  'Laptop',
  'Tai nghe',
  'Máy tính bảng',
  'Đồng hồ thông minh',
  'Máy ảnh',
  'Máy chơi game',
  'TV'
];

export const brands = [
  'Tất cả',
  'Apple',
  'Samsung',
  'Dell',
  'Sony',
  'Canon',
  'Nintendo',
  'LG'
];
