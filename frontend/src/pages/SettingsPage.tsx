const SettingsPage = () => {
    return (
        <div className="page-container">
            <div className="page-header">
                <h1 className="page-title">Application Settings</h1>
                <p className="page-description">
                    Customize your SlayFlashcards experience. Configure preferences, manage your account,
                    and adjust learning parameters.
                </p>
            </div>

            <div className="page-content">
                <div className="placeholder-content">
                    <p>⚙️ Settings panel coming soon...</p>
                    <ul>
                        <li>Language preferences</li>
                        <li>Theme customization</li>
                        <li>Notification settings</li>
                        <li>Audio controls</li>
                        <li>Data export/import</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default SettingsPage;
