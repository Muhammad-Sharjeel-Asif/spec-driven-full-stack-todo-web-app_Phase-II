import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { TaskForm } from '../components/TaskForm/TaskForm';

describe('TaskForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  test('renders form elements correctly', () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText(/Title \*/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Due Date/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Create Task/i })).toBeInTheDocument();
  });

  test('validates required title field', async () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const submitButton = screen.getByRole('button', { name: /Create Task/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Title is required/i)).toBeInTheDocument();
    });
  });

  test('allows submission with valid data', async () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    // Fill in the form
    fireEvent.change(screen.getByLabelText(/Title \*/i), {
      target: { value: 'Test Task' }
    });
    fireEvent.change(screen.getByLabelText(/Description/i), {
      target: { value: 'Test Description' }
    });
    fireEvent.change(screen.getByLabelText(/Due Date/i), {
      target: { value: '2025-12-31' }
    });

    const submitButton = screen.getByRole('button', { name: /Create Task/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        title: 'Test Task',
        description: 'Test Description',
        dueDate: '2025-12-31'
      });
    });
  });

  test('shows error when title exceeds character limit', async () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/Title \*/i);
    fireEvent.change(titleInput, {
      target: { value: 'a'.repeat(201) } // Exceeds 200 char limit
    });

    fireEvent.blur(titleInput);

    await waitFor(() => {
      expect(screen.getByText(/Title must be less than 200 characters/i)).toBeInTheDocument();
    });
  });
});