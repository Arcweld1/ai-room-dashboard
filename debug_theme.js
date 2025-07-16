// Debug theme switching
console.log('=== Theme Debug ===');

// Check if elements exist
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = document.querySelector('.theme-icon');
const themeText = document.querySelector('.theme-text');

console.log('themeToggle exists:', !!themeToggle);
console.log('themeIcon exists:', !!themeIcon);
console.log('themeText exists:', !!themeText);

// Check current theme
const currentTheme = document.documentElement.getAttribute('data-theme');
console.log('Current theme:', currentTheme);

// Manually switch to dark theme
document.documentElement.setAttribute('data-theme', 'dark');
console.log('Switched to dark theme');

// Check if the theme was applied
const newTheme = document.documentElement.getAttribute('data-theme');
console.log('New theme:', newTheme);

// Update button text
if (themeIcon && themeText) {
    themeIcon.textContent = '☀️';
    themeText.textContent = 'Light';
    console.log('Button text updated');
}

console.log('=== End Debug ===');
