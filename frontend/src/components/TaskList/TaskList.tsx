'use client';

import React, { useState } from 'react';
import { Task } from '@/types/task';
import { useTasks } from '@/hooks/useTasks';
import { TaskItem } from '../TaskItem/TaskItem';
import { Button } from '../UI/Button';
import { Skeleton } from '../UI/Skeleton';
import { ErrorMessage } from '../UI/ErrorMessage';

interface TaskListProps {
  filter?: 'all' | 'active' | 'completed';
  dateFilter?: 'today' | 'week' | 'month' | 'overdue' | null;
}

const TaskList = ({ filter = 'all', dateFilter }: TaskListProps) => {
  const {
    tasks,
    loading,
    error,
    toggleTaskCompletion,
    deleteTask,
    filterTasks
  } = useTasks();

  const [deletingTaskId, setDeletingTaskId] = useState<string | null>(null);

  // Filter tasks based on the selected filter
  const filteredTasks = filterTasks(filter, dateFilter);

  if (loading && tasks.length === 0) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, index) => (
          <Skeleton key={index} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (filteredTasks.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500 text-lg">No tasks found</p>
        <p className="text-gray-400 mt-2">
          {filter === 'completed'
            ? "You haven't completed any tasks yet."
            : filter === 'active'
              ? "All tasks are completed! Add a new task."
              : "Get started by adding a new task."}
        </p>
      </div>
    );
  }

  const handleDeleteTask = async (taskId: string) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setDeletingTaskId(taskId);
    try {
      await deleteTask(taskId);
    } catch (err) {
      console.error('Failed to delete task:', err);
    } finally {
      setDeletingTaskId(null);
    }
  };

  return (
    <div className="space-y-4" role="list" aria-label="List of tasks">
      {filteredTasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onToggleCompletion={toggleTaskCompletion}
          onDelete={handleDeleteTask}
          isDeleting={deletingTaskId === task.id}
        />
      ))}
    </div>
  );
};

export { TaskList };