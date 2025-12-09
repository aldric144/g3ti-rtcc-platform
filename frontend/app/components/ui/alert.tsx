import * as React from "react";

type AlertVariant = "default" | "destructive" | "warning" | "success";

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: AlertVariant;
  children: React.ReactNode;
}

const variantStyles: Record<AlertVariant, string> = {
  default: "bg-white text-gray-900 border-gray-200",
  destructive: "bg-red-50 text-red-900 border-red-200",
  warning: "bg-yellow-50 text-yellow-900 border-yellow-200",
  success: "bg-green-50 text-green-900 border-green-200",
};

export function Alert({ className = "", variant = "default", children, ...props }: AlertProps) {
  return (
    <div
      role="alert"
      className={`relative w-full rounded-lg border p-4 ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

interface AlertTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
}

export function AlertTitle({ className = "", children, ...props }: AlertTitleProps) {
  return (
    <h5 className={`mb-1 font-medium leading-none tracking-tight ${className}`} {...props}>
      {children}
    </h5>
  );
}

interface AlertDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode;
}

export function AlertDescription({ className = "", children, ...props }: AlertDescriptionProps) {
  return (
    <div className={`text-sm ${className}`} {...props}>
      {children}
    </div>
  );
}
