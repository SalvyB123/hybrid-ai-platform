// frontend/src/components/ui/spinner.tsx

type SpinnerProps = {
    label?: string;
    className?: string;
};

export default function Spinner({
    label = "Loading…",
    className = "",
}: SpinnerProps) {
    return (
        <div
            className={`flex items-center gap-3 text-muted-foreground ${className}`}
            role="status"
            aria-live="polite"
        >
            <svg
                className="animate-spin h-5 w-5"
                viewBox="0 0 24 24"
                aria-hidden="true"
            >
                <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                />
                <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                />
            </svg>
            <span>{label}</span>
        </div>
    );
}
