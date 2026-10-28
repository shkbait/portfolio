(() => {
  'use strict';

  const $ = (id) => document.getElementById(id);

  const homeView = $('homeView');
  const contentView = $('contentView');
  const dialog = $('adminDialog');

  const state = {
    pages: [],
    apiBase:
      localStorage.getItem('supremeApiBase') ||
      'http://127.0.0.1:8000'
  };

  const setText = (id, value) => {
    const element = $(id);
    if (element) element.textContent = value ?? '';
  };

  const setValue = (id, value) => {
    const element = $(id);
    if (element) element.value = value ?? '';
  };

  function setStatus(message, error = false) {
    const element = $('adminStatus');

    if (!element) {
      console[error ? 'error' : 'log'](message);
      return;
    }

    element.textContent = message;
    element.style.color = error ? '#ef6b72' : '#888';
  }

  if (!homeView || !contentView) {
    console.error('Missing #homeView or #contentView in index.html.');
    return;
  }

  setValue('apiBase', state.apiBase);

  // Clock — Ulan-Ude
  function updateClock() {
    const clock = $('clockline');
    if (!clock) return;

    const now = new Date();

    const date = new Intl.DateTimeFormat('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      timeZone: 'Asia/Irkutsk'
    }).format(now);

    const time = new Intl.DateTimeFormat('en-GB', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
      timeZone: 'Asia/Irkutsk'
    })
      .format(now)
      .toLowerCase()
      .replace(' ', '');

    clock.textContent = `${date} ${time} UU`;
  }

  updateClock();
  setInterval(updateClock, 30000);

  // API
  function apiUrl(path) {
    return `${state.apiBase.replace(/\/$/, '')}${path}`;
  }

  async function api(path, options = {}) {
    const headers = new Headers(options.headers || {});

    if (options.body && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    const response = await fetch(apiUrl(path), {
      ...options,
      headers
    });

    const raw = await response.text();
    let data = null;

    try {
      data = raw ? JSON.parse(raw) : null;
    } catch {
      data = raw;
    }

    if (!response.ok) {
      throw new Error(
        data?.detail ||
        data?.message ||
        `HTTP ${response.status}`
      );
    }

    return data;
  }

  // Pages
  function normalizePage(page) {
    if (!page || typeof page !== 'object') return null;

    return {
      id: page.page_id ?? page.id ?? page.id_page ?? null,
      title: page.title ?? page.name ?? 'untitled page',
      text: page.main_text ?? page.content ?? page.text ?? ''
    };
  }

  async function fetchPages() {
    const data = await api('/get_current');

    const pages = Array.isArray(data)
      ? data
      : Array.isArray(data?.pages)
        ? data.pages
        : [];

    state.pages = pages.map(normalizePage).filter(Boolean);
    return state.pages;
  }

  // Photos
  async function fetchPhotos() {
    const data = await api('/get_photos');

    if (Array.isArray(data)) return data;
    if (Array.isArray(data?.photos)) return data.photos;

    return data;
  }

  // Navigation
  function showHome() {
    contentView.classList.add('hidden');
    homeView.classList.remove('hidden');

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function showContent(eyebrow, title, text = '', pages = []) {
    homeView.classList.add('hidden');
    contentView.classList.remove('hidden');

    setText('contentEyebrow', eyebrow);
    setText('contentTitle', title);
    setText('contentCopy', text);

    const list = $('pageList');

    if (!list) {
      console.error('Missing #pageList in index.html.');
      return;
    }

    list.replaceChildren();

    if (pages.length) {
      pages.forEach((page) => {
        const button = document.createElement('button');

        button.className = 'page-link';
        button.textContent = page.title;
        button.addEventListener('click', () => openPage(page));

        list.appendChild(button);
      });
    } else if (!text) {
      const empty = document.createElement('div');

      empty.className = 'empty-state';
      empty.textContent = 'nothing here yet';

      list.appendChild(empty);
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // Gallery
  async function openGallery() {
    homeView.classList.add('hidden');
    contentView.classList.remove('hidden');

    setText('contentEyebrow', 'archive');
    setText('contentTitle', 'photos');
    setText('contentCopy', '');

    const list = $('pageList');

    if (!list) {
      console.error('Missing #pageList in index.html.');
      return;
    }

    list.replaceChildren();
    list.textContent = 'Loading photos...';

    try {
      const photos = await fetchPhotos();

      list.replaceChildren();

      if (!Array.isArray(photos)) {
        list.textContent =
          'Unexpected API response: ' + JSON.stringify(photos);
        console.error('Unexpected /get_photos response:', photos);
        return;
      }

      if (photos.length === 0) {
        list.textContent = 'No photos yet.';
        return;
      }

      photos.forEach((photo) => {
        const card = document.createElement('article');
        card.className = 'photo-card';

        const img = document.createElement('img');

        const photoPath =
          photo.photo_path ?? photo.path ?? photo.url ?? '';

        if (photoPath) {
          const path = String(photoPath).replace(/^\/+/, '');

          img.src = /^https?:\/\//i.test(path)
            ? path
            : apiUrl('/' + path);
        }

        img.alt = photo.title || 'Photo';
        img.loading = 'lazy';

        img.addEventListener('error', () => {
          console.error('Could not load photo:', img.src);
          img.alt = 'Image could not be loaded';
          img.classList.add('image-error');
        });

        const title = document.createElement('p');
        title.textContent = photo.title || '';

        card.append(img, title);
        list.appendChild(card);
      });

      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
      console.error('Gallery error:', error);

      list.replaceChildren();

      const message = document.createElement('p');
      message.className = 'error-message';
      message.textContent =
        `Could not load photos: ${error.message || String(error)}. ` +
        'Check FastAPI and CORS settings.';

      list.appendChild(message);
    }
  }

  async function openPage(page) {
    try {
      let selected = page;

      if (page.id != null) {
        const data = await api(
          `/get_page?page_id=${encodeURIComponent(page.id)}`
        );

        selected = normalizePage(data) || page;
      }

      showContent('page', selected.title, selected.text);
    } catch (error) {
      showContent('error', 'could not load page', error.message);
    }
  }

  
function openContactForm() {
  showContent('contact', 'contact', '', []);

  const list = $('pageList');
  if (!list) return;

  const form = document.createElement('form');
  form.className = 'contact-form';

  const fields = [
    {
      name: 'first_name',
      label: 'first name',
      type: 'text',
      placeholder: 'Your first name'
    },
    {
      name: 'last_name',
      label: 'last name',
      type: 'text',
      placeholder: 'Your last name'
    },
    {
      name: 'your_email',
      label: 'email',
      type: 'email',
      placeholder: 'you@example.com'
    }
  ];

  fields.forEach((field) => {
    const label = document.createElement('label');
    label.className = 'contact-field';
    label.textContent = field.label;

    const input = document.createElement('input');
    input.name = field.name;
    input.type = field.type;
    input.placeholder = field.placeholder;
    input.required = true;
    input.autocomplete =
      field.name === 'your_email' ? 'email' : 'given-name';

    label.appendChild(input);
    form.appendChild(label);
  });

  const messageLabel = document.createElement('label');
  messageLabel.className = 'contact-field';
  messageLabel.textContent = 'message';

  const message = document.createElement('textarea');
  message.name = 'message';
  message.placeholder = 'Write your message...';
  message.rows = 6;
  message.required = true;
  message.maxLength = 5000;

  messageLabel.appendChild(message);
  form.appendChild(messageLabel);

  const submit = document.createElement('button');
  submit.type = 'submit';
  submit.className = 'contact-submit';
  submit.textContent = 'send message';
  form.appendChild(submit);

  const status = document.createElement('p');
  status.className = 'contact-status';
  status.setAttribute('role', 'status');
  status.setAttribute('aria-live', 'polite');
  form.appendChild(status);

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    if (!form.reportValidity()) return;

    submit.disabled = true;
    submit.textContent = 'sending...';
    status.textContent = '';
    status.className = 'contact-status';

    const params = new URLSearchParams(
      Object.fromEntries(new FormData(form).entries())
    );

    try {
      const response = await fetch(
        `${state.apiBase.replace(/\/+$/, '')}/contact?${params}`,
        { method: 'POST' }
      );

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join(', ')
          : data.detail || data.message || `HTTP ${response.status}`;

        throw new Error(detail);
      }

      status.textContent = 'Message sent successfully.';
      status.classList.add('success');
      form.reset();
    } catch (error) {
      status.textContent = `Could not send message: ${error.message}`;
      status.classList.add('error');
    } finally {
      submit.disabled = false;
      submit.textContent = 'send message';
    }
  });

  list.appendChild(form);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

  
  // Sections
  async function openSection(section) {
    if (section === 'gallery') {
      await openGallery();
      return;
    }

    if (section === 'random') {
      try {
        const pages = await fetchPages();

        if (!pages.length) {
          showContent('random', 'random', 'No pages have been added yet.');
          return;
        }

        await openPage(pages[Math.floor(Math.random() * pages.length)]);
      } catch (error) {
        showContent('error', 'connection error', error.message);
      }

      return;
    }
    if (section === 'contact'){
      openContactForm();
      return;
    }
    if (section === 'about') {
      try {
        const data = await api(`/about`);
        const page = normalizePage(data);

        if (Array.isArray(data)) {
          showContent(
            section,
            section,
            '',
            data.map(normalizePage).filter(Boolean)
          );
          return;
        }

        const text = page
          ? page.text
          : typeof data === 'string'
            ? data
            : JSON.stringify(data, null, 2);

        showContent(
          section,
          page?.title || section,
          text || (data ? JSON.stringify(data, null, 2) : '')
        );
      } catch (error) {
        showContent(
          'error',
          `${section}: unavailable`,
          `${error.message}\n\nCheck FastAPI and CORS settings.`
        );
      }

      return;
    }

    if (section === 'news') {
      try {
        const pages = await fetchPages();

        showContent(
          'news',
          'news',
          pages.length
            ? 'latest pages'
            : 'No pages have been published yet.',
          pages
        );
      } catch (error) {
        showContent('error', 'news', error.message);
      }

      return;
    }

    if (section === 'mailing') {
      showContent(
        'mailing list',
        'mailing list',
        'Mailing list signup is not connected to the current API yet.'
      );
      return;
    }

    if (section === 'stores') {
      showContent(
        'stores',
        'stores',
        'This section is a visual placeholder.'
      );
      return;
    }

    if (section === 'preview' || section === 'lookbook') {
      try {
        const pages = await fetchPages();

        const pattern = section === 'preview'
          ? /preview/i
          : /lookbook/i;

        const filtered = pages.filter((page) =>
          pattern.test(page.title)
        );

        showContent(
          `fall/winter 2026 ${section}`,
          `fall/winter 2026 ${section}`,
          filtered.length ? '' : 'No matching page found yet.',
          filtered
        );
      } catch (error) {
        showContent('error', section, error.message);
      }
    }
  }

  // Section buttons
  document.querySelectorAll('[data-section]').forEach((button) => {
    button.addEventListener('click', () => {
      void openSection(button.dataset.section);
    });
  });

  // Home buttons
  ['homeButton', 'miniHome', 'backButton'].forEach((id) => {
    const button = $(id);
    if (button) button.addEventListener('click', showHome);
  });

  // Admin dialog
  const adminTrigger = $('adminTrigger');

  if (adminTrigger && dialog) {
    adminTrigger.addEventListener('click', () => dialog.showModal());
  }

  // Save API URL
  const saveApi = $('saveApi');

  if (saveApi) {
    saveApi.addEventListener('click', () => {
      const value = ($('apiBase')?.value || '').trim().replace(/\/$/, '');

      if (!value) {
        setStatus('Enter your FastAPI base URL.', true);
        return;
      }

      state.apiBase = value;
      localStorage.setItem('supremeApiBase', value);
      setStatus(`API saved: ${value}`);
    });
  }

  // Database setup
  const setupDb = $('setupDb');

  if (setupDb) {
    setupDb.addEventListener('click', async () => {
      try {
        const result = await api('/setup_database', { method: 'POST' });
        setStatus(result?.message || 'Database setup complete.');
      } catch (error) {
        setStatus(`Database setup failed: ${error.message}`, true);
      }
    });
  }

  // Refresh pages
  const refreshPages = $('refreshPages');

  if (refreshPages) {
    refreshPages.addEventListener('click', async () => {
      try {
        const pages = await fetchPages();
        setStatus(`Loaded ${pages.length} page(s) from /get_current.`);
      } catch (error) {
        setStatus(`Could not load pages: ${error.message}`, true);
      }
    });
  }

  // Clear page editor
  const clearEditor = $('clearEditor');

  if (clearEditor) {
    clearEditor.addEventListener('click', () => {
      setValue('pageId', '');
      setValue('pageTitle', '');
      setValue('pageText', '');
      setText('savePage', 'add page');
      setText('editorHeading', 'Add page');
      setStatus('Editor cleared.');
    });
  }

  // Load page
  const loadPage = $('loadPage');

  if (loadPage) {
    loadPage.addEventListener('click', async () => {
      const id = ($('pageId')?.value || '').trim();

      if (!id) {
        setStatus('Enter a page ID first.', true);
        return;
      }

      try {
        const data = await api(
          `/get_page?page_id=${encodeURIComponent(id)}`
        );

        const page = normalizePage(data);

        if (!page) {
          throw new Error('Unexpected page response format.');
        }

        setValue('pageId', page.id ?? id);
        setValue('pageTitle', page.title);
        setValue('pageText', page.text);
        setText('savePage', 'update page');
        setText('editorHeading', `Edit page ${page.id ?? id}`);
        setStatus(`Loaded page ${id}.`);
      } catch (error) {
        setStatus(`Could not load page: ${error.message}`, true);
      }
    });
  }

  // Save page
  const savePage = $('savePage');

  if (savePage) {
    savePage.addEventListener('click', async () => {
      const id = ($('pageId')?.value || '').trim();
      const title = ($('pageTitle')?.value || '').trim();
      const main_text = $('pageText')?.value || '';

      if (!title) {
        setStatus('Title is required.', true);
        return;
      }

      try {
        const params = new URLSearchParams({ title, main_text });

        if (id) {
          await api(
            `/update_page?page_id=${encodeURIComponent(id)}&${params.toString()}`,
            { method: 'PATCH' }
          );

          setStatus(`Page ${id} updated.`);
        } else {
          const result = await api(`/add_page?${params.toString()}`, {
            method: 'POST'
          });

          setStatus(
            `Page added${
              result?.page_id != null
                ? ` (ID ${result.page_id})`
                : ''
            }.`
          );

          if (result?.page_id != null) {
            setValue('pageId', result.page_id);
          }

          setText('savePage', 'update page');
          setText('editorHeading', `Edit page ${result?.page_id ?? ''}`);
        }

        await fetchPages();
      } catch (error) {
        setStatus(
          `Save failed: ${error.message}. Check your API schema field names.`,
          true
        );
      }
    });
  }

  fetchPages().catch((error) => {
    console.warn('Initial page fetch failed:', error.message);
  });

  console.info('Supreme frontend initialized.');
})();