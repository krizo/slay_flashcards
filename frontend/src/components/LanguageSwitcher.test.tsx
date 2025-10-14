import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n/i18n';
import LanguageSwitcher from './LanguageSwitcher';

describe('LanguageSwitcher', () => {
  beforeEach(async () => {
    // Reset to default language before each test
    await i18n.changeLanguage('pl');
    vi.clearAllMocks();
  });

  it('renders language switcher buttons', () => {
    render(
      <I18nextProvider i18n={i18n}>
        <LanguageSwitcher />
      </I18nextProvider>
    );

    expect(screen.getByTitle('Polski')).toBeInTheDocument();
    expect(screen.getByTitle('English')).toBeInTheDocument();
  });

  it('calls changeLanguage when PL button is clicked', async () => {
    const changeSpy = vi.spyOn(i18n, 'changeLanguage');

    render(
      <I18nextProvider i18n={i18n}>
        <LanguageSwitcher />
      </I18nextProvider>
    );

    const plButton = screen.getByTitle('Polski');
    fireEvent.click(plButton);

    expect(changeSpy).toHaveBeenCalledWith('pl');
    changeSpy.mockRestore();
  });

  it('calls changeLanguage when EN button is clicked', async () => {
    const changeSpy = vi.spyOn(i18n, 'changeLanguage');

    render(
      <I18nextProvider i18n={i18n}>
        <LanguageSwitcher />
      </I18nextProvider>
    );

    const enButton = screen.getByTitle('English');
    fireEvent.click(enButton);

    expect(changeSpy).toHaveBeenCalledWith('en');
    changeSpy.mockRestore();
  });

  it('has proper button structure', () => {
    render(
      <I18nextProvider i18n={i18n}>
        <LanguageSwitcher />
      </I18nextProvider>
    );

    const buttons = screen.getAllByRole('button');
    expect(buttons).toHaveLength(2);

    expect(buttons[0]).toHaveTextContent('English');
    expect(buttons[1]).toHaveTextContent('Polski');
  });

  it('applies active class to current language button', async () => {
    // Ensure language is 'pl'
    await i18n.changeLanguage('pl');

    render(
      <I18nextProvider i18n={i18n}>
        <LanguageSwitcher />
      </I18nextProvider>
    );

    const plButton = screen.getByTitle('Polski');
    expect(plButton.className).toContain('active');
  });

  it('does not apply active class to inactive language button', async () => {
    // Ensure language is 'pl'
    await i18n.changeLanguage('pl');

    render(
      <I18nextProvider i18n={i18n}>
        <LanguageSwitcher />
      </I18nextProvider>
    );

    const enButton = screen.getByTitle('English');
    expect(enButton.className).not.toContain('active');
  });

  it('switches active state when language changes', async () => {
    // Start with Polish
    await i18n.changeLanguage('pl');

    const { rerender } = render(
      <I18nextProvider i18n={i18n}>
        <LanguageSwitcher />
      </I18nextProvider>
    );

    let plButton = screen.getByTitle('Polski');
    let enButton = screen.getByTitle('English');

    expect(plButton.className).toContain('active');
    expect(enButton.className).not.toContain('active');

    // Change to English
    await i18n.changeLanguage('en');

    rerender(
      <I18nextProvider i18n={i18n}>
        <LanguageSwitcher />
      </I18nextProvider>
    );

    plButton = screen.getByTitle('Polski');
    enButton = screen.getByTitle('English');

    expect(plButton.className).not.toContain('active');
    expect(enButton.className).toContain('active');
  });
});
