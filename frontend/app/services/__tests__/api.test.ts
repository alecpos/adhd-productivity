import { describe, expect, it, beforeAll, afterEach, afterAll } from '@jest/globals';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

import api from '../api';

interface APIResponse<T> {
  success: boolean;
  data: T;
}

interface TestData {
  message: string;
}

type TestResponse = APIResponse<TestData>;

// Define your mock handlers
const handlers = [
  rest.get('*/api/test', (req, res, ctx) => {
    return res(
      ctx.json<TestResponse>({
        success: true,
        data: {
          message: 'Success'
        }
      })
    );
  }),
  rest.post('*/api/test', (req, res, ctx) => {
    return res(
      ctx.json<TestResponse>({
        success: true,
        data: {
          message: 'Created'
        }
      })
    );
  }),
  rest.get('*/api/test/error', (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json({
        success: false,
        error: {
          message: 'Internal Server Error'
        }
      })
    );
  })
];

const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  // Reset API headers between tests
  delete api.defaults.headers.Authorization;
});
afterAll(() => server.close());

describe('API Client', () => {
  it('handles successful GET requests', async () => {
    const response = await api.get<TestResponse>('/api/test');
    expect(response.data.success).toBe(true);
    expect(response.data.data.message).toBe('Success');
  });

  it('handles successful POST requests', async () => {
    const response = await api.post<TestResponse>('/api/test');
    expect(response.data.success).toBe(true);
    expect(response.data.data.message).toBe('Created');
  });

  it('handles error responses', async () => {
    await expect(api.get('/api/test/error')).rejects.toThrow();
  });

  it('includes authorization header when token is set', async () => {
    api.defaults.headers.Authorization = 'Bearer test-token';
    const response = await api.get<TestResponse>('/api/test');
    expect(api.defaults.headers.Authorization).toBe('Bearer test-token');
    expect(response.data.success).toBe(true);
  });
});
