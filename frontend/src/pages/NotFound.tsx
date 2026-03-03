import React from 'react';
import { Link } from 'react-router-dom';

export const NotFound: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center p-6">
      <h1 className="text-6xl font-bold text-primary mb-4">404</h1>
      <p className="text-xl text-muted-foreground mb-8">Page not found</p>
      <Link to="/" className="bg-primary text-primary-foreground px-6 py-2 rounded-lg hover:bg-primary-dark transition-colors">
        Go Home
      </Link>
    </div>
  );
};

export default NotFound;
