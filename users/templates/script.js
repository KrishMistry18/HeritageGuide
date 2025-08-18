// Get the theme toggle button
const themeToggle = document.querySelector('.theme-toggle');
const body = document.body;

// Check if dark mode is already set in local storage
if (localStorage.getItem('theme') === 'dark') {
    body.classList.add('dark-mode');
    themeToggle.innerHTML = '<i class="fas fa-sun"></i>'; // Change icon to Sun
}

// Add event listener to toggle theme
themeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');

    // Change the button icon
    if (body.classList.contains('dark-mode')) {
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>'; // Sun icon for light mode
        localStorage.setItem('theme', 'dark');
    } else {
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>'; // Moon icon for dark mode
        localStorage.setItem('theme', 'light');
    }
});
