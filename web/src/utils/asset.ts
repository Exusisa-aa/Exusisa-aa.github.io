/**
 * 资源路径解析 —— 内容里写的路径要用它转一道再交给 <img>/<video>/lightbox。
 *
 * 为什么必须转：
 *   content/*.yaml 里写的 /media/xxx.webp、/certs/xxx.png 是相对
 *   web/public/ 的绝对路径。开发时 Vite 的 base 是 "/"，直接用没问题；
 *   但部署到 GitHub Pages 的子路径（/portfolio/）下，浏览器会去请求
 *   站点根目录的 /media/xxx.webp —— 那个位置什么都没有，全部 404。
 *   表现就是本地好好的，一上线图全挂。
 *
 * 所以所有来自内容数据的资源路径都要过这里，统一加上 BASE_URL 前缀。
 */

export function assetUrl(path: string | null | undefined): string {
  if (!path) return ''

  // 外链和 data URI 原样返回
  if (/^(https?:)?\/\//i.test(path) || path.startsWith('data:')) return path

  const base = import.meta.env.BASE_URL // 结尾一定带 "/"
  return base + path.replace(/^\/+/, '')
}
