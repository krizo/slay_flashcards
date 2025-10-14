import { useTranslation } from 'react-i18next';

const languages = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'pl', name: 'Polski', flag: '🇵🇱' }
];

interface LanguageSwitcherProps {
    onChange?: (languageCode: string) => void | Promise<void>;
}

function LanguageSwitcher({ onChange }: LanguageSwitcherProps) {
    const { i18n } = useTranslation();

    const changeLanguage = async (languageCode: string) => {
        await i18n.changeLanguage(languageCode);
        if (onChange) {
            await onChange(languageCode);
        }
    };

    return (
        <div className="language-switcher">
            {languages.map(({ code, name, flag }) => (
                <button
                    key={code}
                    onClick={() => changeLanguage(code)}
                    className={`language-button ${i18n.language === code ? 'active' : ''}`}
                    title={name}
                >
                    {flag} {name}
                </button>
            ))}
        </div>
    );
}

export default LanguageSwitcher;
