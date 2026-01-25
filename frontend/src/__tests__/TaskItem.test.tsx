import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { TaskItem } from '../components/TaskItem/TaskItem';

describe('TaskItem', () => {
  const mockTask = {
    id: '1',
    title: 'Test Task',
    description: 'Test Description',
    completed: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    userId: 'user123'
  };

  const mockOnToggleCompletion = jest.fn();
  const mockOnDelete = jest.fn();

  beforeEach(() => {
    mockOnToggleCompletion.mockClear();
    mockOnDelete.mockClear();
  });

  test('renders task information correctly', () => {
    render(
      <TaskItem
        task={mockTask}
        onToggleCompletion={mockOnToggleCompletion}
        onDelete={mockOnDelete}
        isDeleting={false}
      />
    );

    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
    expect(screen.getByRole('checkbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Delete/i })).toBeInTheDocument();
  });

  test('calls onToggleCompletion when checkbox is clicked', () => {
    render(
      <TaskItem
        task={mockTask}
        onToggleCompletion={mockOnToggleCompletion}
        onDelete={mockOnDelete}
        isDeleting={false}
      />
    );

    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);

    expect(mockOnToggleCompletion).toHaveBeenCalledWith('1');
  });

  test('calls onDelete when delete button is clicked', () => {
    render(
      <TaskItem
        task={mockTask}
        onToggleCompletion={mockOnToggleCompletion}
        onDelete={mockOnDelete}
        isDeleting={false}
      />
    );

    const deleteButton = screen.getByRole('button', { name: /Delete/i });
    fireEvent.click(deleteButton);

    expect(mockOnDelete).toHaveBeenCalledWith('1');
  });

  test('shows spinner when isDeleting is true', () => {
    render(
      <TaskItem
        task={mockTask}
        onToggleCompletion={mockOnToggleCompletion}
        onDelete={mockOnDelete}
        isDeleting={true}
      />
    );

    expect(screen.getByRole('status')).toBeInTheDocument(); // Spinner element
  });

  test('applies strikethrough to completed task', () => {
    const completedTask = { ...mockTask, completed: true };

    render(
      <TaskItem
        task={completedTask}
        onToggleCompletion={mockOnToggleCompletion}
        onDelete={mockOnDelete}
        isDeleting={false}
      />
    );

    const taskLabel = screen.getByText('Test Task');
    expect(taskLabel).toHaveClass('line-through');
  });
});