interface TodoItemProps {
  id: string;
  title: string;
  completed: boolean;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}

export function TodoItem({ id, title, completed, onToggle, onDelete }: TodoItemProps) {
  return (
    <div className="flex items-center justify-between p-4 bg-white rounded-lg shadow mb-2">
      <div className="flex items-center">
        <input
          type="checkbox"
          checked={completed}
          onChange={() => onToggle(id)}
          className="mr-3 h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
        />
        <span className={`${completed ? 'line-through text-gray-500' : 'text-gray-800'}`}>
          {title}
        </span>
      </div>
      <button
        onClick={() => onDelete(id)}
        className="text-red-500 hover:text-red-700"
      >
        Delete
      </button>
    </div>
  );
}