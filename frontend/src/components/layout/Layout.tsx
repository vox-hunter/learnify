import React from 'react';
import { Link } from 'react-router-dom';
import { Navigation } from '../common/Navigation';
import styles from '../../styles/Footer.module.css';

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
        <footer className={styles.footer}>
          <div className={styles['footer-content']}>
            <div className={styles['footer-section']}>
              <div className={styles['footer-brand']}>
                <div className={styles['footer-logo']}>🚀</div>
                <span className={styles['footer-brand-name']}>AI Loom</span>
              </div>
              <p className={styles['footer-description']}>
                Transform your documents into interactive learning experiences with AI-powered education.
              </p>
            </div>

            <div className={styles['footer-section']}>
              <h4 className={styles['footer-title']}>Product</h4>
              <ul className={styles['footer-links']}>
                <li><Link to="/" className={styles['footer-link']}>Home</Link></li>
                <li><Link to="/features" className={styles['footer-link']}>Features</Link></li>
                <li><Link to="/pricing" className={styles['footer-link']}>Pricing</Link></li>
                <li><Link to="/docs" className={styles['footer-link']}>Documentation</Link></li>
              </ul>
            </div>

            <div className={styles['footer-section']}>
              <h4 className={styles['footer-title']}>Support</h4>
              <ul className={styles['footer-links']}>
                <li><Link to="/help" className={styles['footer-link']}>Help Center</Link></li>
                <li><Link to="/contact" className={styles['footer-link']}>Contact Us</Link></li>
                <li><Link to="/community" className={styles['footer-link']}>Community</Link></li>
                <li><Link to="/status" className={styles['footer-link']}>Status</Link></li>
              </ul>
            </div>

            <div className={styles['footer-section']}>
              <h4 className={styles['footer-title']}>Legal</h4>
              <ul className={styles['footer-links']}>
                <li><Link to="/privacy" className={styles['footer-link']}>Privacy Policy</Link></li>
                <li><Link to="/terms" className={styles['footer-link']}>Terms of Service</Link></li>
                <li><Link to="/cookies" className={styles['footer-link']}>Cookie Policy</Link></li>
                <li><Link to="/security" className={styles['footer-link']}>Security</Link></li>
              </ul>
            </div>

            <div className={styles['footer-section']}>
              <h4 className={styles['footer-title']}>Connect</h4>
              <ul className={styles['footer-links']}>
                <li><a href="https://twitter.com/ailoom" className={styles['footer-link']} target="_blank" rel="noopener noreferrer">Twitter</a></li>
                <li><a href="https://linkedin.com/company/ailoom" className={styles['footer-link']} target="_blank" rel="noopener noreferrer">LinkedIn</a></li>
                <li><a href="https://github.com/ailoom" className={styles['footer-link']} target="_blank" rel="noopener noreferrer">GitHub</a></li>
                <li><a href="https://blog.ailoom.com" className={styles['footer-link']} target="_blank" rel="noopener noreferrer">Blog</a></li>
              </ul>
            </div>
          </div>

          <div className={styles['footer-bottom']}>
            <div className={styles['footer-bottom-content']}>
              <p className={styles.copyright}>
                © {currentYear} AI Loom. All rights reserved.
              </p>
              <div className={styles['footer-bottom-links']}>
                <span className={styles['footer-version']}>v1.0.0</span>
                <span className={styles['footer-separator']}>•</span>
                <span className={styles['footer-status']}>
                  <span className={styles['status-indicator']}></span>
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