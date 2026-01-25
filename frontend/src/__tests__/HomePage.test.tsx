import { render } from '@testing-library/react';
import { describe, it, expect } from '@jest/globals';
import HomePage from '../../app/page';

describe('HomePage', () => {
  it('renders without crashing', () => {
    const { getByText } = render(<HomePage />);
    expect(getByText('Simplify Your Tasks, Amplify Your Productivity')).toBeInTheDocument();
  });
});