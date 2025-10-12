import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api } from './apiClient';

// Mock global fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('apiClient', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('DELETE requests', () => {
        it('handles 204 No Content response without throwing error', async () => {
            mockFetch.mockResolvedValue({
                ok: true,
                status: 204,
                statusText: 'No Content',
            });

            await expect(api.delete('/quizzes/1', 'mock-token')).resolves.toBeUndefined();

            expect(mockFetch).toHaveBeenCalledWith(
                '/api/v1/quizzes/1',
                expect.objectContaining({
                    method: 'DELETE',
                    headers: expect.objectContaining({
                        'Authorization': 'Bearer mock-token',
                    }),
                })
            );
        });

        it('throws error on 404 response', async () => {
            mockFetch.mockResolvedValue({
                ok: false,
                status: 404,
                statusText: 'Not Found',
                json: vi.fn().mockResolvedValue({ message: 'Quiz not found' }),
            });

            await expect(api.delete('/quizzes/999', 'mock-token')).rejects.toThrow('Quiz not found');
        });

        it('throws error on 500 response', async () => {
            mockFetch.mockResolvedValue({
                ok: false,
                status: 500,
                statusText: 'Internal Server Error',
                json: vi.fn().mockResolvedValue({}),
            });

            await expect(api.delete('/quizzes/1', 'mock-token')).rejects.toThrow('Server Error');
        });
    });

    describe('GET requests', () => {
        it('handles successful response with data', async () => {
            const mockData = { id: 1, name: 'Test Quiz' };
            mockFetch.mockResolvedValue({
                ok: true,
                status: 200,
                json: vi.fn().mockResolvedValue({
                    success: true,
                    data: mockData,
                }),
            });

            const result = await api.get('/quizzes/1', 'mock-token');

            expect(result).toEqual(mockData);
        });
    });

    describe('POST requests', () => {
        it('handles successful response with data', async () => {
            const mockData = { id: 1, name: 'New Quiz' };
            mockFetch.mockResolvedValue({
                ok: true,
                status: 201,
                json: vi.fn().mockResolvedValue({
                    success: true,
                    data: mockData,
                }),
            });

            const result = await api.post('/quizzes', { name: 'New Quiz' }, 'mock-token');

            expect(result).toEqual(mockData);
        });
    });

    describe('PUT requests', () => {
        it('handles successful response with data', async () => {
            const mockData = { id: 1, name: 'Updated Quiz' };
            mockFetch.mockResolvedValue({
                ok: true,
                status: 200,
                json: vi.fn().mockResolvedValue({
                    success: true,
                    data: mockData,
                }),
            });

            const result = await api.put('/quizzes/1', { name: 'Updated Quiz' }, 'mock-token');

            expect(result).toEqual(mockData);
        });
    });
});
