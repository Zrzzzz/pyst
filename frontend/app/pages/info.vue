<template>
  <div class="info-page">
    <!-- 名片容器 -->
    <div class="card-container">
      <div class="card">
        <!-- 头像 -->
        <div class="avatar-wrapper">
          <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="Avatar" class="avatar" />
        </div>

        <!-- 名字 -->
        <h1 class="name">Your Name</h1>

        <!-- 技能列表 -->
        <div class="skills-section">
          <h2 class="skills-title">Skills</h2>
          <div class="skills-grid">
            <div class="skill-tag">Vue.js</div>
            <div class="skill-tag">TypeScript</div>
            <div class="skill-tag">Nuxt</div>
            <div class="skill-tag">SCSS</div>
            <div class="skill-tag">Python</div>
            <div class="skill-tag">Web Design</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主题切换按钮 -->
    <ThemeToggle />
  </div>
</template>

<script setup lang="ts">
import ThemeToggle from '@/components/ThemeToggle.vue'
</script>

<style scoped>
.info-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  position: relative;
}

/* 名片容器 */
.card-container {
  width: 100%;
  max-width: 400px;
  animation: slideUp 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.card {
  background: rgba(21, 26, 33, 0.95);
  backdrop-filter: blur(20px);
  padding: 3rem 2.5rem;
  border-radius: 20px;
  text-align: center;
  border: 1px solid rgba(41, 98, 255, 0.15);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(41, 98, 255, 0.1);
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
}

/* 亮色模式 */
:global(html:not(.dark)) .card {
  background: rgba(248, 249, 250, 0.95);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08), 0 0 20px rgba(41, 98, 255, 0.08);
}

:global(html:not(.dark)) .card:hover {
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.12);
}

/* 头像 */
.avatar-wrapper {
  margin-bottom: 2.5rem;
  display: flex;
  justify-content: center;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid #2962FF;
  box-shadow: 0 4px 16px rgba(41, 98, 255, 0.3);
  transition: all 0.3s ease;
}

.avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(41, 98, 255, 0.4);
}

/* 名字 */
.name {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0 0 2.5rem 0;
  background: linear-gradient(135deg, #2962FF 0%, #3D5AFE 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
}

/* 技能部分 */
.skills-section {
  margin-top: 2.5rem;
  padding-top: 2.5rem;
  border-top: 1px solid rgba(41, 98, 255, 0.1);
}

:global(html:not(.dark)) .skills-section {
  border-top: 1px solid rgba(41, 98, 255, 0.2);
}

.skills-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #EAECEF;
  margin: 0 0 1.5rem 0;
}

:global(html:not(.dark)) .skills-title {
  color: #1F2937;
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.skill-tag {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, rgba(41, 98, 255, 0.1), rgba(61, 90, 254, 0.05));
  border: 1px solid rgba(41, 98, 255, 0.1);
  border-radius: 12px;
  color: #E1E4E8;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: default;
}

:global(html:not(.dark)) .skill-tag {
  background: linear-gradient(135deg, rgba(41, 98, 255, 0.08), rgba(61, 90, 254, 0.04));
  border: 1px solid rgba(41, 98, 255, 0.2);
  color: #374151;
}

.skill-tag:hover {
  background: linear-gradient(135deg, rgba(41, 98, 255, 0.15), rgba(61, 90, 254, 0.1));
  border-color: #2962FF;
  color: #2962FF;
  transform: translateY(-2px);
}

:global(html:not(.dark)) .skill-tag:hover {
  background: linear-gradient(135deg, rgba(41, 98, 255, 0.15), rgba(61, 90, 254, 0.1));
  border-color: #2962FF;
  color: #2962FF;
}

/* 动画 */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card {
    padding: 2.5rem 1.5rem;
  }

  .avatar {
    width: 100px;
    height: 100px;
  }

  .name {
    font-size: 1.75rem;
  }

  .skills-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

