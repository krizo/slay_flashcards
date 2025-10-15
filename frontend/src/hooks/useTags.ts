import { useState, useEffect } from 'react';
import { Tag, TagCreateRequest, TagUpdateRequest } from '../types';
import { api as apiClient } from '../services/apiClient';

interface UseTagsReturn {
    tags: Tag[];
    loading: boolean;
    error: string | null;
    createTag: (data: TagCreateRequest) => Promise<Tag | null>;
    updateTag: (id: number, data: TagUpdateRequest) => Promise<Tag | null>;
    deleteTag: (id: number) => Promise<boolean>;
    refetch: () => Promise<void>;
}

export const useTags = (accessToken?: string | null): UseTagsReturn => {
    const [tags, setTags] = useState<Tag[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const fetchTags = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await apiClient.get<{ data: Tag[] }>('/tags/', accessToken);
            setTags(response.data.data || []);
        } catch (err: any) {
            console.error('Error fetching tags:', err);
            setError(err.message || 'Failed to fetch tags');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (accessToken) {
            fetchTags();
        }
    }, [accessToken]);

    const createTag = async (data: TagCreateRequest): Promise<Tag | null> => {
        try {
            const response = await apiClient.post<{ data: Tag }>('/tags/', data, accessToken);
            const newTag = response.data.data;
            setTags((prev) => [...prev, newTag].sort((a, b) => a.name.localeCompare(b.name)));
            return newTag;
        } catch (err: any) {
            console.error('Error creating tag:', err);
            setError(err.message || 'Failed to create tag');
            return null;
        }
    };

    const updateTag = async (id: number, data: TagUpdateRequest): Promise<Tag | null> => {
        try {
            const response = await apiClient.put<{ data: Tag }>(`/tags/${id}`, data, accessToken);
            const updatedTag = response.data.data;
            setTags((prev) =>
                prev.map((tag) => (tag.id === id ? updatedTag : tag)).sort((a, b) => a.name.localeCompare(b.name))
            );
            return updatedTag;
        } catch (err: any) {
            console.error('Error updating tag:', err);
            setError(err.message || 'Failed to update tag');
            return null;
        }
    };

    const deleteTag = async (id: number): Promise<boolean> => {
        try {
            await apiClient.delete(`/tags/${id}`, accessToken);
            setTags((prev) => prev.filter((tag) => tag.id !== id));
            return true;
        } catch (err: any) {
            console.error('Error deleting tag:', err);
            setError(err.message || 'Failed to delete tag');
            return false;
        }
    };

    const refetch = async () => {
        await fetchTags();
    };

    return {
        tags,
        loading,
        error,
        createTag,
        updateTag,
        deleteTag,
        refetch,
    };
};
