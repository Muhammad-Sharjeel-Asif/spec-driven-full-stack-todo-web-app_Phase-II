import React from 'react';
import { ErrorMessage } from './ErrorMessage';

interface ErrorHandlerProps {
  error: any;
  onRetry?: () => void;
  showRetry?: boolean;
}

export const ErrorHandler: React.FC<ErrorHandlerProps> = ({
  error,
  onRetry,
  showRetry = false
}) => {
  // Determine error type based on HTTP status or error properties
  let errorMessage = 'An unexpected error occurred';
  let errorTitle = 'Error';

  if (error?.response?.status === 401) {
    errorMessage = 'Your session has expired. Please log in again.';
    errorTitle = 'Session Expired';
  } else if (error?.response?.status === 403) {
    errorMessage = 'You do not have permission to access this resource.';
    errorTitle = 'Access Denied';
  } else if (error?.response?.status === 404) {
    errorMessage = 'The requested resource could not be found.';
    errorTitle = 'Not Found';
  } else if (error?.code === 'ECONNABORTED' || error?.code === 'ERR_NETWORK') {
    errorMessage = 'Unable to connect to the server. Please check your internet connection.';
    errorTitle = 'Connection Error';
  } else if (error?.message) {
    errorMessage = error.message;
  }

  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    }
  };

  return (
    <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4 rounded">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800">{errorTitle}</h3>
          <div className="mt-2 text-sm text-red-700">
            <p>{errorMessage}</p>
          </div>
          {showRetry && onRetry && (
            <div className="mt-4">
              <button
                type="button"
                onClick={handleRetry}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
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