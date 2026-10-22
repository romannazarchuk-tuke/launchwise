import { useCallback, useEffect, useRef, useState } from "react";

/** A short message at the bottom of the screen, announced to screen readers. */
export function useToast(duration = 2500) {
  const [message, setMessage] = useState<string | null>(null);
  const timer = useRef<number | undefined>(undefined);

  const notify = useCallback(
    (text: string) => {
      setMessage(text);
      window.clearTimeout(timer.current);
      timer.current = window.setTimeout(() => setMessage(null), duration);
    },
    [duration],
  );

  useEffect(() => () => window.clearTimeout(timer.current), []);

  const toast = (
    <div aria-live="polite" role="status" className="pointer-events-none fixed inset-x-0 bottom-6 z-50 flex justify-center px-4">
      {message && (
        <span className="rounded-xl bg-ink px-4 py-2.5 text-[0.95rem] font-semibold text-white shadow-lift">{message}</span>
      )}
    </div>
  );
  return { notify, toast };
}
