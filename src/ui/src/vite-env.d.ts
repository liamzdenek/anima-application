/// <reference types="vite/client" />

interface ImportMeta {
  readonly env: {
    readonly VITE_API_ENDPOINT?: string;
    [key: string]: string | undefined;
  };
}