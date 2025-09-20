import request from 'supertest';
import app from './index'; // Import the configured express app
import { auth } from './firebase';

// Mock the entire firebase module
jest.mock('./firebase', () => ({
  auth: {
    createUser: jest.fn(),
    getUserByEmail: jest.fn(),
    createCustomToken: jest.fn(),
  },
}));

// Cast the mock to the correct type to satisfy TypeScript
const mockedAuth = auth as jest.Mocked<typeof auth>;

describe('POST /register', () => {
  afterEach(() => {
    jest.clearAllMocks(); // Clear mocks after each test
  });

  it('should create a new user and return a UID', async () => {
    const userData = { email: 'test@example.com', password: 'password123' };
    const expectedUid = 'test-uid-123';

    // Configure the mock to return a successful response
    mockedAuth.createUser.mockResolvedValue({ uid: expectedUid });

    const response = await request(app)
      .post('/register')
      .send(userData);

    expect(response.status).toBe(201);
    expect(response.body).toEqual({ uid: expectedUid });
    expect(mockedAuth.createUser).toHaveBeenCalledWith(userData);
  });

  it('should return a 400 error if user creation fails', async () => {
    const userData = { email: 'test@example.com', password: 'password123' };
    const errorMessage = 'Email already exists';

    // Configure the mock to throw an error
    mockedAuth.createUser.mockRejectedValue(new Error(errorMessage));

    const response = await request(app)
      .post('/register')
      .send(userData);

    expect(response.status).toBe(400);
    expect(response.body).toEqual({ error: errorMessage });
  });
});