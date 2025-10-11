import { useState, FormEvent } from 'react';
import { QuizCreateRequest } from '../../types';
import { api } from '../../services/apiClient';
import { useAuth } from '../../context/AuthContext';

interface QuizCreateFormProps {
    onSuccess: () => void;
    onCancel: () => void;
}

/**
 * Form component for creating a new quiz
 */
function QuizCreateForm({ onSuccess, onCancel }: QuizCreateFormProps) {
    const { accessToken } = useAuth();
    const [formData, setFormData] = useState<QuizCreateRequest>({
        name: '',
        subject: '',
        description: '',
    });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Handle input changes
    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    ) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    // Handle form submission
    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();

        if (!accessToken) {
            setError('You must be logged in to create a quiz');
            return;
        }

        // Validation
        if (!formData.name.trim()) {
            setError('Quiz name is required');
            return;
        }

        if (!formData.subject.trim()) {
            setError('Subject is required');
            return;
        }

        setIsSubmitting(true);
        setError(null);

        try {
            // Call API to create quiz
            await api.post('/quizzes/', formData, accessToken);

            // Call onSuccess callback
            onSuccess();
        } catch (err) {
            console.error('Failed to create quiz:', err);
            setError(
                err instanceof Error ? err.message : 'Failed to create quiz'
            );
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="quiz-details-panel">
            <div className="quiz-form-container">
                <h1 className="quiz-form-title">Create New Quiz</h1>

                <form onSubmit={handleSubmit} className="quiz-form">
                    {/* Name Input */}
                    <div className="form-group">
                        <label htmlFor="name" className="form-label">
                            Quiz Name *
                        </label>
                        <input
                            type="text"
                            id="name"
                            name="name"
                            className="form-input"
                            value={formData.name}
                            onChange={handleChange}
                            placeholder="Enter quiz name"
                            required
                            disabled={isSubmitting}
                        />
                    </div>

                    {/* Subject Input */}
                    <div className="form-group">
                        <label htmlFor="subject" className="form-label">
                            Subject *
                        </label>
                        <input
                            type="text"
                            id="subject"
                            name="subject"
                            className="form-input"
                            value={formData.subject}
                            onChange={handleChange}
                            placeholder="e.g., Mathematics, History, Programming"
                            required
                            disabled={isSubmitting}
                        />
                    </div>

                    {/* Description Textarea */}
                    <div className="form-group">
                        <label htmlFor="description" className="form-label">
                            Description
                        </label>
                        <textarea
                            id="description"
                            name="description"
                            className="form-input form-textarea"
                            value={formData.description || ''}
                            onChange={handleChange}
                            placeholder="Enter quiz description (optional)"
                            rows={4}
                            disabled={isSubmitting}
                        />
                    </div>

                    {/* Error Message */}
                    {error && <div className="error-message">{error}</div>}

                    {/* Form Actions */}
                    <div className="form-actions">
                        <button
                            type="button"
                            className="quiz-action-button quiz-action-button--secondary"
                            onClick={onCancel}
                            disabled={isSubmitting}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="quiz-action-button quiz-action-button--primary"
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? 'Creating...' : 'Create Quiz'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default QuizCreateForm;
