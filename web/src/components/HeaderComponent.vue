<template>
  <div class="header-container">
    <div class="header-content">
      <div class="header-actions" v-if="$slots.left">
        <slot name="left"></slot>
      </div>
      <div class="header-title">
        <div class="header-title-block">
          <h1>{{ title }}</h1>
          <slot name="behind-title"></slot>
        </div>
        <slot name="description">
          <p v-if="description">{{ description }}</p>
        </slot>
      </div>
      <div class="header-actions" v-if="$slots.actions">
        <loading-outlined v-if="loading" />
        <slot name="actions"></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { LoadingOutlined } from '@ant-design/icons-vue'
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped lang="less">
.header-container {
  background:
    linear-gradient(90deg, rgba(7, 15, 24, 0.92), rgba(2, 5, 10, 0.88)),
    radial-gradient(circle at 12% 0%, rgba(var(--wl-gold-rgb), 0.1), transparent 30%);
  backdrop-filter: blur(16px);
  padding: 10px 24px;
  border-bottom: 1px solid var(--wl-border);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.header-title {
  flex: 1;
  width: 100%;
  font-size: 14px;
  color: var(--wl-muted);

  .header-title-block {
    display: flex;
    align-items: baseline;
    gap: 10px;
  }

  h1 {
    margin: 0;
    font-size: 18px;
    font-weight: 800;
    color: var(--wl-text);
  }

  p {
    margin: 4px 0 0;
    color: var(--wl-muted);
  }
}

.header-actions {
  display: flex;
  gap: 8px;
}
</style>
