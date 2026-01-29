import React, { useState } from 'react';
import PropTypes from 'prop-types';

/**
 * TaskToggle component - A reusable toggle switch for marking tasks as complete/incomplete
 * Implements optimistic UI updates for immediate visual feedback
 * @param {Object} task - The task object containing id, title, completed status, etc.
 * @param {Function} onUpdate - Callback function to handle task updates
 * @param {boolean} disabled - Whether the toggle is disabled (optional)
 * @param {boolean} externalLoading - Whether an external loading state is active (optional)
 */
const TaskToggle = ({ task, onUpdate, disabled = false, externalLoading = false }) => {
  const [internalLoading, setInternalLoading] = useState(false);
  // Use optimistic update to immediately reflect the change in UI
  const [optimisticCompleted, setOptimisticCompleted] = useState(task.completed);

  const handleToggle = async () => {
    if (disabled || externalLoading || internalLoading) return;

    try {
      // Optimistically update the UI before making the API call
      const newCompletedStatus = !optimisticCompleted;
      setOptimisticCompleted(newCompletedStatus);
      setInternalLoading(true);

      // Call the onUpdate callback with the updated task
      await onUpdate({
        ...task,
        completed: newCompletedStatus
      });
    } catch (error) {
      // If the API call fails, revert the optimistic update
      setOptimisticCompleted(task.completed);
      console.error('Failed to update task completion:', error);

      // Show error message to user
      if (error.status === 404) {
        alert('Task not found. It may have been deleted by another process.');
      } else if (error.status === 403) {
        alert('Access denied. You cannot modify this task.');
      } else {
        alert('Failed to update task completion. Please try again.');
      }
    } finally {
      setInternalLoading(false);
    }
  };

  const isPending = internalLoading || externalLoading;

  return (
    <button
      type="button"
      onClick={handleToggle}
      disabled={disabled || isPending}
      className={`
        relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-200 ease-in-out
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
        ${isPending
          ? 'opacity-70 cursor-not-allowed'
          : 'hover:scale-105 cursor-pointer'}
        ${optimisticCompleted
          ? 'bg-green-500 hover:bg-green-600'
          : 'bg-gray-300 hover:bg-gray-400'}
      `}
      aria-checked={optimisticCompleted}
      role="switch"
      aria-label={optimisticCompleted ? 'Mark as incomplete' : 'Mark as complete'}
    >
      <span
        className={`
          inline-block h-4 w-4 transform rounded-full bg-white shadow-lg ring-0
          transition-all duration-200 ease-in-out
          ${optimisticCompleted ? 'translate-x-6' : 'translate-x-1'}
          ${isPending ? 'animate-pulse' : ''}
        `}
      />
      {isPending && (
        <span className="absolute inset-0 flex items-center justify-center">
          <svg
            className="h-3 w-3 text-white animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        </span>
      )}
      {!isPending && (
        <span className="absolute inset-0 flex items-center justify-center">
          {optimisticCompleted ? (
            <svg
              className="h-3 w-3 text-green-600"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
          ) : (
            <svg
              className="h-3 w-3 text-gray-400"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </span>
      )}
    </button>
  );
};

TaskToggle.propTypes = {
  task: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    title: PropTypes.string.isRequired,
    completed: PropTypes.bool.isRequired,
    // Optional properties that might be in the task object
    description: PropTypes.string,
    createdAt: PropTypes.oneOfType([PropTypes.string, PropTypes.instanceOf(Date)]),
    updatedAt: PropTypes.oneOfType([PropTypes.string, PropTypes.instanceOf(Date)])
  }).isRequired,
  onUpdate: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
  externalLoading: PropTypes.bool
};

TaskToggle.defaultProps = {
  disabled: false,
  externalLoading: false
};

export default TaskToggle;