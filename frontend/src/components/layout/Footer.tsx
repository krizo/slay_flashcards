function Footer() {
    const buildVersion = import.meta.env.VITE_BUILD_VERSION;
    const buildDate = import.meta.env.VITE_BUILD_DATE;
    const isCI = import.meta.env.VITE_IS_CI === 'true';
    const environment = import.meta.env.VITE_ENVIRONMENT || 'staging';

    const getEnvironmentEmoji = () => {
        if (environment === 'production') return '🚀';
        if (environment === 'staging') return '🧪';
        return '🔧';
    };

    return (
        <footer className="sidebar-footer">
            <div className="version-info">
                {isCI && buildVersion && buildDate ? (
                    <div className="version-label">
                        {getEnvironmentEmoji()} {environment} : v{buildVersion} : {buildDate}
                    </div>
                ) : (
                    <div className="version-label">
                        🔧 Local
                    </div>
                )}
            </div>
        </footer>
    );
}

export default Footer;
