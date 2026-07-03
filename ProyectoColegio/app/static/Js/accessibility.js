/**
 * Accessibility Module for Proyecto Colegio
 * Features: High Contrast, Font Size adjustment, Readable Font toggle
 */

document.addEventListener('DOMContentLoaded', () => {
    const accessBtn = document.getElementById('btnAccessibility');
    const accessPanel = document.getElementById('accessibilityPanel');
    const body = document.body;

    // Load saved preferences
    const contrast = localStorage.getItem('accessibility-contrast');
    const fontSize = localStorage.getItem('accessibility-font-size');
    const readableFont = localStorage.getItem('accessibility-readable-font');

    if (contrast === 'enabled') body.classList.add('is-high-contrast');
    if (fontSize) body.classList.add(`is-size-${fontSize}`);
    if (readableFont === 'enabled') body.classList.add('is-readable-font');

    // Toggle Panel
    if (accessBtn) {
        accessBtn.addEventListener('click', () => {
            accessPanel.classList.toggle('show');
        });
    }

    // High Contrast
    const btnContrast = document.getElementById('btnContrast');
    if (btnContrast) {
        btnContrast.addEventListener('click', () => {
            body.classList.toggle('is-high-contrast');
            const status = body.classList.contains('is-high-contrast') ? 'enabled' : 'disabled';
            localStorage.setItem('accessibility-contrast', status);
        });
    }

    // Font Size
    const btnIncreaseFont = document.getElementById('btnIncreaseFont');
    const btnDecreaseFont = document.getElementById('btnDecreaseFont');
    const btnResetFont = document.getElementById('btnResetFont');

    const updateFontSize = (size) => {
        body.classList.remove('is-size-small', 'is-size-medium', 'is-size-large');
        if (size !== 'medium') body.classList.add(`is-size-${size}`);
        localStorage.setItem('accessibility-font-size', size);
    };

    if (btnIncreaseFont) {
        btnIncreaseFont.addEventListener('click', () => {
            let current = localStorage.getItem('accessibility-font-size') || 'medium';
            if (current === 'small') updateFontSize('medium');
            else if (current === 'medium') updateFontSize('large');
        });
    }

    if (btnDecreaseFont) {
        btnDecreaseFont.addEventListener('click', () => {
            let current = localStorage.getItem('accessibility-font-size') || 'medium';
            if (current === 'large') updateFontSize('medium');
            else if (current === 'medium') updateFontSize('small');
        });
    }

    if (btnResetFont) {
        btnResetFont.addEventListener('click', () => updateFontSize('medium'));
    }

    // Readable Font
    const btnReadableFont = document.getElementById('btnReadableFont');
    if (btnReadableFont) {
        btnReadableFont.addEventListener('click', () => {
            body.classList.toggle('is-readable-font');
            const status = body.classList.contains('is-readable-font') ? 'enabled' : 'disabled';
            localStorage.setItem('accessibility-readable-font', status);
        });
    }

    // Voice Assistant
    const btnVoiceAssistant = document.getElementById('btnVoiceAssistant');
    let isVoiceActive = localStorage.getItem('accessibility-voice') === 'enabled';
    let currentUtterance = null;

    const speak = (text) => {
        if (!isVoiceActive) return;
        window.speechSynthesis.cancel();
        currentUtterance = new SpeechSynthesisUtterance(text);
        currentUtterance.lang = 'es-ES'; // Set to Spanish
        window.speechSynthesis.speak(currentUtterance);
    };

    const updateVoiceAssistantLink = () => {
        if (isVoiceActive) btnVoiceAssistant.classList.add('active');
        else btnVoiceAssistant.classList.remove('active');
    };

    if (btnVoiceAssistant) {
        updateVoiceAssistantLink();
        btnVoiceAssistant.addEventListener('click', () => {
            isVoiceActive = !isVoiceActive;
            localStorage.setItem('accessibility-voice', isVoiceActive ? 'enabled' : 'disabled');
            updateVoiceAssistantLink();
            if (isVoiceActive) speak("Asistente de voz activado");
            else window.speechSynthesis.cancel();
        });
    }

    // Read elements on hover
    document.addEventListener('mouseover', (e) => {
        if (!isVoiceActive) return;
        
        const target = e.target;
        // Only read relevant text-containing elements
        if (['P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'A', 'BUTTON', 'LABEL', 'LI', 'SPAN'].includes(target.tagName)) {
            const text = target.innerText || target.getAttribute('aria-label') || target.title;
            if (text && text.trim().length > 0) {
                target.classList.add('is-being-read');
                speak(text);
                
                target.addEventListener('mouseleave', () => {
                    target.classList.remove('is-being-read');
                }, { once: true });
            }
        }
    });

    // Close panel when clicking outside
    document.addEventListener('click', (e) => {
        if (accessPanel && accessBtn && !accessPanel.contains(e.target) && !accessBtn.contains(e.target)) {
            accessPanel.classList.remove('show');
        }
    });
});
