import { useCallback, useEffect, useState } from "react";

const STORAGE_KEY = "price_hub_subscriptions";

function readSubscriptions(): string[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as string[]) : [];
  } catch {
    return [];
  }
}

export function useSubscriptions() {
  const [subscriptions, setSubscriptions] = useState<string[]>(readSubscriptions);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(subscriptions));
  }, [subscriptions]);

  const isSubscribed = useCallback(
    (code: string) => subscriptions.includes(code),
    [subscriptions],
  );

  const toggle = useCallback((code: string) => {
    setSubscriptions((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code],
    );
  }, []);

  const remove = useCallback((code: string) => {
    setSubscriptions((prev) => prev.filter((c) => c !== code));
  }, []);

  return { subscriptions, isSubscribed, toggle, remove };
}
