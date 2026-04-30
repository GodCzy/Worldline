<template>
  <div class="theme-hub-view">
    <header class="hub-header">
      <router-link to="/" class="brand-link">
        <img
          v-if="infoStore.organization.logo"
          :src="infoStore.organization.logo"
          :alt="infoStore.organization.name"
          class="brand-logo"
        />
        <span>{{ infoStore.organization.name }}</span>
      </router-link>
      <div class="header-actions">
        <a
          v-if="docsUrl"
          class="header-link"
          :href="docsUrl"
          target="_blank"
          rel="noopener noreferrer"
        >
          文档中心
        </a>
      </div>
    </header>

    <main class="hub-main">
      <section class="hero-card">
        <p class="eyebrow">主题模块</p>
        <h1>{{ infoStore.branding.title }}</h1>
        <p class="subtitle">{{ infoStore.branding.subtitle }}</p>
        <p v-if="infoStore.branding.description" class="description">
          {{ infoStore.branding.description }}
        </p>
      </section>

      <section class="theme-section">
        <div class="section-header">
          <h2>主题分区</h2>
          <p>从这里进入不同主题模块，系统会在后续页面持续保留当前主题上下文。</p>
        </div>

        <div v-if="themes.length" class="theme-grid">
          <article v-for="theme in themes" :key="theme.id" class="theme-card">
            <div class="theme-card-head">
              <div>
                <p class="theme-status">{{ theme.status }}</p>
                <h3>{{ theme.name }}</h3>
                <p class="theme-subtitle">{{ theme.subtitle }}</p>
              </div>
              <button class="enter-button" @click="openTheme(theme)">进入主题</button>
            </div>

            <p class="theme-description">{{ theme.description }}</p>

            <div v-if="theme.tags.length" class="theme-tags">
              <span v-for="tag in theme.tags" :key="tag">{{ tag }}</span>
            </div>

            <ul v-if="theme.highlights.length" class="theme-highlights">
              <li v-for="item in theme.highlights" :key="item">{{ item }}</li>
            </ul>
          </article>
        </div>

        <a-empty v-else description="暂无可展示的主题模块" />
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInfoStore } from '@/stores/info'

const router = useRouter()
const infoStore = useInfoStore()

const themes = computed(() => infoStore.themes || [])
const docsUrl = computed(() => infoStore.docsUrl || '')

const openTheme = (theme) => {
  router.push(theme.entry_route || `/themes/${theme.id}`)
}

onMounted(() => {
  infoStore.loadInfoConfig()
})
</script>

<style scoped lang="less">
.theme-hub-view {
  min-height: 100vh;
  background:
    radial-gradient(circle at top right, var(--main-50), transparent 40%),
    linear-gradient(180deg, var(--gray-10), var(--gray-0));
}

.hub-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  border-bottom: 1px solid var(--gray-100);
  background: color-mix(in srgb, var(--gray-0) 85%, transparent);
  backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 20;
}

.brand-link {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: var(--main-800);
  font-size: 18px;
  font-weight: 700;
  text-decoration: none;
}

.brand-logo {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-link {
  color: var(--gray-700);
  text-decoration: none;
  font-size: 14px;

  &:hover {
    color: var(--main-600);
  }
}

.hub-main {
  max-width: 1180px;
  margin: 0 auto;
  padding: 48px 24px 72px;
}

.hero-card {
  padding: 32px;
  border-radius: 24px;
  background: var(--gray-0);
  border: 1px solid var(--gray-100);
  box-shadow: 0 24px 48px rgba(3, 80, 101, 0.08);
}

.eyebrow {
  margin: 0 0 12px;
  color: var(--main-600);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.hero-card h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3.4rem);
  line-height: 1.08;
  color: var(--main-900);
}

.subtitle {
  margin: 16px 0 0;
  font-size: 1.2rem;
  color: var(--gray-700);
}

.description {
  margin: 16px 0 0;
  max-width: 760px;
  color: var(--gray-600);
  line-height: 1.7;
}

.theme-section {
  margin-top: 40px;
}

.section-header {
  margin-bottom: 20px;

  h2 {
    margin: 0;
    color: var(--main-900);
    font-size: 1.7rem;
  }

  p {
    margin: 8px 0 0;
    color: var(--gray-600);
  }
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.theme-card {
  padding: 24px;
  border-radius: 20px;
  border: 1px solid var(--gray-100);
  background: var(--gray-0);
  box-shadow: 0 14px 36px rgba(3, 80, 101, 0.06);
}

.theme-card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.theme-status {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--main-600);
}

.theme-card h3 {
  margin: 0;
  color: var(--main-900);
  font-size: 1.35rem;
}

.theme-subtitle {
  margin: 8px 0 0;
  color: var(--gray-600);
  font-size: 0.95rem;
}

.theme-description {
  margin: 18px 0 0;
  color: var(--gray-700);
  line-height: 1.7;
}

.theme-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;

  span {
    padding: 6px 10px;
    border-radius: 999px;
    background: var(--main-20);
    color: var(--main-700);
    font-size: 12px;
    font-weight: 600;
  }
}

.theme-highlights {
  margin: 18px 0 0;
  padding-left: 18px;
  color: var(--gray-600);
  line-height: 1.7;
}

.enter-button {
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--main-600), var(--main-500));
  color: var(--gray-0);
  padding: 10px 16px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .hub-header {
    padding: 18px 16px;
    gap: 12px;
    flex-wrap: wrap;
  }

  .hub-main {
    padding: 24px 16px 56px;
  }

  .hero-card,
  .theme-card {
    padding: 20px;
  }

  .theme-card-head {
    flex-direction: column;
  }

  .enter-button {
    width: 100%;
  }
}
</style>
