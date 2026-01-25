import { Todo } from '@/types/todo';

export function createTodo(title: string): Todo {
  const now = new Date();
  return {
    id: generateId(),
    title,
    completed: false,
    createdAt: now,
    updatedAt: now,
  };
}

export function toggleTodo(todo: Todo): Todo {
  return {
    ...todo,
    completed: !todo.completed,
    updatedAt: new Date(),
  };
}

function generateId(): string {
  return Math.random().toString(36).substr(2, 9);
}

export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}