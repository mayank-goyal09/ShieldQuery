/* ══════════════════════════════════════════════════════════════
   Document Intelligence — Frontend Logic
   ══════════════════════════════════════════════════════════════ */

// ── State ──
const state = {
    documentsLoaded: false,
    isUploading: false,
    isQuerying: false,
    totalDocs: 0,
    totalPages: 0,
    totalQueries: 0,
};


// ══════════════════════════════════════════════════════════════
// 1. INITIALIZATION
// ══════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initRevealAnimations();
    initNavbar();
    initDropzone();
    initChatInput();
    checkSystemStatus();
});


// ══════════════════════════════════════════════════════════════
// 2. PARTICLES BACKGROUND (lightweight, GPU-accelerated)
// ══════════════════════════════════════════════════════════════

function initParticles() {
    const canvas = document.getElementById('particles-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];
    let animId;
    let w, h;

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', debounce(resize, 200));

    // Create particles — keep count low for performance
    const COUNT = Math.min(50, Math.floor(window.innerWidth / 25));
    for (let i = 0; i < COUNT; i++) {
        particles.push({
            x: Math.random() * w,
            y: Math.random() * h,
            vx: (Math.random() - 0.5) * 0.3,
            vy: (Math.random() - 0.5) * 0.3,
            r: Math.random() * 1.5 + 0.5,
            a: Math.random() * 0.3 + 0.1,
        });
    }

    function draw() {
        ctx.clearRect(0, 0, w, h);

        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < 0) p.x = w;
            if (p.x > w) p.x = 0;
            if (p.y < 0) p.y = h;
            if (p.y > h) p.y = 0;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(108, 92, 231, ${p.a})`;
            ctx.fill();

            // Connect nearby particles
            for (let j = i + 1; j < particles.length; j++) {
                const q = particles[j];
                const dx = p.x - q.x;
                const dy = p.y - q.y;
                const dist = dx * dx + dy * dy;
                if (dist < 12000) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(q.x, q.y);
                    ctx.strokeStyle = `rgba(108, 92, 231, ${0.06 * (1 - dist / 12000)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
        animId = requestAnimationFrame(draw);
    }
    draw();

    // Pause when tab not visible (performance)
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            cancelAnimationFrame(animId);
        } else {
            draw();
        }
    });
}


// ══════════════════════════════════════════════════════════════
// 3. SCROLL REVEAL ANIMATIONS (IntersectionObserver)
// ══════════════════════════════════════════════════════════════

function initRevealAnimations() {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        },
        { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );

    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
}


// ══════════════════════════════════════════════════════════════
// 4. NAVBAR (scroll effects + active link tracking)
// ══════════════════════════════════════════════════════════════

function initNavbar() {
    const navbar = document.getElementById('navbar');
    const links = document.querySelectorAll('.nav-link');
    const sections = ['hero', 'upload-section', 'chat-section'];

    window.addEventListener('scroll', () => {
        // Navbar background
        navbar.classList.toggle('scrolled', window.scrollY > 40);

        // Active link
        const scrollY = window.scrollY + 200;
        for (let i = sections.length - 1; i >= 0; i--) {
            const section = document.getElementById(sections[i]);
            if (section && scrollY >= section.offsetTop) {
                links.forEach(l => l.classList.remove('active'));
                links[i]?.classList.add('active');
                break;
            }
        }
    }, { passive: true });
}


// ══════════════════════════════════════════════════════════════
// 5. DRAG & DROP UPLOAD
// ══════════════════════════════════════════════════════════════

function initDropzone() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');

    // Click to browse
    dropzone.addEventListener('click', (e) => {
        if (!state.isUploading) fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });

    // Drag events
    ['dragenter', 'dragover'].forEach(evt => {
        dropzone.addEventListener(evt, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('drag-over');
        });
    });
    ['dragleave', 'drop'].forEach(evt => {
        dropzone.addEventListener(evt, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('drag-over');
        });
    });

    dropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer?.files;
        if (files && files.length) handleFile(files[0]);
    });
}

async function handleFile(file) {
    if (state.isUploading) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showNotification('Only PDF files are supported. Please upload a .pdf document.', 'warning');
        return;
    }

    if (file.size > 50 * 1024 * 1024) {
        showNotification('File too large. Please upload a PDF under 50MB.', 'warning');
        return;
    }

    state.isUploading = true;

    // Show progress UI
    const content = document.getElementById('dropzone-content');
    const progress = document.getElementById('upload-progress');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    content.style.display = 'none';
    progress.style.display = 'block';
    progressText.textContent = `Analyzing "${file.name}"...`;
    progressBar.style.width = '0%';

    // Simulate progress while waiting for server
    let fakeProgress = 0;
    const progressInterval = setInterval(() => {
        fakeProgress = Math.min(fakeProgress + Math.random() * 8, 90);
        progressBar.style.width = fakeProgress + '%';
    }, 300);

    try {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch('/api/upload', {
            method: 'POST',
            body: formData,
        });
        const data = await res.json();

        clearInterval(progressInterval);
        progressBar.style.width = '100%';

        if (data.success) {
            state.documentsLoaded = true;
            state.totalDocs++;
            state.totalPages += data.page_count || 0;
            updateStats();
            updateSystemStatus(true);

            // Show insights
            setTimeout(() => showInsights(data), 400);
            showNotification(data.message, 'success');
        } else {
            showNotification(data.message, 'warning');
        }
    } catch (err) {
        clearInterval(progressInterval);
        showNotification('Failed to upload. Please check your connection and try again.', 'error');
        console.error('Upload error:', err);
    } finally {
        // Reset UI
        setTimeout(() => {
            const content = document.getElementById('dropzone-content');
            const progress = document.getElementById('upload-progress');
            content.style.display = 'block';
            progress.style.display = 'none';
            state.isUploading = false;
        }, 600);
    }
}


// ══════════════════════════════════════════════════════════════
// 6. INSIGHTS PANEL
// ══════════════════════════════════════════════════════════════

function showInsights(data) {
    const panel = document.getElementById('insights-panel');
    const meta = document.getElementById('insights-meta');
    const grid = document.getElementById('insights-grid');

    meta.innerHTML = `
        <span>📄 ${data.page_count} pages</span>
        <span>🧩 ${data.chunk_count} chunks</span>
    `;

    const icons = ['📋', '📑', '📅', '💼', '👥', '⚖️', '🎓', '🔒'];
    grid.innerHTML = '';
    if (data.insights && data.insights.length) {
        data.insights.forEach((insight, i) => {
            const chip = document.createElement('div');
            chip.className = 'insight-chip';
            chip.innerHTML = `<span>${icons[i % icons.length]}</span><span>${escapeHtml(insight)}</span>`;
            grid.appendChild(chip);
        });
    } else {
        grid.innerHTML = '<div class="insight-chip"><span>✅</span><span>Document processed — ask me anything!</span></div>';
    }

    panel.style.display = 'block';
}


// ══════════════════════════════════════════════════════════════
// 7. CHAT INTERFACE
// ══════════════════════════════════════════════════════════════

function initChatInput() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const charCount = document.getElementById('char-count');

    // Auto-resize textarea
    input.addEventListener('input', () => {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
        sendBtn.disabled = !input.value.trim();
        charCount.textContent = `${input.value.length} / 2000`;
    });

    // Send on Enter (Shift+Enter for new line)
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (input.value.trim()) sendMessage();
        }
    });
}

function askSuggestion(btn) {
    const input = document.getElementById('chat-input');
    input.value = btn.textContent;
    input.dispatchEvent(new Event('input'));
    sendMessage();
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const query = input.value.trim();
    if (!query || state.isQuerying) return;

    state.isQuerying = true;

    // Hide welcome
    const welcome = document.getElementById('chat-welcome');
    if (welcome) welcome.style.display = 'none';

    // Add user message
    appendMessage('user', query);

    // Clear input
    input.value = '';
    input.style.height = 'auto';
    document.getElementById('send-btn').disabled = true;
    document.getElementById('char-count').textContent = '0 / 2000';

    // Show typing indicator
    const typingId = showTypingIndicator();

    try {
        const formData = new FormData();
        formData.append('query', query);

        const res = await fetch('/api/query', {
            method: 'POST',
            body: formData,
        });
        const data = await res.json();

        removeTypingIndicator(typingId);

        appendMessage('ai', data.result, data.source, data.response_time_ms);

        state.totalQueries++;
        updateStats();

        // Show response time
        if (data.response_time_ms) {
            document.getElementById('response-time').textContent =
                `⚡ Last response: ${data.response_time_ms}ms`;
        }
    } catch (err) {
        removeTypingIndicator(typingId);
        appendMessage('ai', "I'm sorry, I couldn't process your request. Please check your connection and try again.");
        console.error('Query error:', err);
    } finally {
        state.isQuerying = false;
    }
}

function appendMessage(role, content, source = '', timeMs = null) {
    const container = document.getElementById('chat-messages');

    const msgDiv = document.createElement('div');
    msgDiv.className = `msg ${role === 'user' ? 'user-msg' : 'ai-msg'}`;

    const avatar = role === 'user' ? '👤' : '🤖';
    const avatarClass = role === 'user' ? 'user-avatar' : 'ai-avatar';
    const roleText = role === 'user' ? 'You' : 'Document Analyst';
    const roleClass = role === 'user' ? 'user-role' : 'ai-role';

    let timeHtml = '';
    if (timeMs) {
        timeHtml = `<span class="msg-time">⚡ ${timeMs}ms</span>`;
    }

    let sourceHtml = '';
    if (source) {
        sourceHtml = `<div class="msg-source">📎 Source: ${escapeHtml(source)}</div>`;
    }

    msgDiv.innerHTML = `
        <div class="msg-header">
            <div class="msg-avatar ${avatarClass}">${avatar}</div>
            <span class="msg-role ${roleClass}">${roleText}</span>
            ${timeHtml}
        </div>
        <div class="msg-body">${formatContent(content)}</div>
        ${sourceHtml}
    `;

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function formatContent(text) {
    // Basic markdown-like formatting
    let html = escapeHtml(text);
    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Line breaks
    html = html.replace(/\n/g, '<br>');
    return html;
}

function showTypingIndicator() {
    const container = document.getElementById('chat-messages');
    const id = 'typing-' + Date.now();

    const div = document.createElement('div');
    div.className = 'msg ai-msg';
    div.id = id;
    div.innerHTML = `
        <div class="msg-header">
            <div class="msg-avatar ai-avatar">🤖</div>
            <span class="msg-role ai-role">Document Analyst</span>
        </div>
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    `;

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}


// ══════════════════════════════════════════════════════════════
// 8. SYSTEM STATUS
// ══════════════════════════════════════════════════════════════

async function checkSystemStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        updateSystemStatus(data.documents_loaded);
        if (data.documents_loaded) {
            state.documentsLoaded = true;
        }
    } catch {
        updateSystemStatus(false);
    }
}

function updateSystemStatus(ready) {
    const dot = document.getElementById('status-dot');
    const text = document.getElementById('status-text');

    if (ready) {
        dot.classList.add('ready');
        text.textContent = 'Ready';
        text.style.color = 'var(--success)';
    } else {
        dot.classList.remove('ready');
        text.textContent = 'Awaiting Document';
        text.style.color = 'var(--warning)';
    }
}

function updateStats() {
    animateNumber('stat-docs', state.totalDocs);
    animateNumber('stat-pages', state.totalPages);
    animateNumber('stat-queries', state.totalQueries);
}

function animateNumber(elId, target) {
    const el = document.getElementById(elId);
    if (!el) return;
    const current = parseInt(el.textContent) || 0;
    if (current === target) return;

    const duration = 500;
    const start = performance.now();

    function tick(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        el.textContent = Math.round(current + (target - current) * eased);
        if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
}


// ══════════════════════════════════════════════════════════════
// 9. NOTIFICATIONS
// ══════════════════════════════════════════════════════════════

function showNotification(message, type = 'info') {
    // Remove existing
    document.querySelectorAll('.notification').forEach(n => n.remove());

    const colors = {
        success: { bg: 'rgba(0,206,201,0.12)', border: 'rgba(0,206,201,0.3)', text: '#00cec9', icon: '✅' },
        warning: { bg: 'rgba(253,203,110,0.12)', border: 'rgba(253,203,110,0.3)', text: '#fdcb6e', icon: '⚠️' },
        error: { bg: 'rgba(255,107,107,0.12)', border: 'rgba(255,107,107,0.3)', text: '#ff6b6b', icon: '❌' },
        info: { bg: 'rgba(108,92,231,0.12)', border: 'rgba(108,92,231,0.3)', text: '#a29bfe', icon: 'ℹ️' },
    };
    const c = colors[type] || colors.info;

    const div = document.createElement('div');
    div.className = 'notification';
    div.innerHTML = `${c.icon} ${escapeHtml(message)}`;
    Object.assign(div.style, {
        position: 'fixed',
        top: '80px',
        right: '24px',
        zIndex: '9999',
        padding: '14px 24px',
        borderRadius: '12px',
        background: c.bg,
        border: `1px solid ${c.border}`,
        color: c.text,
        fontSize: '0.88rem',
        fontWeight: '500',
        fontFamily: "'Inter', sans-serif",
        backdropFilter: 'blur(12px)',
        maxWidth: '400px',
        animation: 'notif-in 0.4s cubic-bezier(0.4,0,0.2,1)',
        boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
    });

    document.body.appendChild(div);

    // Auto-remove
    setTimeout(() => {
        div.style.animation = 'notif-out 0.3s ease forwards';
        setTimeout(() => div.remove(), 300);
    }, 4000);
}

// Add notification animations to head
(function addNotifStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes notif-in {
            from { opacity: 0; transform: translateX(40px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @keyframes notif-out {
            from { opacity: 1; transform: translateX(0); }
            to { opacity: 0; transform: translateX(40px); }
        }
    `;
    document.head.appendChild(style);
})();


// ══════════════════════════════════════════════════════════════
// 10. UTILITIES
// ══════════════════════════════════════════════════════════════

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function debounce(fn, ms) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), ms);
    };
}

// Smooth scroll for nav links
document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(link.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});
