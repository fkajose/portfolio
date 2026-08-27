/*!
 * Farook Ajose — Portfolio
 * Mobile nav auto-collapse on link click
 */
window.addEventListener('DOMContentLoaded', () => {
  const navbarCollapse = document.getElementById('navbarResponsive');
  if (!navbarCollapse) return;

  const navLinks = navbarCollapse.querySelectorAll('.nav-link');
  navLinks.forEach((link) => {
    link.addEventListener('click', () => {
      if (navbarCollapse.classList.contains('show')) {
        const bsCollapse = bootstrap.Collapse.getOrCreateInstance(navbarCollapse);
        bsCollapse.hide();
      }
    });
  });
});