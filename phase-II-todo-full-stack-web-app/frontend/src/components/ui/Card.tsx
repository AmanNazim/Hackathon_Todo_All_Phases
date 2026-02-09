import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
}

interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ children, className = '', ...props }) => {
  const classes = `rounded-lg border border-gray-200 bg-white text-card-foreground shadow-sm dark:border-gray-800 dark:bg-gray-900 ${className}`;
  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

const CardHeader: React.FC<CardHeaderProps> = ({ children, className = '', ...props }) => {
  const classes = `flex flex-col space-y-1.5 p-6 ${className}`;
  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

const CardTitle: React.FC<CardTitleProps> = ({ children, className = '', ...props }) => {
  const classes = `text-2xl font-semibold leading-none tracking-tight ${className}`;
  return (
    <h3 className={classes} {...props}>
      {children}
    </h3>
  );
};

const CardContent: React.FC<CardContentProps> = ({ children, className = '', ...props }) => {
  const classes = `p-6 pt-0 ${className}`;
  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

const CardFooter: React.FC<CardFooterProps> = ({ children, className = '', ...props }) => {
  const classes = `flex items-center p-6 pt-0 ${className}`;
  return (
    <div className={classes} {...props}>
      {children}
    </div>
  );
};

export { Card, CardHeader, CardTitle, CardContent, CardFooter };