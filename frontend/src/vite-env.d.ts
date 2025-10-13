/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_BUILD_VERSION: string
  readonly VITE_BUILD_DATE: string
  readonly VITE_IS_CI: string
  readonly VITE_ENVIRONMENT: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
