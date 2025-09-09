// Global theme functionality
function setTheme(isDark) {
    const root = document.documentElement;
    if (isDark) {
        root.style.setProperty('--bg-primary', '#0a0a0a');
        root.style.setProperty('--bg-secondary', '#1a1a1a');
        root.style.setProperty('--bg-glass', 'rgba(255, 255, 255, 0.05)');
        root.style.setProperty('--bg-glass-hover', 'rgba(255, 255, 255, 0.1)');
        root.style.setProperty('--text-primary', '#ffffff');
        root.style.setProperty('--text-secondary', '#a0a0a0');
        root.style.setProperty('--accent', '#6366f1');
        root.style.setProperty('--accent-hover', '#4f46e5');
        root.style.setProperty('--border', 'rgba(255, 255, 255, 0.1)');
        root.style.setProperty('--shadow', '0 8px 32px rgba(0, 0, 0, 0.3)');
        root.style.setProperty('--shadow-hover', '0 12px 40px rgba(0, 0, 0, 0.4)');
        document.body.style.background = 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0f0f23 100%)';
        localStorage.setItem('theme', 'dark');
    } else {
        root.style.setProperty('--bg-primary', '#ffffff');
        root.style.setProperty('--bg-secondary', '#f8fafc');
        root.style.setProperty('--bg-glass', 'rgba(255, 255, 255, 0.8)');
        root.style.setProperty('--bg-glass-hover', 'rgba(255, 255, 255, 0.9)');
        root.style.setProperty('--text-primary', '#1a1a1a');
        root.style.setProperty('--text-secondary', '#6b7280');
        root.style.setProperty('--accent', '#6366f1');
        root.style.setProperty('--accent-hover', '#4f46e5');
        root.style.setProperty('--border', 'rgba(0, 0, 0, 0.1)');
        root.style.setProperty('--shadow', '0 8px 32px rgba(0, 0, 0, 0.1)');
        root.style.setProperty('--shadow-hover', '0 12px 40px rgba(0, 0, 0, 0.15)');
        document.body.style.background = 'linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%)';
        localStorage.setItem('theme', 'light');
    }
}

// Toggle theme function
function toggleTheme() {
    const currentTheme = localStorage.getItem('theme');
    const isDark = currentTheme !== 'light';
    setTheme(!isDark);
    updateThemeToggleText(!isDark);
}

// Update theme toggle text
function updateThemeToggleText(isDark) {
    const text = isDark ? '浅色' : '深色'; // Default to Chinese, will be overridden by template
    
    // Update all theme toggle text elements
    const themeTextElements = [
        'themeToggleText',      // index.html avatar menu
        'guestThemeText',       // index.html guest settings
        'loginThemeText',       // login.html
        'aboutThemeText',       // about.html
        'joinThemeText',        // join.html
        'downloadsThemeText',   // downloads.html
        'gamesThemeText',       // games.html
        'newDownloadThemeText', // new_download.html
        'newPostThemeText'      // new_post.html
    ];
    
    themeTextElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.textContent = text;
    });
}

// Initialize theme
(function() {
    const savedTheme = localStorage.getItem('theme');
    const isDark = savedTheme !== 'light';
    setTheme(isDark);
    updateThemeToggleText(isDark);
})();
