// ═══════════════════════════════════════════════════════
// NovaBuy — Main JavaScript
// ═══════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    // ─── Mobile Menu Toggle ────────────────────────────
    const toggle = document.getElementById('mobile-toggle');
    const navLinks = document.getElementById('nav-links');

    if (toggle && navLinks) {
        toggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            const icon = toggle.querySelector('i');
            icon.classList.toggle('fa-bars');
            icon.classList.toggle('fa-times');
        });

        // Close menu when clicking a link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                const icon = toggle.querySelector('i');
                icon.classList.add('fa-bars');
                icon.classList.remove('fa-times');
            });
        });
    }

    // ─── Navbar scroll effect ──────────────────────────
    const navbar = document.getElementById('navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.scrollY;

        if (currentScroll > 50) {
            navbar.style.background = 'rgba(10, 10, 15, 0.95)';
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
        } else {
            navbar.style.background = 'rgba(10, 10, 15, 0.85)';
            navbar.style.boxShadow = 'none';
        }

        lastScroll = currentScroll;
    });

    // ─── Auto-dismiss flash messages ───────────────────
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach((flash, index) => {
        setTimeout(() => {
            flash.style.transition = 'all 0.4s ease';
            flash.style.opacity = '0';
            flash.style.transform = 'translateX(100%)';
            setTimeout(() => flash.remove(), 400);
        }, 4000 + index * 500);
    });

    // ─── Smooth scroll for anchor links ────────────────
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ─── Animate elements on scroll ────────────────────
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Animate product cards, category cards, and feature cards
    const animateElements = document.querySelectorAll(
        '.product-card, .category-card, .feature-card'
    );

    animateElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = `all 0.5s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.07}s`;
        observer.observe(el);
    });

    // ─── Back to Top Button ────────────────────────────
    const backToTop = document.getElementById('back-to-top');
    if (backToTop) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 400) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        });
        backToTop.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // ─── Lazy Image Loading ────────────────────────────
    const images = document.querySelectorAll('.product-image img, .product-detail-image img');
    if ('IntersectionObserver' in window) {
        const imgObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.style.opacity = '1';
                    imgObserver.unobserve(img);
                }
            });
        }, { threshold: 0.1 });
        images.forEach(img => {
            img.style.opacity = '0';
            img.style.transition = 'opacity 0.5s ease';
            imgObserver.observe(img);
        });
    }
});
