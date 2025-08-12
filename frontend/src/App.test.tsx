import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders sign in form', () => {
  render(<App />);
  const signInElement = screen.getByText(/sign in to your account/i);
  expect(signInElement).toBeInTheDocument();
});
