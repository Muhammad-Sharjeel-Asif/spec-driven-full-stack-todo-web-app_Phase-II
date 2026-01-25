import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Task, CreateTaskRequest } from '@/types/task';
import { Button } from '../UI/Button';
import { Input } from '../UI/Input';

const taskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title must be less than 200 characters'),
  description: z.string().max(1000, 'Description must be less than 1000 characters').optional(),
  dueDate: z.string().optional(),
});

type TaskFormData = z.infer<typeof taskSchema>;

interface TaskFormProps {
  onSubmit: (data: CreateTaskRequest) => void;
  onCancel?: () => void;
  initialData?: Partial<Task>;
  submitButtonText?: string;
  loading?: boolean;
}

export const TaskForm = ({
  onSubmit,
  onCancel,
  initialData,
  submitButtonText = 'Create Task',
  loading = false
}: TaskFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: initialData?.title || '',
      description: initialData?.description || '',
      dueDate: initialData?.dueDate || '',
    }
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFormSubmit = async (data: TaskFormData) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data);
      reset();
    } catch (error) {
      console.error('Failed to submit task:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    reset();
    if (onCancel) {
      onCancel();
    }
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4" role="form" aria-label="Task creation form">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Title *
        </label>
        <Input
          id="title"
          {...register('title')}
          placeholder="Task title"
          className={`${errors.title ? 'border-red-500' : ''}`}
          aria-invalid={!!errors.title}
          aria-describedby={errors.title ? "title-error" : undefined}
        />
        {errors.title && (
          <p id="title-error" className="mt-1 text-sm text-red-600" role="alert">{errors.title.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="description"
          {...register('description')}
          placeholder="Task description (optional)"
          rows={3}
          className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
            errors.description ? 'border-red-500' : 'border-gray-300'
          }`}
          aria-invalid={!!errors.description}
          aria-describedby={errors.description ? "description-error" : undefined}
        />
        {errors.description && (
          <p id="description-error" className="mt-1 text-sm text-red-600" role="alert">{errors.description.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 mb-1">
          Due Date
        </label>
        <Input
          id="dueDate"
          type="date"
          {...register('dueDate')}
          className={`${errors.dueDate ? 'border-red-500' : ''}`}
          aria-invalid={!!errors.dueDate}
          aria-describedby={errors.dueDate ? "dueDate-error" : undefined}
        />
        {errors.dueDate && (
          <p id="dueDate-error" className="mt-1 text-sm text-red-600" role="alert">{errors.dueDate.message}</p>
        )}
      </div>

      <div className="flex space-x-3 pt-2">
        <Button
          type="submit"
          disabled={isSubmitting || loading}
          aria-busy={isSubmitting || loading}
        >
          {isSubmitting || loading ? 'Saving...' : submitButtonText}
        </Button>
        {onCancel && (
          <Button
            type="button"
            variant="outline"
            onClick={handleCancel}
            disabled={isSubmitting}
            aria-label="Cancel form submission"
          >
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
};