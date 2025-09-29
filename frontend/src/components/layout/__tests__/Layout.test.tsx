import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Layout } from '../Layout';
import '@testing-library/jest-dom';

// Mock the Navigation component
jest.mock('../../common/Navigation', () => ({
  Navigation: () => <div data-testid="navigation">Navigation</div>
}));

// Mock the useAuth hook
jest.mock('../../../hooks/useAuth', () => ({
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
    login: jest.fn(),
    logout: jest.fn(),
    register: jest.fn(),
    refreshToken: jest.fn(),
    clearError: jest.fn(),
    updateProfile: jest.fn(),
    isLoading: false,
    error: null,
    token: null
  })
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Layout', () => {
  it('renders children content', () => {
    renderWithRouter(
      <Layout>
        <div data-testid="test-content">Test Content</div>
      </Layout>
    );
    
    expect(screen.getByTestId('test-content')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('renders navigation by default', () => {
    renderWithRouter(
      <Layout>
        <div>Content</div>
      </Layout>
    );
    
    expect(screen.getByTestId('navigation')).toBeInTheDocument();
  });

  it('hides navigation when showNavigation is false', () => {
    renderWithRouter(
      <Layout showNavigation={false}>
        <div>Content</div>
      </Layout>
    );
    
    expect(screen.queryByTestId('navigation')).not.toBeInTheDocument();
  });

  it('renders footer by default', () => {
    renderWithRouter(
      <Layout>
        <div>Content</div>
      </Layout>
    );
    
    expect(screen.getByRole('contentinfo')).toBeInTheDocument();
    expect(screen.getByText('Learnify')).toBeInTheDocument();
    expect(screen.getByText(/Transform your documents into interactive learning experiences/)).toBeInTheDocument();
  });

  it('hides footer when showFooter is false', () => {
    renderWithRouter(
      <Layout showFooter={false}>
        <div>Content</div>
      </Layout>
    );
    
    expect(screen.queryByRole('contentinfo')).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = renderWithRouter(
      <Layout className="custom-layout">
        <div>Content</div>
      </Layout>
    );
    
    expect(container.firstChild).toHaveClass('layout', 'custom-layout');
  });

  it('renders all footer sections', () => {
    renderWithRouter(
      <Layout>
        <div>Content</div>
      </Layout>
    );
    
    // Check footer sections
    expect(screen.getByText('Product')).toBeInTheDocument();
    expect(screen.getByText('Support')).toBeInTheDocument();
    expect(screen.getByText('Legal')).toBeInTheDocument();
    expect(screen.getByText('Connect')).toBeInTheDocument();
  });

  it('renders footer links correctly', () => {
    renderWithRouter(
      <Layout>
        <div>Content</div>
      </Layout>
    );
    
    // Check some key footer links
    expect(screen.getByRole('link', { name: 'Home' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Privacy Policy' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Terms of Service' })).toBeInTheDocument();
  });

  it('renders current year in copyright', () => {
    const currentYear = new Date().getFullYear();
    
    renderWithRouter(
      <Layout>
        <div>Content</div>
      </Layout>
    );
    
    expect(screen.getByText(new RegExp(`© ${currentYear} Learnify`))).toBeInTheDocument();
  });

  it('renders external links with proper attributes', () => {
    renderWithRouter(
      <Layout>
        <div>Content</div>
      </Layout>
    );
    
    const twitterLink = screen.getByRole('link', { name: 'Twitter' });
    expect(twitterLink).toHaveAttribute('target', '_blank');
    expect(twitterLink).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('renders status indicator', () => {
    renderWithRouter(
      <Layout>
        <div>Content</div>
      </Layout>
    );
    
    expect(screen.getByText('All systems operational')).toBeInTheDocument();
    expect(screen.getByText('v1.0.0')).toBeInTheDocument();
  });
});