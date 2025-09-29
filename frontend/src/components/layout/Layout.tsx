import React from 'react';
import { Link } from 'react-router-dom';
import { Navigation } from '../common/Navigation';

interface LayoutProps {
  children: React.ReactNode;
  className?: string;
  showNavigation?: boolean;
  showFooter?: boolean;
}

export const Layout: React.FC<LayoutProps> = ({
  children,
  className = '',
  showNavigation = true,
  showFooter = true
}) => {
  const currentYear = new Date().getFullYear();

  return (
    <div className={`layout ${className}`}>
      {showNavigation && <Navigation />}
      
      <main className="main-content">
        {children}
      </main>
      
      {showFooter && (
        <footer className="footer">
          <div className="footer-content">
            <div className="footer-section">
              <div className="footer-brand">
                <div className="footer-logo">🤓</div>
                <span className="footer-brand-name">Learnify</span>
              </div>
              <p className="footer-description">
                Transform your documents into interactive learning experiences with AI-powered education.
              </p>
            </div>

            <div className="footer-section">
              <h4 className="footer-title">Product</h4>
              <ul className="footer-links">
                <li><Link to="/" className="footer-link">Home</Link></li>
                <li><Link to="/features" className="footer-link">Features</Link></li>
                <li><Link to="/pricing" className="footer-link">Pricing</Link></li>
                <li><Link to="/docs" className="footer-link">Documentation</Link></li>
              </ul>
            </div>

            <div className="footer-section">
              <h4 className="footer-title">Support</h4>
              <ul className="footer-links">
                <li><Link to="/help" className="footer-link">Help Center</Link></li>
                <li><Link to="/contact" className="footer-link">Contact Us</Link></li>
                <li><Link to="/community" className="footer-link">Community</Link></li>
                <li><Link to="/status" className="footer-link">Status</Link></li>
              </ul>
            </div>

            <div className="footer-section">
              <h4 className="footer-title">Legal</h4>
              <ul className="footer-links">
                <li><Link to="/privacy" className="footer-link">Privacy Policy</Link></li>
                <li><Link to="/terms" className="footer-link">Terms of Service</Link></li>
                <li><Link to="/cookies" className="footer-link">Cookie Policy</Link></li>
                <li><Link to="/security" className="footer-link">Security</Link></li>
              </ul>
            </div>

            <div className="footer-section">
              <h4 className="footer-title">Connect</h4>
              <ul className="footer-links">
                <li><a href="https://twitter.com/learnify" className="footer-link" target="_blank" rel="noopener noreferrer">Twitter</a></li>
                <li><a href="https://linkedin.com/company/learnify" className="footer-link" target="_blank" rel="noopener noreferrer">LinkedIn</a></li>
                <li><a href="https://github.com/learnify" className="footer-link" target="_blank" rel="noopener noreferrer">GitHub</a></li>
                <li><a href="https://blog.learnify.com" className="footer-link" target="_blank" rel="noopener noreferrer">Blog</a></li>
              </ul>
            </div>
          </div>

          <div className="footer-bottom">
            <div className="footer-bottom-content">
              <p className="copyright">
                © {currentYear} Learnify. All rights reserved.
              </p>
              <div className="footer-bottom-links">
                <span className="footer-version">v1.0.0</span>
                <span className="footer-separator">•</span>
                <span className="footer-status">
                  <span className="status-indicator"></span>
                  All systems operational
                </span>
              </div>
            </div>
          </div>
        </footer>
      )}
    </div>
  );
};