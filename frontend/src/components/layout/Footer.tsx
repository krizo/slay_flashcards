import { useTranslation } from 'react-i18next';

function Footer() {
    const { t } = useTranslation();
    const buildVersion = import.meta.env.VITE_BUILD_VERSION;
    const buildDate = import.meta.env.VITE_BUILD_DATE;
    const isCI = import.meta.env.VITE_IS_CI === 'true';
    const environment = import.meta.env.VITE_ENVIRONMENT || 'staging';

    const getEnvironmentEmoji = () => {
        if (environment === 'production') return '🚀';
        if (environment === 'staging') return '🧪';
        return '🔧';
    };

    const getEnvironmentLabel = () => {
        if (environment === 'production') return t('auth.productionEnvironment');
        if (environment === 'staging') return t('auth.stagingEnvironment');
        return t('auth.localEnvironment');
    };

    return (
        <footer className="sidebar-footer">
            <div className="version-info">
                {isCI && buildVersion && buildDate ? (
                    <div className="version-label">
                        {getEnvironmentEmoji()} {getEnvironmentLabel()} : v{buildVersion} : {buildDate}
                    </div>
                ) : (
                    <div className="version-label">
                        🔧 {t('auth.localEnvironment')}
                    </div>
                )}
            </div>
        </footer>
    );
}

export default Footer;
