import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';

export const PrivacyPage: React.FC = () => {
  const navigate = useNavigate();
  const lastUpdated = 'September 29, 2025';

  return (
    <div className="privacy-page">
      <div className="legal-header">
        <Button
          onClick={() => navigate(-1)}
          variant="ghost"
          leftIcon="←"
          className="back-button"
        >
          Back
        </Button>
        <h1>Privacy Policy</h1>
        <p className="last-updated">Last updated: {lastUpdated}</p>
      </div>

      <div className="legal-content">
        <section className="legal-section">
          <h2>1. Information We Collect</h2>
          <p>
            At Learnify, we collect information to provide you with the best learning experience possible. 
            This includes:
          </p>
          <ul>
            <li><strong>Account Information:</strong> Name, email address, and password when you create an account</li>
            <li><strong>Learning Content:</strong> Documents you upload, URLs you provide, and generated course materials</li>
            <li><strong>Usage Data:</strong> Quiz responses, progress tracking, time spent learning, and performance analytics</li>
            <li><strong>Technical Information:</strong> Device information, browser type, IP address, and usage logs</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>2. How We Use Your Information</h2>
          <p>We use your information to:</p>
          <ul>
            <li>Create personalized learning experiences and course materials</li>
            <li>Track your progress and provide performance insights</li>
            <li>Improve our AI algorithms and service quality</li>
            <li>Send you important updates about your account and our services</li>
            <li>Provide customer support and respond to your inquiries</li>
            <li>Ensure platform security and prevent abuse</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>3. Information Sharing</h2>
          <p>
            We respect your privacy and do not sell your personal information. We may share your information only in these limited circumstances:
          </p>
          <ul>
            <li><strong>Service Providers:</strong> With trusted third-party services that help us operate our platform</li>
            <li><strong>Legal Requirements:</strong> When required by law or to protect our rights and users' safety</li>
            <li><strong>Business Transfers:</strong> In connection with a merger, sale, or transfer of our business</li>
            <li><strong>With Your Consent:</strong> When you explicitly agree to share information with third parties</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>4. Data Security</h2>
          <p>
            We implement industry-standard security measures to protect your information:
          </p>
          <ul>
            <li>Encryption of data in transit and at rest</li>
            <li>Regular security audits and vulnerability assessments</li>
            <li>Access controls and authentication systems</li>
            <li>Secure data centers with physical security measures</li>
            <li>Employee training on data protection and privacy</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>5. Your Rights and Choices</h2>
          <p>You have several rights regarding your personal information:</p>
          <ul>
            <li><strong>Access:</strong> Request a copy of the personal information we have about you</li>
            <li><strong>Correction:</strong> Request corrections to inaccurate or incomplete information</li>
            <li><strong>Deletion:</strong> Request deletion of your personal information (subject to legal requirements)</li>
            <li><strong>Portability:</strong> Request a copy of your data in a machine-readable format</li>
            <li><strong>Opt-out:</strong> Unsubscribe from marketing communications at any time</li>
          </ul>
          <p>
            To exercise these rights, please contact us at <a href="mailto:privacy@learnify.com">privacy@learnify.com</a>.
          </p>
        </section>

        <section className="legal-section">
          <h2>6. Cookies and Tracking</h2>
          <p>
            We use cookies and similar technologies to enhance your experience:
          </p>
          <ul>
            <li><strong>Essential Cookies:</strong> Required for basic platform functionality</li>
            <li><strong>Analytics Cookies:</strong> Help us understand how you use our service</li>
            <li><strong>Preference Cookies:</strong> Remember your settings and preferences</li>
          </ul>
          <p>
            You can control cookie settings through your browser, but disabling certain cookies may affect platform functionality.
          </p>
        </section>

        <section className="legal-section">
          <h2>7. Data Retention</h2>
          <p>
            We retain your information for as long as necessary to provide our services and comply with legal obligations:
          </p>
          <ul>
            <li>Account information: Until you delete your account</li>
            <li>Learning content: Until you remove it or delete your account</li>
            <li>Usage data: Up to 2 years for analytics and improvement purposes</li>
            <li>Legal compliance data: As required by applicable laws</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>8. International Data Transfers</h2>
          <p>
            Your information may be processed and stored in countries other than your own. 
            We ensure appropriate safeguards are in place when transferring data internationally, 
            including:
          </p>
          <ul>
            <li>Standard contractual clauses approved by relevant authorities</li>
            <li>Adequacy decisions by regulatory bodies</li>
            <li>Certification schemes and codes of conduct</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>9. Children's Privacy</h2>
          <p>
            Our service is not intended for children under 13. We do not knowingly collect 
            personal information from children under 13. If we become aware that we have 
            collected personal information from a child under 13, we will take steps to 
            delete such information promptly.
          </p>
        </section>

        <section className="legal-section">
          <h2>10. Changes to This Policy</h2>
          <p>
            We may update this Privacy Policy from time to time. We will notify you of 
            significant changes by:
          </p>
          <ul>
            <li>Posting the updated policy on our website</li>
            <li>Sending you an email notification</li>
            <li>Displaying a notice on our platform</li>
          </ul>
          <p>
            Your continued use of our service after changes take effect constitutes 
            acceptance of the updated policy.
          </p>
        </section>

        <section className="legal-section">
          <h2>11. Contact Us</h2>
          <p>
            If you have questions about this Privacy Policy or our privacy practices, 
            please contact us:
          </p>
          <div className="contact-info">
            <p><strong>Email:</strong> <a href="mailto:privacy@learnify.com">privacy@learnify.com</a></p>
            <p><strong>Mail:</strong> Learnify Privacy Team, 123 Learning Street, Education City, EC 12345</p>
            <p><strong>Phone:</strong> +1 (555) 123-LEARN</p>
          </div>
        </section>
      </div>

      <div className="legal-footer">
        <Button
          onClick={() => navigate('/')}
          variant="primary"
          size="lg"
        >
          Back to Home
        </Button>
      </div>
    </div>
  );
};