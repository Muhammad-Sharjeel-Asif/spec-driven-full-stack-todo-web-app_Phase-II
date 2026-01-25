import React from 'react';
import { Task } from '@/types/task';
import { Button } from '../UI/Button';
import { Spinner } from '../UI/Spinner';

interface TaskItemProps {
  task: Task;
  onToggleCompletion: (taskId: string) => void;
  onDelete: (taskId: string) => void;
  isDeleting: boolean;
}

export const TaskItem = ({ task, onToggleCompletion, onDelete, isDeleting }: TaskItemProps) => {
  const handleToggleCompletion = () => {
    onToggleCompletion(task.id);
  };

  const handleDelete = () => {
    onDelete(task.id);
  };

  return (
    <div
      className="flex items-center justify-between p-4 bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
      role="listitem"
    >
      <div className="flex items-center space-x-3">
        <input
          type="checkbox"
          id={`task-${task.id}`}
          checked={task.completed}
          onChange={handleToggleCompletion}
          className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          aria-label={`Mark task "${task.title}" as ${task.completed ? 'incomplete' : 'complete'}`}
        />
        <div>
          <label
            htmlFor={`task-${task.id}`}
            className={`text-base font-medium ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}
          >
            {task.title}
          </label>
          {task.description && (
            <p className={`text-sm mt-1 ${task.completed ? 'text-gray-400' : 'text-gray-600'}`} aria-label="Task description">
              {task.description}
            </p>
          )}
          {task.dueDate && (
            <p className={`text-xs mt-1 ${task.completed ? 'text-gray-400' : 'text-gray-500'}`} aria-label="Due date">
              Due: {new Date(task.dueDate).toLocaleDateString()}
            </p>
          )}
        </div>
      </div>
      <div className="flex items-center space-x-2">
        {isDeleting ? (
          <Spinner size="sm" />
        ) : (
          <Button
            variant="destructive"
            size="sm"
            onClick={handleDelete}
            aria-label={`Delete task: ${task.title}`}
          >
            Delete
          </Button>
        )}
      </div>
    </div>
  );
};