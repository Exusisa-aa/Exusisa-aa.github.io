/**
 * 调试开关 —— 通过 URL 参数控制，只在开发/验证时用。
 *
 *   ?noanim          关掉入场动效和滚动吸附，所有内容直接显示
 *   ?api=static      强制走静态快照，不探测后端
 *   ?api=live        强制走后端
 *
 * noanim 主要给截图、录屏、无障碍测试用 ——
 * 无头浏览器截图经常抓在过渡中途，导致画面缺元素。
 */

const params = typeof location !== 'undefined' ? new URLSearchParams(location.search) : null

export function hasParam(name: string): boolean {
  return params?.has(name) ?? false
}

/** 关掉动效 */
export function isNoAnim(): boolean {
  return hasParam('noanim')
}

/** 系统是否要求减少动态效果 */
export function prefersReducedMotion(): boolean {
  return (
    typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches
  )
}

/** 动效应该被跳过（URL 参数或系统偏好任一命中） */
export function shouldSkipAnimation(): boolean {
  return isNoAnim() || prefersReducedMotion()
}
