export interface MockUser {
  email: string;
  password: string;
  displayName: string;
}

export const mockUserList: MockUser[] = [
  { email: "jack@example.com", password: "123456", displayName: "Jack Sparrow" }
];