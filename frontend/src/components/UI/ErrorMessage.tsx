import React from 'react';

interface ErrorMessageProps {
  message: string;
  className?: string;
  onRetry?: () => void;
  showRetryButton?: boolean;
}

const ErrorMessage = ({
  message,
  className = '',
  onRetry,
  showRetryButton = false
}: ErrorMessageProps) => {
  return (
    <div className={`p-4 bg-red-50 border border-red-200 rounded-md ${className}`}>
      <div className="flex items-start">
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800">Error</h3>
          <div className="mt-2 text-sm text-red-700">
            <p>{message}</p>
          </div>
          {showRetryButton && onRetry && (
            <div className="mt-4">
              <button
                onClick={onRetry}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                Retry
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export { ErrorMessage };