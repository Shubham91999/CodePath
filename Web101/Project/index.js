/*** Dark Mode ***
  
  Purpose:
  - Use this starter code to add a dark mode feature to your website.

  When To Modify:
  - [ ] Project 5 (REQUIRED FEATURE) 
  - [ ] Any time after
***/

// Step 1: Select the theme button
let themeButton = document.getElementById('theme-button');

// Helper: apply visual state to button and body
function applyDarkModeState(isDark) {
  if (isDark) {
    document.body.classList.add('dark-mode');
    if (themeButton) {
      themeButton.textContent = 'Toggle Light Mode';
      themeButton.setAttribute('aria-pressed', 'true');
    }
  } else {
    document.body.classList.remove('dark-mode');
    if (themeButton) {
      themeButton.textContent = 'Toggle Dark Mode';
      themeButton.setAttribute('aria-pressed', 'false');
    }
  }
}

// Step 2: Write the callback function
const toggleDarkMode = () => {
  const isNowDark = document.body.classList.toggle('dark-mode');
  console.log('[theme] dark mode toggled:', isNowDark);
  // update button label and aria state
  applyDarkModeState(isNowDark);
  // persist user preference
  try {
    localStorage.setItem('darkMode', isNowDark ? '1' : '0');
  } catch (e) {
    // ignore localStorage errors
  }
}

// Initialize from saved preference (if any)
try {
  const saved = localStorage.getItem('darkMode');
  const shouldBeDark = saved === '1';
  applyDarkModeState(shouldBeDark);
} catch (e) {
  // ignore
}

// Step 3: Register a 'click' event listener for the theme button,
//             and tell it to use toggleDarkMode as its callback function
if (themeButton) {
  themeButton.addEventListener('click', toggleDarkMode);
}


/*** Form Handling ***
  
  Purpose:
  - When the user submits the RSVP form, the name and state they 
    entered should be added to the list of participants.

  When To Modify:
  - [ ] Project 6 (REQUIRED FEATURE)
  - [ ] Project 6 (STRETCH FEATURE) 
  - [ ] Project 7 (REQUIRED FEATURE)
  - [ ] Project 9 (REQUIRED FEATURE)
  - [ ] Any time between / after
**/

// Step 1: Add your query for the submit RSVP button here

const rsvpButton = document.getElementById('rsvp-button');

const addParticipant = (person) => {
  // person: { name, hometown, email }
  if (!person || !person.name) return;

  const participantsDiv = document.querySelector('.participants');
  if (participantsDiv) {
    const p = document.createElement('p');
    p.textContent = `🎟️ ${person.name} from ${person.hometown || 'Unknown'} has RSVP'd.`;
    participantsDiv.appendChild(p);

    // Update count
    const countEl = document.getElementById('rsvp-count');
    let count = 0;
    if (countEl) {
      const text = countEl.textContent || '';
      const match = text.match(/⭐\s*(\d+)/);
      count = match ? parseInt(match[1], 10) : 0;
      count = count + 1;
      const newCountEl = document.createElement('p');
      newCountEl.id = 'rsvp-count';
      newCountEl.textContent = `⭐ ` + count + " people have RSVP'd to this event!";
      countEl.remove();
      participantsDiv.parentElement.appendChild(newCountEl);
    }

    // Show success modal with animation (if present)
    try { toggleModal(person); } catch (e) { /* ignore if modal not ready */ }
  }
}

// Step 3: Add a click event listener to the submit RSVP button here
// We will replace this listener below with validation-aware listener
if (rsvpButton) {
    rsvpButton.removeEventListener('click', addParticipant);
}

/*** Form Validation ***
  
  Purpose:
  - Prevents invalid form submissions from being added to the list of participants.

  When To Modify:
  - [ ] Project 7 (REQUIRED FEATURE)
  - [ ] Project 7 (STRETCH FEATURE)
  - [ ] Project 9 (REQUIRED FEATURE)
  - [ ] Any time between / after
**/

// Step 1: We actually don't need to select the form button again -- we already did it in the RSVP code above.

// Step 2: Write the callback function
const validateForm = () => {

  let containsErrors = false;

  const form = document.getElementById('rsvp-form');
  var rsvpInputs = form.elements;

  // Build person object from current inputs
  const person = {
    name: (document.getElementById('rsvp-name')?.value || '').trim(),
    hometown: (document.getElementById('rsvp-city')?.value || '').trim(),
    email: (document.getElementById('rsvp-email')?.value || '').trim()
  };

  // Loop through all inputs and run simple length validation
  for (let i = 0; i < rsvpInputs.length; i++) {
    const input = rsvpInputs[i];
    if (!input || !input.type) continue;
    const value = (input.value || '').trim();

    if (input.type === 'text' || input.type === 'email') {
      if (value.length < 2) {
        containsErrors = true;
        input.classList.add('error');
      } else {
        input.classList.remove('error');
      }
    }
  }

  // Email-specific check: must contain '@'
  const emailEl = document.getElementById('rsvp-email');
  if (emailEl) {
    const emailVal = person.email;
    if (emailVal.indexOf('@') === -1) {
      containsErrors = true;
      emailEl.classList.add('error');
    } else {
      emailEl.classList.remove('error');
    }
  }

  // If no errors, call addParticipant(person) and clear fields
  if (!containsErrors) {
    addParticipant(person);
    // Clear inputs and remove error styles
    for (let i = 0; i < rsvpInputs.length; i++) {
      const input = rsvpInputs[i];
      if (input && input.classList) input.classList.remove('error');
      try { input.value = ''; } catch (e) {}
    }
  }

}

// Step 3: Replace the form button's event listener with a new one that calls validateForm()
if (rsvpButton) {
  rsvpButton.addEventListener('click', (e) => {
    e.preventDefault();
    validateForm();
  });
}

/*** Form Validation [PLACEHOLDER] [ADDED IN UNIT 7] ***/
/*** Animations [PLACEHOLDER] [ADDED IN UNIT 8] ***/

/*** Modal ***
  
  Purpose:
  - Use this starter code to add a pop-up modal to your website.

  When To Modify:
  - [ ] Project 9 (REQUIRED FEATURE)
  - [ ] Project 9 (STRETCH FEATURE)
  - [ ] Any time after
**/

let modalInterval = null;
let modalTimeout = null;
let reduceMotion = false; // toggled by UI later

// TODO: animation variables and animateImage() (Step 5)
let rotateFactor = 0;
let modalImage = document.getElementById('modal-image');

function animateImage() {
  // toggle between 0 and -10 degrees to create a "waving" effect
  if (rotateFactor === 0) rotateFactor = -10; else rotateFactor = 0;
  if (modalImage) {
    modalImage.style.transform = `rotate(${rotateFactor}deg)`;
  }
}

// Close modal helper: hides modal, clears timers, and resets image
function closeModal() {
  const modal = document.getElementById('success-modal');
  if (!modal) return;

  // Clear timers
  if (modalInterval) { clearInterval(modalInterval); modalInterval = null; }
  if (modalTimeout) { clearTimeout(modalTimeout); modalTimeout = null; }

  // Remove overlay click listener if it was saved
  if (modal._onOverlayClick) {
    modal.removeEventListener('click', modal._onOverlayClick);
    modal._onOverlayClick = null;
  }

  // Hide and reset
  modal.style.display = 'none';
  modal.setAttribute('aria-hidden', 'true');
  if (modalImage) modalImage.style.transform = '';
}

const toggleModal = (person) => {
  const modal = document.getElementById('success-modal');
  const modalText = document.getElementById('modal-text');
  // refresh reference to the modal image element (top-level var holds the node)
  modalImage = document.getElementById('modal-image');
  if (!modal) return;

  // Personalized message
  if (modalText) modalText.textContent = `Thanks for RSVPing, ${person.name}! We can't wait to see you at the event in ${person.hometown || 'your area'}!`;

  // Show modal
  modal.style.display = 'flex';
  modal.setAttribute('aria-hidden', 'false');

  // Clear previous timers if any
  if (modalInterval) { clearInterval(modalInterval); modalInterval = null; }
  if (modalTimeout) { clearTimeout(modalTimeout); modalTimeout = null; }

  // Animate image (if motion allowed) - rotate "wave" every 500ms
  let intervalId = null;
  if (!reduceMotion && modalImage) {
    modalImage.style.transformOrigin = 'center center';
    intervalId = setInterval(animateImage, 500);
    // keep compatibility with older clearing logic
    modalInterval = intervalId;
  }

  // Auto-dismiss after 5 seconds
  modalTimeout = setTimeout(() => {
    if (intervalId) { clearInterval(intervalId); }
    if (modalInterval) { clearInterval(modalInterval); modalInterval = null; }
    modal.style.display = 'none';
    modal.setAttribute('aria-hidden', 'true');
    if (modalImage) modalImage.style.transform = '';
  }, 5000);

  // Allow clicking the overlay (outside modal container) to close early
  const onOverlayClick = (e) => {
    if (e.target === modal) {
        if (intervalId) { clearInterval(intervalId); }
        if (modalInterval) { clearInterval(modalInterval); modalInterval = null; }
        if (modalTimeout) { clearTimeout(modalTimeout); modalTimeout = null; }
      modal.style.display = 'none';
      modal.setAttribute('aria-hidden', 'true');
      modal.removeEventListener('click', onOverlayClick);
      modal._onOverlayClick = null;
      if (modalImage) modalImage.style.transform = '';
    }
  };
  modal.addEventListener('click', onOverlayClick);
  // save reference so other code (closeModal) can remove listener
  modal._onOverlayClick = onOverlayClick;
}

// Wire up modal close button (if present)
document.addEventListener('DOMContentLoaded', () => {
  const closeBtn = document.getElementById('modal-close-button');
  if (closeBtn) {
    closeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      closeModal();
    });
  }

  // Reduce Motion button wiring and state
  const reduceBtn = document.getElementById('reduce-motion-button');
  try {
    const saved = localStorage.getItem('reduceMotion');
    reduceMotion = saved === '1';
  } catch (e) {
    reduceMotion = false;
  }
  if (reduceBtn) {
    reduceBtn.setAttribute('aria-pressed', reduceMotion ? 'true' : 'false');
    reduceBtn.addEventListener('click', (e) => {
      e.preventDefault();
      reduceMotion = !reduceMotion;
      reduceBtn.setAttribute('aria-pressed', reduceMotion ? 'true' : 'false');
      // persist preference
      try { localStorage.setItem('reduceMotion', reduceMotion ? '1' : '0'); } catch (err) {}
      // if motion is now reduced, clear any running modal animation
      if (reduceMotion && modalInterval) {
        clearInterval(modalInterval);
        modalInterval = null;
      }
    });
  }
  
  // YouTube lazy-load placeholder: replace with iframe on click as a fallback for embed errors
  const ytPlaceholder = document.getElementById('youtube-placeholder');
  if (ytPlaceholder) {
    const videoId = ytPlaceholder.getAttribute('data-video-id');
    const playBtn = document.getElementById('youtube-play-button');
    const loadIframe = () => {
      const watchUrl = `https://www.youtube.com/watch?v=${videoId}`;
      // Create iframe element
      const iframe = document.createElement('iframe');
      iframe.width = '500';
      iframe.height = '350';
      iframe.title = 'STEM for Kids Fair video';
      iframe.frameBorder = '0';
      iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
      iframe.allowFullscreen = true;

      // Try the standard YouTube embed first (more likely to play inline)
      iframe.src = `https://www.youtube.com/embed/${videoId}?rel=0&autoplay=1`;

      // If the iframe doesn't successfully load the playable player within a short time,
      // fall back to opening the watch page where embedding restrictions don't apply.
      let didLoad = false;
      const loadTimeout = setTimeout(() => {
        if (didLoad) return;
        // fallback: open watch page in new tab and leave the placeholder intact
        window.open(watchUrl, '_blank', 'noopener');
      }, 2500);

      // onload will fire when the iframe document is loaded, but that doesn't guarantee playback.
      iframe.addEventListener('load', () => {
        didLoad = true;
        clearTimeout(loadTimeout);
        // Replace placeholder with iframe
        try { ytPlaceholder.parentElement.replaceChild(iframe, ytPlaceholder); } catch (e) {
          // If replacement fails, open on YouTube as a fallback
          window.open(watchUrl, '_blank', 'noopener');
        }
      });

      // extra safety: listen for a possible error event on iframe
      iframe.addEventListener('error', () => {
        clearTimeout(loadTimeout);
        window.open(watchUrl, '_blank', 'noopener');
      });
    };

    if (playBtn) playBtn.addEventListener('click', (e) => { e.preventDefault(); loadIframe(); });
    // also make clicking the placeholder load the iframe
    ytPlaceholder.addEventListener('click', (e) => {
      // avoid triggering when user clicked the 'Open on YouTube' link
      if (e.target && e.target.tagName.toLowerCase() === 'a') return;
      loadIframe();
    });
  }
});

/*** Success Modal [PLACEHOLDER] [ADDED IN UNIT 9] ***/