import { cn } from "@/lib/utils";

interface PageHeaderProps {
  title: string;
  description?: string;
  eyebrow?: string;
  className?: string;
}

export function PageHeader({ title, description, eyebrow, className }: PageHeaderProps) {
  return (
    <header
      className={cn(
        "space-y-1.5 border-b border-border/60 pb-4 print:hidden",
        className,
      )}
    >
      {eyebrow ? (
        <p className="text-xs font-medium tracking-widest text-primary uppercase">
          {eyebrow}
        </p>
      ) : null}
      <h1 className="text-2xl font-semibold tracking-tight text-foreground">
        {title}
      </h1>
      {description ? (
        <p className="max-w-2xl text-sm leading-relaxed text-muted-foreground">
          {description}
        </p>
      ) : null}
    </header>
  );
}
