/// <reference types="vite/client" />

declare module '*.yaml' {
  const content: any;
  export default content;
}

declare module 'virtual:report-summaries' {
  const summaries: Record<string, unknown>;
  export default summaries;
}
