import * as React from "react";

import { cn } from "@/lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "primary" | "secondary";
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = "primary", ...props }, ref) => {
    const variantStyles: Record<string, React.CSSProperties> = {
      primary: {
        backgroundColor:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.bg_color || "#334155",
        color:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.text_color || "white",
        borderColor:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.bg_color || "red",
      },
      secondary: {
        backgroundColor:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.section_bg_color || "#6B7280",
        color:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.text_color || "white",
        borderColor:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.section_separator_color || "#4B5563",
      },
    };

    return (
      <div
        ref={ref}
        // className={cn("relative rounded-xl border bg-card text-card-foreground shadow", className)}
        className={cn("relative rounded-xl border bg-card text-card-foreground", className)}
        style={{ ...variantStyles[variant] }}
        {...props}
      />
    );
  },
);
Card.displayName = "Card";

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, style, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("flex flex-col space-y-1.5 p-6", className)}
      {...props}
      style={{
        color:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.section_header_text_color || "white",
        ...style,
      }}
    />
  ),
);
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3
      ref={ref}
      className={cn("font-semibold leading-none tracking-tight", className)}
      {...props}
    />
  ),
);
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p ref={ref} className={cn("text-sm text-muted-foreground", className)} {...props} />
));
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
  ),
);
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex items-center p-6 pt-0", className)} {...props} />
  ),
);
CardFooter.displayName = "CardFooter";

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };
