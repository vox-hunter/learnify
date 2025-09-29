import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Button } from '../ui/Button';
import { useAuth } from '../../hooks/useAuth';
import styles from '../../styles/Navigation.module.css';

export const Navigation: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
    setIsMobileMenuOpen(false);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  const isActiveRoute = (path: string) => {
    return location.pathname === path;
  };

  return (
    <nav className={styles.navigation}>
      <div className={styles['nav-container']}>
        {/* Logo and Brand */}
        <div className={styles['nav-brand']}>
          <Link to="/" className={styles['brand-link']} onClick={closeMobileMenu}>
            <div className={styles['brand-logo']}>🚀</div>
            <span className={styles['brand-name']}>AI Loom</span>
          </Link>
        </div>

        {/* Desktop Navigation */}
        <div className={`${styles['nav-links']} ${styles['desktop-nav']}`}>
          <Link 
            to="/" 
            className={`${styles['nav-link']} ${isActiveRoute('/') ? styles.active : ''}`}
          >
            Home
          </Link>
          
          {isAuthenticated && (
            <>
              <Link 
                to="/dashboard" 
                className={`${styles['nav-link']} ${isActiveRoute('/dashboard') ? styles.active : ''}`}
              >
                Dashboard
              </Link>
              <Link 
                to="/courses" 
                className={`${styles['nav-link']} ${isActiveRoute('/courses') ? styles.active : ''}`}
              >
                My Courses
              </Link>
            </>
          )}
        </div>

        {/* Desktop Auth Section */}
        <div className={`${styles['nav-auth']} ${styles['desktop-nav']}`}>
          {isAuthenticated ? (
            <div className={styles['user-menu']}>
              <div className={styles['user-info']}>
                <span className={styles['user-name']}>Hi, {user?.name}</span>
                {user?.avatar && (
                  <img 
                    src={user.avatar} 
                    alt={user.name} 
                    className={styles['user-avatar']}
                  />
                )}
              </div>
              <Button
                onClick={handleLogout}
                variant="ghost"
                size="sm"
                className={styles['logout-button']}
              >
                Sign Out
              </Button>
            </div>
          ) : (
            <div className={styles['auth-buttons']}>
              <Button
                onClick={() => navigate('/login')}
                variant="ghost"
                size="sm"
              >
                Sign In
              </Button>
              <Button
                onClick={() => navigate('/login?mode=register')}
                variant="primary"
                size="sm"
              >
                Sign Up
              </Button>
            </div>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button 
          className={styles['mobile-menu-toggle']}
          onClick={toggleMobileMenu}
          aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
        >
          <span className={styles['hamburger-line']}></span>
          <span className={styles['hamburger-line']}></span>
          <span className={styles['hamburger-line']}></span>
        </button>
      </div>

      {/* Mobile Navigation Menu */}
      {isMobileMenuOpen && (
        <div className={styles['mobile-nav']}>
          <div className={styles['mobile-nav-content']}>
            <div className={styles['mobile-nav-links']}>
              <Link 
                to="/" 
                className={`${styles['mobile-nav-link']} ${isActiveRoute('/') ? styles.active : ''}`}
                onClick={closeMobileMenu}
              >
                🏠 Home
              </Link>
              
              {isAuthenticated && (
                <>
                  <Link 
                    to="/dashboard" 
                    className={`${styles['mobile-nav-link']} ${isActiveRoute('/dashboard') ? styles.active : ''}`}
                    onClick={closeMobileMenu}
                  >
                    📈 Dashboard
                  </Link>
                  <Link 
                    to="/courses" 
                    className={`${styles['mobile-nav-link']} ${isActiveRoute('/courses') ? styles.active : ''}`}
                    onClick={closeMobileMenu}
                  >
                    📚 My Courses
                  </Link>
                </>
              )}
            </div>

            <div className={styles['mobile-nav-auth']}>
              {isAuthenticated ? (
                <div className={styles['mobile-user-section']}>
                  <div className={styles['mobile-user-info']}>
                    <div className={styles['mobile-user-avatar']}>
                      {user?.avatar ? (
                        <img src={user.avatar} alt={user.name} />
                      ) : (
                        <div className={styles['avatar-placeholder']}>👤</div>
                      )}
                    </div>
                    <div className={styles['mobile-user-details']}>
                      <span className={styles['mobile-user-name']}>{user?.name}</span>
                      <span className={styles['mobile-user-email']}>{user?.email}</span>
                    </div>
                  </div>
                  <Button
                    onClick={handleLogout}
                    variant="ghost"
                    fullWidth
                    className={styles['mobile-logout-button']}
                  >
                    Sign Out
                  </Button>
                </div>
              ) : (
                <div className={styles['mobile-auth-buttons']}>
                  <Button
                    onClick={() => {
                      navigate('/login');
                      closeMobileMenu();
                    }}
                    variant="ghost"
                    fullWidth
                  >
                    Sign In
                  </Button>
                  <Button
                    onClick={() => {
                      navigate('/login?mode=register');
                      closeMobileMenu();
                    }}
                    variant="primary"
                    fullWidth
                  >
                    Sign Up
                  </Button>
                </div>
              )}
            </div>
          </div>

          {/* Mobile Menu Overlay */}
          <div 
            className={styles['mobile-menu-overlay']}
            onClick={closeMobileMenu}
          />
        </div>
      )}
    </nav>
  );
};