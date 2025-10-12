// API Response format based on backend specification
interface ApiResponse<T> {
    success: boolean;
    data: T;
    message?: string;
}

// Pydantic validation error format (422)
interface ValidationError {
    loc: (string | number)[];
    msg: string;
    type: string;
}

interface ValidationErrorResponse {
    detail: ValidationError[];
}

const BASE_URL = '/api/v1';

/**
 * Centralized API client using native fetch
 * Handles authentication, error handling, and data extraction
 */
export async function apiClient<T>(
    endpoint: string,
    options?: RequestInit,
    accessToken?: string | null,
    queryParams?: Record<string, string | number | boolean | undefined>
): Promise<T> {

    // Build full URL with query params
    let url = `${BASE_URL}${endpoint}`;

    if (queryParams) {
        const params = new URLSearchParams();
        Object.entries(queryParams).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                params.append(key, String(value));
            }
        });
        const queryString = params.toString();
        if (queryString) {
            url += `?${queryString}`;
        }
    }

    // Prepare headers
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
    };

    // Add authorization header if token exists
    if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
    }

    // Merge with provided headers
    if (options?.headers) {
        Object.assign(headers, options.headers);
    }

    // Make the request
    const response = await fetch(url, {
        ...options,
        headers,
    });

    // Handle HTTP errors
    if (!response.ok) {
        // Handle 422 Validation Error (Pydantic)
        if (response.status === 422) {
            const errorData: ValidationErrorResponse = await response.json();
            const validationMessages = errorData.detail
                .map((err) => `${err.loc.join('.')}: ${err.msg}`)
                .join(', ');
            throw new Error(`Validation Error: ${validationMessages}`);
        }

        // Handle other HTTP errors
        if (response.status >= 400 && response.status < 500) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(
                errorData.message || `Client Error: ${response.status} ${response.statusText}`
            );
        }

        if (response.status >= 500) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(
                errorData.message || `Server Error: ${response.status} ${response.statusText}`
            );
        }

        throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
    }

    // Handle 204 No Content (e.g., successful DELETE operations)
    if (response.status === 204) {
        return undefined as T;
    }

    // Parse response
    const responseData: ApiResponse<T> = await response.json();

    // Validate response format
    if (!responseData.success) {
        throw new Error(responseData.message || 'API request was not successful');
    }

    // Return only the data property
    return responseData.data;
}

/**
 * Helper functions for common HTTP methods
 */
export const api = {
    get: <T>(endpoint: string, accessToken?: string | null, queryParams?: Record<string, string | number | boolean | undefined>) =>
        apiClient<T>(endpoint, { method: 'GET' }, accessToken, queryParams),

    post: <T>(endpoint: string, data: any, accessToken?: string | null) =>
        apiClient<T>(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        }, accessToken),

    put: <T>(endpoint: string, data: any, accessToken?: string | null) =>
        apiClient<T>(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        }, accessToken),

    patch: <T>(endpoint: string, data: any, accessToken?: string | null) =>
        apiClient<T>(endpoint, {
            method: 'PATCH',
            body: data ? JSON.stringify(data) : undefined,
        }, accessToken),

    delete: <T>(endpoint: string, accessToken?: string | null) =>
        apiClient<T>(endpoint, { method: 'DELETE' }, accessToken),
};
