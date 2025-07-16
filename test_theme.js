// Test the theme switching functionality
function testThemeSwitch() {
    console.log('Testing theme switch...');
    
    // Get current theme
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    console.log('Current theme:', currentTheme);
    
    // Switch to dark
    document.documentElement.setAttribute('data-theme', 'dark');
    console.log('Switched to dark theme');
    
    // Update button text
    const themeIcon = document.querySelector('.theme-icon');
    const themeText = document.querySelector('.theme-text');
    
    if (themeIcon && themeText) {
        themeIcon.textContent = '☀️';
        themeText.textContent = 'Light';
        console.log('Updated button text');
    }
    
    return 'Theme switch test completed';
}

testThemeSwitch();
