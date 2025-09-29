import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Button } from '../ui/Button';
import { useAuth } from '../../hooks/useAuth';

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
    <nav className="navigation">
      <div className="nav-container">
        {/* Logo and Brand */}
        <div className="nav-brand">
          <Link to="/" className="brand-link" onClick={closeMobileMenu}>
            <div className="brand-logo">🤓</div>
            <span className="brand-name">Learnify</span>
          </Link>
        </div>

        {/* Desktop Navigation */}
        <div className="nav-links desktop-nav">
          <Link 
            to="/" 
            className={`nav-link ${isActiveRoute('/') ? 'active' : ''}`}
          >
            Home
          </Link>
          
          {isAuthenticated && (
            <>
              <Link 
                to="/dashboard" 
                className={`nav-link ${isActiveRoute('/dashboard') ? 'active' : ''}`}
              >
                Dashboard
              </Link>
              <Link 
                to="/courses" 
                className={`nav-link ${isActiveRoute('/courses') ? 'active' : ''}`}
              >
                My Courses
              </Link>
            </>
          )}
        </div>

        {/* Desktop Auth Section */}
        <div className="nav-auth desktop-nav">
          {isAuthenticated ? (
            <div className="user-menu">
              <div className="user-info">
                <span className="user-name">Hi, {user?.name}</span>
                {user?.avatar && (
                  <img 
                    src={user.avatar} 
                    alt={user.name} 
                    className="user-avatar"
                  />
                )}
              </div>
              <Button
                onClick={handleLogout}
                variant="ghost"
                size="sm"
                className="logout-button"
              >
                Sign Out
              </Button>
            </div>
          ) : (
            <div className="auth-buttons">
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
          className="mobile-menu-toggle"
          onClick={toggleMobileMenu}
          aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
        >
          <span className="hamburger-line"></span>
          <span className="hamburger-line"></span>
          <span className="hamburger-line"></span>
        </button>
      </div>

      {/* Mobile Navigation Menu */}
      {isMobileMenuOpen && (
        <div className="mobile-nav">
          <div className="mobile-nav-content">
            <div className="mobile-nav-links">
              <Link 
                to="/" 
                className={`mobile-nav-link ${isActiveRoute('/') ? 'active' : ''}`}
                onClick={closeMobileMenu}
              >
                🏠 Home
              </Link>
              
              {isAuthenticated && (
                <>
                  <Link 
                    to="/dashboard" 
                    className={`mobile-nav-link ${isActiveRoute('/dashboard') ? 'active' : ''}`}
                    onClick={closeMobileMenu}
                  >
                    📈 Dashboard
                  </Link>
                  <Link 
                    to="/courses" 
                    className={`mobile-nav-link ${isActiveRoute('/courses') ? 'active' : ''}`}
                    onClick={closeMobileMenu}
                  >
                    📚 My Courses
                  </Link>
                </>
              )}
            </div>

            <div className="mobile-nav-auth">
              {isAuthenticated ? (
                <div className="mobile-user-section">
                  <div className="mobile-user-info">
                    <div className="mobile-user-avatar">
                      {user?.avatar ? (
                        <img src={user.avatar} alt={user.name} />
                      ) : (
                        <div className="avatar-placeholder">👤</div>
                      )}
                    </div>
                    <div className="mobile-user-details">
                      <span className="mobile-user-name">{user?.name}</span>
                      <span className="mobile-user-email">{user?.email}</span>
                    </div>
                  </div>
                  <Button
                    onClick={handleLogout}
                    variant="ghost"
                    fullWidth
                    className="mobile-logout-button"
                  >
                    Sign Out
                  </Button>
                </div>
              ) : (
                <div className="mobile-auth-buttons">
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
            className="mobile-menu-overlay"
            onClick={closeMobileMenu}
          />
        </div>
      )}
    </nav>
  );
};