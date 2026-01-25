import { render, screen, fireEvent } from '@testing-library/react';
import { TodoItem } from '../todo-item';

describe('TodoItem', () => {
  const mockOnToggle = jest.fn();
  const mockOnDelete = jest.fn();
  const defaultProps = {
    id: '1',
    title: 'Test Todo',
    completed: false,
    onToggle: mockOnToggle,
    onDelete: mockOnDelete,
  };

  beforeEach(() => {
    mockOnToggle.mockClear();
    mockOnDelete.mockClear();
  });

  it('renders the todo title', () => {
    render(<TodoItem {...defaultProps} />);
    expect(screen.getByText('Test Todo')).toBeInTheDocument();
  });

  it('calls onToggle when checkbox is clicked', () => {
    render(<TodoItem {...defaultProps} />);
    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);
    expect(mockOnToggle).toHaveBeenCalledWith('1');
  });

  it('calls onDelete when delete button is clicked', () => {
    render(<TodoItem {...defaultProps} />);
    const deleteButton = screen.getByText('Delete');
    fireEvent.click(deleteButton);
    expect(mockOnDelete).toHaveBeenCalledWith('1');
  });

  it('displays strikethrough for completed todos', () => {
    render(<TodoItem {...defaultProps} completed={true} />);
    const titleElement = screen.getByText('Test Todo');
    expect(titleElement).toHaveClass('line-through');
  });
});