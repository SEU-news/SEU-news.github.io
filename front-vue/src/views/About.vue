<template>
  <div class="about">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <img v-if="config.platform.logo" :src="config.platform.logo" alt="Logo" class="hero-logo">
        <h1 class="hero-title">{{ config.platform.title }}</h1>
        <h2 class="hero-subtitle">{{ config.platform.subtitle }}</h2>
        <p class="hero-description">{{ config.platform.description }}</p>
      </div>
    </section>

    <!-- Features Section -->
    <section class="section features-section">
      <div class="container">
        <h2 class="section-title">{{ config.platform.title }}</h2>
        <div class="features-grid">
          <AboutFeatureCard
            v-for="(feature, index) in config.platform.features"
            :key="index"
            :icon="feature.icon"
            :title="feature.title"
            :description="feature.description"
          />
        </div>
      </div>
    </section>

    <!-- Team Section -->
    <section class="section team-section">
      <div class="container">
        <h2 class="section-title">{{ config.team.title }}</h2>
        <div class="team-grid">
          <TeamCard
            v-for="(member, index) in config.team.members"
            :key="index"
            :name="member.name"
            :role="member.role"
            :avatar="member.avatar"
            :description="member.description"
            :github="member.github"
          />
        </div>
      </div>
    </section>

    <!-- History Section -->
    <section class="section history-section">
      <div class="container">
        <h2 class="section-title">{{ config.history.title }}</h2>
        <div class="history-container">
          <Timeline :milestones="config.history.milestones" />
        </div>
      </div>
    </section>

    <!-- Contact Section -->
    <section class="section contact-section">
      <div class="container">
        <h2 class="section-title">{{ config.contact.title }}</h2>
        <div class="contact-grid">
          <ContactCard
            v-for="(method, index) in config.contact.methods"
            :key="index"
            :icon="method.icon"
            :label="method.label"
            :value="method.value"
            :link="method.link"
          />
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="container">
        <p class="footer-text">{{ config.footer.copyright }}</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import AboutFeatureCard from '@/components/about/AboutFeatureCard.vue'
import TeamCard from '@/components/about/TeamCard.vue'
import Timeline from '@/components/about/Timeline.vue'
import ContactCard from '@/components/about/ContactCard.vue'
import config from '@/config/about.json'
</script>

<style scoped>
@import '../styles/layout.css';
@import '../styles/animations.css';

.about {
  min-height: 100vh;
  background-color: #fafafa;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 20px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 1;
  animation: fadeInDown 0.8s ease forwards;
}

.hero-logo {
  width: 120px;
  height: 120px;
  object-fit: contain;
  margin-bottom: 30px;
  animation: pulse 2s ease-in-out infinite;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin: 0 0 20px 0;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.hero-subtitle {
  font-size: 1.5rem;
  font-weight: 500;
  margin: 0 0 30px 0;
  opacity: 0.95;
}

.hero-description {
  font-size: 1.1rem;
  line-height: 1.8;
  max-width: 800px;
  margin: 0 auto;
  opacity: 0.9;
}

/* Section Styles */
.section {
  padding: 80px 20px;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  text-align: center;
  margin: 0 0 50px 0;
  position: relative;
  padding-bottom: 20px;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background: linear-gradient(to right, #667eea, #764ba2);
  border-radius: 2px;
}

/* Features Grid */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Team Grid */
.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  max-width: 1000px;
  margin: 0 auto;
}

/* History Container */
.history-container {
  max-width: 800px;
  margin: 0 auto;
}

/* Contact Grid */
.contact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

/* Footer */
.footer {
  background: #2c3e50;
  color: white;
  padding: 30px 20px;
  text-align: center;
}

.footer-text {
  margin: 0;
  font-size: 0.95rem;
  opacity: 0.9;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1.25rem;
  }

  .hero-description {
    font-size: 1rem;
  }

  .hero-logo {
    width: 100px;
    height: 100px;
  }

  .section-title {
    font-size: 2rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .team-grid {
    grid-template-columns: 1fr;
  }

  .contact-grid {
    grid-template-columns: 1fr;
  }
}
</style>
