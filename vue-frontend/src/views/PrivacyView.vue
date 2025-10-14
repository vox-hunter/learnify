<template>
  <div class="privacy-view">
    <div class="container-sm">
      <div class="content-card card">
        <h1 class="page-title">
          Privacy Policy
        </h1>
        
        <div class="content">
          <section class="section">
            <h2>Introduction</h2>
            <p>
              This Privacy Policy describes how AI Loom ("we", "us", or "our") collects, uses, 
              and protects your personal information when you use our AI-powered learning platform.
            </p>
          </section>

          <section class="section">
            <h2>Information We Collect</h2>
            <p>We collect the following types of information:</p>
            <ul>
              <li><strong>Account Information:</strong> Username, email address, and name when you register</li>
              <li><strong>Course Data:</strong> Documents you upload and courses you generate</li>
              <li><strong>Usage Data:</strong> Your progress, quiz answers, and interaction with our platform</li>
              <li><strong>Technical Data:</strong> IP address, browser type, and device information</li>
            </ul>
          </section>

          <section class="section">
            <h2>How We Use Your Information</h2>
            <p>We use your information to:</p>
            <ul>
              <li>Provide and maintain our learning platform</li>
              <li>Generate personalized courses using AI</li>
              <li>Track your learning progress</li>
              <li>Improve our services and user experience</li>
              <li>Send you important updates (if you've opted in)</li>
            </ul>
          </section>

          <section class="section">
            <h2>Data Storage and Security</h2>
            <p>
              We store your data securely using industry-standard encryption and security practices. 
              Your course content and personal information are protected using MongoDB with secure connections.
              We implement appropriate technical and organizational measures to protect your data.
            </p>
          </section>

          <section class="section">
            <h2>AI Processing</h2>
            <p>
              Your uploaded documents are processed using Google's Gemini AI to generate course content. 
              The documents are sent to Google's servers for processing. Please review 
              <a
                href="https://ai.google.dev/terms"
                target="_blank"
                rel="noopener"
              >Google's AI Terms of Service</a> 
              for more information about how they handle data.
            </p>
          </section>

          <section class="section">
            <h2>Your Rights</h2>
            <p>You have the right to:</p>
            <ul>
              <li>Access your personal data</li>
              <li>Correct inaccurate data</li>
              <li>Request deletion of your data</li>
              <li>Export your data</li>
              <li>Opt-out of marketing communications</li>
            </ul>
          </section>

          <section class="section">
            <h2>Cookies</h2>
            <p>
              We use cookies and similar technologies to maintain your session and improve your experience. 
              Essential cookies are necessary for the platform to function, while optional cookies help us 
              analyze usage patterns.
            </p>
          </section>

          <section class="section">
            <h2>Third-Party Services</h2>
            <p>We use the following third-party services:</p>
            <ul>
              <li><strong>Google Gemini AI:</strong> For course content generation</li>
              <li><strong>MongoDB:</strong> For data storage</li>
            </ul>
          </section>

          <section class="section">
            <h2>Changes to This Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify you of any changes 
              by posting the new Privacy Policy on this page and updating the "Last Updated" date.
            </p>
          </section>

          <section class="section">
            <h2>Contact Us</h2>
            <p>
              If you have any questions about this Privacy Policy, please contact us through our platform 
              or reach out to our support team.
            </p>
          </section>

          <div class="last-updated">
            <p><strong>Last Updated:</strong> January 2024</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PrivacyView',
  mounted() {
    this.trackPrivacyView();
  },
  methods: {
    trackPrivacyView() {
      if (typeof this.saEvent === 'function') {
        this.saEvent('privacy_view_opened');
      }
    }
  }
}
</script>

<style scoped>
.privacy-view {
  padding: 2rem 0;
  min-height: calc(100vh - 200px);
}

.content-card {
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 2rem;
  text-align: center;
}

.content {
  color: #cbd5e0;
  line-height: 1.8;
}

.section {
  margin-bottom: 2rem;
}

.section h2 {
  font-size: 1.75rem;
  font-weight: 600;
  color: #06b6d4;
  margin-bottom: 1rem;
}

.section p {
  margin-bottom: 1rem;
}

.section ul {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.section li {
  margin-bottom: 0.5rem;
}

.section a {
  color: #06b6d4;
  text-decoration: underline;
}

.section a:hover {
  color: #0891b2;
}

.last-updated {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 2px solid rgba(6, 182, 212, 0.2);
  text-align: center;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .section h2 {
    font-size: 1.5rem;
  }
}
</style>
