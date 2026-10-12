/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Web3Forms 的 access key。配了它，静态部署时表单也能提交到邮箱。 */
  readonly VITE_WEB3FORMS_KEY?: string
  /** 兜底邮箱，mailto 用。留空则用 profile.yaml 里的主邮箱。 */
  readonly VITE_CONTACT_EMAIL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
