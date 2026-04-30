<template>
  <section class="worldline-chat-panel" :class="{ open: isOpen }">
    <header class="panel-header">
      <div class="panel-copy">
        <p class="eyebrow">对话面板</p>
        <strong>直接在工作台中继续对话</strong>
      </div>
      <button class="panel-toggle" type="button" @click="$emit('toggle')">
        {{ isOpen ? '收起' : '展开' }}
      </button>
    </header>

    <div v-if="isOpen" class="panel-body">
      <div v-if="!isLoggedIn" class="panel-empty">
        <p>登录后可在这里直接与模型对话。</p>
        <button class="panel-action" type="button" @click="$emit('open-login')">去登录</button>
      </div>
      <div v-else-if="!chatUrl" class="panel-loading">正在准备对话面板…</div>
      <iframe
        v-else
        class="panel-iframe"
        :src="chatUrl"
        title="Worldline Chat"
        loading="lazy"
        referrerpolicy="no-referrer"
      ></iframe>
    </div>
  </section>
</template>

<script setup>
defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  isLoggedIn: {
    type: Boolean,
    default: false
  },
  chatUrl: {
    type: String,
    default: ''
  }
})

defineEmits(['toggle', 'open-login'])
</script>

<style scoped lang="less">
.worldline-chat-panel {
  border-radius: 22px;
  border: 1px solid color-mix(in srgb, var(--main-200) 50%, transparent);
  background:
    radial-gradient(circle at top right, color-mix(in srgb, var(--main-100) 18%, transparent), transparent 34%),
    linear-gradient(180deg, color-mix(in srgb, var(--gray-0) 92%, transparent), var(--main-10));
  box-shadow: 0 14px 30px color-mix(in srgb, var(--gray-1000) 8%, transparent);
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
}

.panel-copy strong {
  display: block;
  color: var(--gray-1000);
  font-size: 14px;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--main-600);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.panel-toggle {
  border: 1px solid color-mix(in srgb, var(--gray-150) 70%, transparent);
  background: color-mix(in srgb, var(--gray-0) 88%, transparent);
  color: var(--gray-700);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  cursor: pointer;
}

.panel-toggle:hover {
  color: var(--main-700);
  border-color: color-mix(in srgb, var(--main-300) 70%, transparent);
}

.panel-body {
  padding: 0 14px 14px;
}

.panel-empty,
.panel-loading {
  padding: 12px 10px;
  border-radius: 16px;
  background: color-mix(in srgb, var(--gray-0) 86%, transparent);
  border: 1px solid color-mix(in srgb, var(--gray-150) 70%, transparent);
  color: var(--gray-700);
  font-size: 13px;
}

.panel-action {
  margin-top: 10px;
  border: 1px solid color-mix(in srgb, var(--main-300) 70%, transparent);
  background: color-mix(in srgb, var(--main-20) 76%, var(--gray-0));
  color: var(--main-800);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  padding: 6px 12px;
  cursor: pointer;
}

.panel-iframe {
  width: 100%;
  height: 360px;
  border: none;
  border-radius: 16px;
  background: var(--gray-0);
}

@media (max-width: 960px) {
  .panel-iframe {
    height: 320px;
  }
}
</style>
