import React from 'react';
import { User } from 'lucide-react';

interface UsersProps {
  users?: Array<{
    name: string;
    avatar?: string;
    role?: string;
  }>;
  className?: string;
}

const Users: React.FC<UsersProps> = ({ users = [], className = '' }) => {
  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      {users.slice(0, 3).map((user, index) => (
        <div
          key={index}
          className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center border-2 border-white -ml-2 first:ml-0"
          title={user.name}
        >
          {user.avatar ? (
            <img
              src={user.avatar}
              alt={user.name}
              className="w-full h-full rounded-full object-cover"
            />
          ) : (
            <User className="w-4 h-4 text-gray-600" />
          )}
        </div>
      ))}
      {users.length > 3 && (
        <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center border-2 border-white -ml-2">
          <span className="text-xs font-medium text-gray-600">+{users.length - 3}</span>
        </div>
      )}
    </div>
  );
};

export { Users };