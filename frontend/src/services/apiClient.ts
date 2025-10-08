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

// Mock auth hook - will be replaced with real implementation later
const useAuth = () => {
    // TODO: Replace with actual auth context
    // Token generated for user Emila (id: 1) - valid for 30 minutes
    // Run: .venv/bin/python create_demo_data.py to generate a new token
    return {
        accessToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJFbWlsYSIsInVzZXJfaWQiOjEsImV4cCI6MTc1OTk0NTE4Mn0.BGQppMUPkqI62xcI0NdnlGpHHw6DYeH356rVCOvHMsA',
    };
};

const BASE_URL = '/api/v1';

/**
 * Centralized API client using native fetch
 * Handles authentication, error handling, and data extraction
 */
export async function apiClient<T>(
    endpoint: string,
    options?: RequestInit
): Promise<T> {
    // Get token from auth context (mock for now)
    const { accessToken } = useAuth();

    // Build full URL
    const url = `${BASE_URL}${endpoint}`;

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

    try {
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

        // Parse response
        const responseData: ApiResponse<T> = await response.json();

        // Validate response format
        if (!responseData.success) {
            throw new Error(responseData.message || 'API request was not successful');
        }

        // Return only the data property
        return responseData.data;
    } catch (error) {
        // Re-throw custom errors
        if (error instanceof Error) {
            throw error;
        }

        // Handle network errors or other unexpected errors
        throw new Error('Network error or unexpected error occurred');
    }
}
