function Footer() {
    const buildVersion = import.meta.env.VITE_BUILD_VERSION || 'dev';
    const buildDate = import.meta.env.VITE_BUILD_DATE || 'unknown';

    return (
        <footer className="sidebar-footer">
            <div className="version-info">
                <div className="version-label">v{buildVersion}</div>
                <div className="build-date">{buildDate}</div>
            </div>
        </footer>
    );
}

export default Footer;
