function Footer() {
    const buildVersion = import.meta.env.VITE_BUILD_VERSION || 'dev';
    const buildDate = import.meta.env.VITE_BUILD_DATE || 'local build';
    const isCI = import.meta.env.VITE_IS_CI === 'true';

    return (
        <footer className="sidebar-footer">
            <div className="version-info">
                <div className="version-label">
                    {isCI ? `v${buildVersion}` : '🔧 Local'}
                </div>
                <div className="build-date">{buildDate}</div>
            </div>
        </footer>
    );
}

export default Footer;
