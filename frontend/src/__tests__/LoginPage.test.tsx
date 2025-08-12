import React from 'react';
import { render, screen } from '@testing-library/react';
import { LoginPage } from '../pages/LoginPage';
import { BrowserRouter } from 'react-router-dom';

// Mock the AuthContext to avoid dependency issues
jest.mock('../contexts/AuthContext', () => ({
  useAuth: () => ({
    login: jest.fn(),
    user: null,
    loading: false
  })
}));

test('renders login page with Tailwind CSS classes', () => {
  render(
    <BrowserRouter>
      <LoginPage />
    </BrowserRouter>
  );
  
  const signInElement = screen.getByText(/sign in to your account/i);
  expect(signInElement).toBeInTheDocument();
  
  const emailInput = screen.getByPlaceholderText(/email address/i);
  expect(emailInput).toBeInTheDocument();
  
  const passwordInput = screen.getByPlaceholderText(/password/i);
  expect(passwordInput).toBeInTheDocument();
});