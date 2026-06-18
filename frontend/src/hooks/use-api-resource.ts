"use client";

import { useEffect, useState } from "react";

interface ApiResourceState<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  reload: () => void;
}

export function useApiResource<T>(
  loader: () => Promise<T>,
  deps: readonly unknown[],
): ApiResourceState<T> {
  const [reloadToken, setReloadToken] = useState(0);
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);

    loader()
      .then((result) => {
        if (!active) return;
        setData(result);
        setError(null);
      })
      .catch((err) => {
        if (!active) return;
        setData(null);
        setError(err instanceof Error ? err.message : "Error desconocido");
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [...deps, reloadToken]);

  return {
    data,
    error,
    loading,
    reload: () => {
      setLoading(true);
      setReloadToken((value) => value + 1);
    },
  };
}
