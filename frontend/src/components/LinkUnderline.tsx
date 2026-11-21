import React from 'react';

interface LinkUnderlineProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  children: React.ReactNode;
  className?: string;
}

export const LinkUnderline: React.FC<LinkUnderlineProps> = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <a
      className={`link text-paper/80 hover:text-white font-medium transition-colors duration-300 ${className}`}
      {...props}
    >
      {children}
    </a>
  );
};
