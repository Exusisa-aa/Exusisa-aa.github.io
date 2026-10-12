<script setup lang="ts">
/**
 * 联系 —— 三行，从上到下依次「电话 / 邮箱 / 写信按钮」。
 *
 * 电话和邮箱都是**纯文本**，不做成链接：做成链接反而不好复制
 * （右键菜单、拖选都被链接的默认行为干扰）。这里给它们加了
 * user-select: all —— 点一下整段就选中，Ctrl+C 直接拿走。
 * 真正需要跳转的只有最下面那两个按钮。
 */
import { computed } from 'vue'

import type { ContactItem, StageSection } from '@/api/types'
import { useContentStore } from '@/stores/content'
import { assetUrl } from '@/utils/asset'

const props = defineProps<{ section: StageSection }>()

const content = useContentStore()

const profile = computed(() => content.profile)
const contacts = computed(() => profile.value?.contacts ?? [])

const phone = computed(() => contacts.value.find((c) => c.type === 'phone') ?? null)
const emailContacts = computed(() => contacts.value.filter((c) => c.type === 'email'))

/** compose 没配就退回 mailto，至少不会点了没反应 */
function composeHref(contact: ContactItem): string {
  return contact.compose || contact.href || `mailto:${contact.value}`
}

const resumeUrl = computed(() => assetUrl(profile.value?.resumePdf) || null)
const githubUrl = computed(
  () => contacts.value.find((c) => c.type === 'github')?.href ?? null,
)
</script>

<template>
  <section :id="props.section.id" class="scene center contact-scene">
    <div class="scene-inner">
      <div>
        <p v-reveal class="scene-tag contact-tag">// 找我聊聊</p>

        <h2 v-reveal="1" class="scene-title contact-title">
          项目合作 · 技术交流<br />或只是打个招呼
        </h2>

        <!-- 第一行：电话，最大最亮 -->
        <p v-if="phone" v-reveal="2" class="contact-phone">
          {{ phone.value }}
        </p>

        <!-- 第二行：邮箱，小一号 -->
        <p v-if="emailContacts.length" v-reveal="3" class="contact-emails">
          <span v-for="c in emailContacts" :key="c.value" class="contact-email">
            {{ c.value }}
          </span>
        </p>

        <!-- 第三行：只有这两个是按钮，点了跳到对应邮箱的写信页 -->
        <div v-reveal="4" class="mail-actions">
          <a
            v-for="contact in emailContacts"
            :key="contact.value"
            class="btn ghost mail-btn"
            :href="composeHref(contact)"
            target="_blank"
            rel="noopener"
            :aria-label="`打开 ${contact.label}，给 ${contact.value} 写信`"
          >
            {{ contact.label }} ↗
          </a>
        </div>

        <div v-reveal="5" class="scene-btns contact-actions">
          <a v-if="resumeUrl" class="btn ghost" :href="resumeUrl" target="_blank" rel="noopener">
            查看简历 ↗
          </a>
          <a v-if="githubUrl" class="btn ghost" :href="githubUrl" target="_blank" rel="noopener">
            GitHub ↗
          </a>
        </div>

        <p v-reveal="6" class="contact-copyright">
          © {{ new Date().getFullYear() }} {{ profile?.name }} · {{ profile?.headline }}
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.contact-scene {
  padding-block: 12vh;
}

.contact-tag {
  color: var(--ink-faint) !important;
}

.contact-title {
  font-size: clamp(2.4rem, 5.4vw, 4.4rem);
  margin-bottom: 2.6rem;
}

/*
  user-select: all —— 点一下就把整段选中。
  这两个都是「要被人抄走」的信息，别让人拖半天选不准。
  不做成链接是故意的：链接会带来右键菜单和拖拽的默认行为，反而碍事。
*/
.contact-phone {
  font-family: var(--mono);
  font-size: clamp(1.4rem, 2.6vw, 2.1rem);
  font-weight: 500;
  letter-spacing: 0.06em;
  color: var(--ink);
  margin-bottom: 0.9rem;
  user-select: all;
}

.contact-emails {
  display: flex;
  gap: 1.6rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 2.6rem;
}

.contact-email {
  font-family: var(--mono);
  font-size: clamp(0.8rem, 1.3vw, 0.95rem);
  color: var(--ink-dim);
  letter-spacing: 0.02em;
  user-select: all;
}

/* ---- 写信按钮 ---- */
.mail-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 1.6rem;
}

.mail-btn {
  min-width: 168px;
  justify-content: center;
}

.contact-actions {
  justify-content: center;
  margin-bottom: 2.4rem;
}

.contact-copyright {
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--ink-faint);
  letter-spacing: 0.08em;
}

@media (max-width: 640px) {
  .contact-emails {
    flex-direction: column;
    gap: 0.5rem;
  }

  .mail-btn {
    width: 100%;
    min-width: 0;
  }
}
</style>
