// Mock user data for testing personalized recommendations
// These users have specific preferences defined in the backend

export interface MockUser {
  email: string;
  password: string;
  displayName: string;
  userId: string;
  description: string;
  preferences: {
    categories: string[];
    brands: string[];
  };
}

export const mockUsers: MockUser[] = [
  {
    email: 'tech.enthusiast@gmail.com',
    password: 'password123',
    displayName: 'Tech Enthusiast',
    userId: 'user1',
    description: 'Loves Apple and Samsung phones & laptops',
    preferences: {
      categories: ['Điện thoại', 'Laptop'],
      brands: ['Apple', 'Samsung']
    }
  },
  {
    email: 'photo.lover@gmail.com', 
    password: 'password123',
    displayName: 'Photo Lover',
    userId: 'user2',
    description: 'Passionate about photography and audio equipment',
    preferences: {
      categories: ['Tai nghe', 'Máy ảnh'],
      brands: ['Sony', 'Canon']
    }
  },
  {
    email: 'gamer.pro@gmail.com',
    password: 'password123', 
    displayName: 'Gamer Pro',
    userId: 'user3',
    description: 'Gaming enthusiast who loves entertainment tech',
    preferences: {
      categories: ['Máy chơi game', 'TV'],
      brands: ['Nintendo', 'LG']
    }
  },
  {
    email: 'test.user@gmail.com',
    password: 'password123',
    displayName: 'Test User', 
    userId: 'testuser',
    description: 'Tech professional focused on productivity',
    preferences: {
      categories: ['Laptop', 'Tai nghe'],
      brands: ['Apple', 'Sony']
    }
  },
  {
    email: 'john.doe@example.com',
    password: 'demo123',
    displayName: 'John Doe',
    userId: 'user1',
    description: 'Demo user with same preferences as Tech Enthusiast',
    preferences: {
      categories: ['Điện thoại', 'Laptop'],
      brands: ['Apple', 'Samsung']
    }
  },
  {
    email: 'jane.smith@example.com',
    password: 'demo123', 
    displayName: 'Jane Smith',
    userId: 'user2',
    description: 'Demo user with same preferences as Photo Lover',
    preferences: {
      categories: ['Tai nghe', 'Máy ảnh'],
      brands: ['Sony', 'Canon']
    }
  }
];

// Quick access to login credentials for testing
export const testCredentials = {
  techEnthusiast: {
    email: 'tech.enthusiast@gmail.com',
    password: 'password123'
  },
  photoLover: {
    email: 'photo.lover@gmail.com', 
    password: 'password123'
  },
  gamerPro: {
    email: 'gamer.pro@gmail.com',
    password: 'password123'
  },
  testUser: {
    email: 'test.user@gmail.com',
    password: 'password123'
  },
  johnDoe: {
    email: 'john.doe@example.com',
    password: 'demo123'
  },
  janeSmith: {
    email: 'jane.smith@example.com',
    password: 'demo123'
  }
};

// Helper function to get user by email
export const getMockUserByEmail = (email: string): MockUser | undefined => {
  return mockUsers.find(user => user.email === email);
};

// Helper function to get user by userId
export const getMockUserByUserId = (userId: string): MockUser | undefined => {
  return mockUsers.find(user => user.userId === userId);
};
