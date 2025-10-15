const heroStartBtn = document.getElementById('startBtn');
const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const timerDisplay = document.getElementById('timer');
const waveform = document.getElementById('waveform');
const playback = document.getElementById('playback');
const generateFactsBtn = document.getElementById('generateFactsBtn');
const factsContent = document.getElementById('factsContent');
const mysteryCard = document.getElementById('mysteryCard');
const matchHeadline = document.getElementById('matchHeadline');
const scrollIndicator = document.getElementById('scrollIndicator');
const tryAgainBtn = document.getElementById('tryAgainBtn');
const wheelInner = document.getElementById('wheelInner');
const wheelCards = Array.from(document.querySelectorAll('.wheel-card'));
const heroAvatar = document.getElementById('heroAvatar');
const sceneImage = document.getElementById('sceneImage');
const wheelImages = Array.from(document.querySelectorAll('img[data-asset="qmark"]'));

const placeholderDataUri =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10'%3E%3C/svg%3E";

const assetPaths = {
  avatar: 'assets/avatar.png',
  qmark: 'assets/qmark.png',
  scene: 'assets/chat-scene.png'
};

const assetCache = {};

let mediaRecorder;
let audioChunks = [];
let countdownInterval;
let countdownTimeout;
let currentFacts = [];
let generateCardBtn;
let findMatchCardBtn;
let profiles = [
  {
    name: 'Jamie',
    fact1: 'Runs a rooftop garden',
    fact2: 'Collects vintage vinyl'
  },
  {
    name: 'Taylor',
    fact1: 'Trains for half-marathons',
    fact2: 'Volunteers at animal shelters'
  },
  {
    name: 'Robin',
    fact1: 'Hosts a movie trivia night',
    fact2: 'Learning conversational Italian'
  }
];
let wheelRotation = 0;

async function loadAssets() {
  const entries = Object.entries(assetPaths);
  await Promise.all(
    entries.map(async ([key, path]) => {
      try {
        const response = await fetch(path);
        const data = await response.text();
        assetCache[key] = data.trim();
      } catch (error) {
        assetCache[key] = '';
      }
    })
  );

  if (heroAvatar) {
    heroAvatar.src = assetCache.avatar || placeholderDataUri;
  }
  if (sceneImage) {
    sceneImage.src = assetCache.scene || placeholderDataUri;
  }
  wheelImages.forEach((img) => {
    img.src = assetCache.qmark || placeholderDataUri;
  });
}

function createQmarkImage() {
  const img = document.createElement('img');
  img.alt = 'Mystery';
  img.dataset.asset = 'qmark';
  img.src = assetCache.qmark || placeholderDataUri;
  return img;
}

async function setupMediaStream() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.ondataavailable = (event) => {
    if (event.data.size > 0) {
      audioChunks.push(event.data);
    }
  };
  mediaRecorder.onstop = handleRecordingStop;
}

async function startRecording() {
  if (!mediaRecorder) {
    try {
      await setupMediaStream();
    } catch (error) {
      alert('Microphone access is required to record.');
      return;
    }
  }

  audioChunks = [];
  mediaRecorder.start();
  recordBtn.disabled = true;
  stopBtn.disabled = false;
  generateFactsBtn.classList.add('hidden');
  playback.classList.add('hidden');
  playback.src = '';
  startCountdown(5);
  waveform.classList.add('active');

  countdownTimeout = setTimeout(() => {
    if (mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
    }
  }, 5000);
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
  }
}

function handleRecordingStop() {
  clearInterval(countdownInterval);
  clearTimeout(countdownTimeout);
  timerDisplay.textContent = '00:05';
  waveform.classList.remove('active');
  stopBtn.disabled = true;
  recordBtn.disabled = false;

  const blob = new Blob(audioChunks, { type: 'audio/webm' });
  const url = URL.createObjectURL(blob);
  playback.src = url;
  playback.classList.remove('hidden');
  generateFactsBtn.classList.remove('hidden');
}

function startCountdown(seconds) {
  let remaining = seconds;
  timerDisplay.textContent = formatTime(remaining);
  countdownInterval = setInterval(() => {
    remaining -= 1;
    timerDisplay.textContent = formatTime(Math.max(remaining, 0));
    if (remaining <= 0) {
      clearInterval(countdownInterval);
    }
  }, 1000);
}

function formatTime(value) {
  return `00:0${value}`;
}

function resetRecordingUI() {
  clearInterval(countdownInterval);
  clearTimeout(countdownTimeout);
  timerDisplay.textContent = '00:05';
  waveform.classList.remove('active');
  recordBtn.disabled = false;
  stopBtn.disabled = true;
  playback.classList.add('hidden');
  generateFactsBtn.classList.add('hidden');
}

function generateFacts(text) {
  const factPool = [
    'Loves chai',
    'CS @ UIUC',
    'Writes bad puns',
    'Bakes midnight cookies',
    'Runs sunrise 5Ks',
    'Builds indie games',
    'Collects concert tees',
    'Volunteers with robotics kids'
  ];
  const shuffled = [...factPool].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, 2);
}

function displayFacts(facts) {
  currentFacts = facts;
  const transcript = '“Hi I’m Avi I like chai and coding.”';
  factsContent.innerHTML = `
    <div class="space-y-4">
      <p class="text-white/70">Transcript sample: ${transcript}</p>
      <div class="bg-white/5 border border-white/10 rounded-3xl p-6 max-w-xl mx-auto">
        <h3 class="text-2xl font-semibold mb-3">Avinash</h3>
        <ul class="space-y-2">
          ${facts.map((fact) => `<li class="bg-white/5 rounded-full px-5 py-2">${fact}</li>`).join('')}
        </ul>
      </div>
    </div>
  `;

  if (!generateCardBtn) {
    generateCardBtn = document.createElement('button');
    generateCardBtn.className = 'btn-primary mt-6';
    generateCardBtn.textContent = 'Generate My Card';
    generateCardBtn.addEventListener('click', () => buildMysteryCard(currentFacts));
  }

  if (!factsContent.contains(generateCardBtn)) {
    factsContent.appendChild(generateCardBtn);
  }
}

function buildMysteryCard(facts) {
  mysteryCard.innerHTML = '';
  const avatar = document.createElement('img');
  avatar.src = assetCache.avatar || placeholderDataUri;
  avatar.alt = 'Mystery Avatar';

  const factList = document.createElement('ul');
  facts.forEach((fact) => {
    const li = document.createElement('li');
    li.textContent = fact;
    factList.appendChild(li);
  });

  const qrWrapper = document.createElement('div');
  qrWrapper.id = 'qrCode';
  qrWrapper.className = 'bg-white p-4 rounded-3xl';

  const note = document.createElement('p');
  note.id = 'mysteryNote';
  note.textContent = 'Data is local and resets on refresh.';

  if (!findMatchCardBtn) {
    findMatchCardBtn = document.createElement('button');
    findMatchCardBtn.className = 'btn-accent';
    findMatchCardBtn.textContent = 'Find My Match';
    findMatchCardBtn.addEventListener('click', startMatchSpin);
  }

  findMatchCardBtn.disabled = false;

  mysteryCard.appendChild(avatar);
  mysteryCard.appendChild(factList);
  mysteryCard.appendChild(qrWrapper);
  mysteryCard.appendChild(note);
  mysteryCard.appendChild(findMatchCardBtn);
  mysteryCard.classList.remove('hidden');

  qrWrapper.innerHTML = '';
  new QRCode(qrWrapper, {
    text: `${window.location.href.split('#')[0]}#profile-avinash`,
    width: 128,
    height: 128,
    colorDark: '#020617',
    colorLight: '#ffffff',
    correctLevel: QRCode.CorrectLevel.H
  });
}

function startMatchSpin() {
  if (!profiles.length) {
    fetchProfiles();
    setTimeout(() => {
      if (profiles.length) {
        startMatchSpin();
      }
    }, 400);
    return;
  }

  const targetIndex = Math.floor(Math.random() * profiles.length);
  const baseRotation = Math.floor(Math.random() * 360);
  wheelRotation += 720 + baseRotation;
  wheelInner.style.transform = `rotate(${wheelRotation}deg)`;

  if (findMatchCardBtn) {
    findMatchCardBtn.disabled = true;
  }
  matchHeadline.classList.add('hidden');
  scrollIndicator.classList.add('hidden');

  setTimeout(() => {
    revealMatch(targetIndex);
  }, 3100);
}

function revealMatch(index) {
  const profile = profiles[index % profiles.length];
  wheelCards.forEach((card) => {
    card.classList.remove('highlight');
    card.innerHTML = '';
    card.appendChild(createQmarkImage());
  });

  const selectedCard = wheelCards[index % wheelCards.length];
  selectedCard.classList.add('highlight');
  selectedCard.innerHTML = `
    <div class="card-content">
      <h4 class="text-lg font-semibold">${profile.name}</h4>
      <p class="text-sm text-white/80">${profile.fact1}</p>
      <p class="text-sm text-white/60">${profile.fact2}</p>
    </div>
  `;

  matchHeadline.classList.remove('hidden');
  scrollIndicator.classList.remove('hidden');
  createConfetti();

  setTimeout(() => {
    if (findMatchCardBtn) {
      findMatchCardBtn.disabled = false;
    }
  }, 1500);
}

function positionWheelCards() {
  const radius = (wheelInner.clientWidth / 2) - 70;
  wheelCards.forEach((card, index) => {
    const angle = (360 / wheelCards.length) * index;
    const radians = (angle * Math.PI) / 180;
    const x = Math.cos(radians) * radius;
    const y = Math.sin(radians) * radius;
    card.style.left = '50%';
    card.style.top = '50%';
    card.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px)`;
  });
}

function createConfetti() {
  const colors = ['#ec4899', '#34d399', '#fef3c7', '#bae6fd'];
  const confettiContainer = document.createElement('div');
  confettiContainer.className = 'confetti-container';
  document.body.appendChild(confettiContainer);

  for (let i = 0; i < 80; i += 1) {
    const piece = document.createElement('span');
    piece.className = 'confetti-piece';
    piece.style.background = colors[i % colors.length];
    piece.style.left = `${Math.random() * 100}%`;
    piece.style.setProperty('--x', `${Math.random() * 100}%`);
    piece.style.setProperty('--drift', `${(Math.random() - 0.5) * 60}%`);
    piece.style.animationDuration = `${1.5 + Math.random()}s`;
    confettiContainer.appendChild(piece);
  }

  setTimeout(() => {
    confettiContainer.remove();
  }, 2500);
}

function observeSections() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          if (entry.target.id === 'scene') {
            entry.target.querySelectorAll('.chat-bubble').forEach((bubble, idx) => {
              bubble.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
              bubble.style.opacity = '1';
              bubble.style.transform = 'translateY(0)';
              bubble.style.transitionDelay = `${idx * 0.15}s`;
            });
          }
        }
      });
    },
    { threshold: 0.2 }
  );

  document.querySelectorAll('.section-card').forEach((section) => {
    observer.observe(section);
    if (section.id === 'scene') {
      section.querySelectorAll('.chat-bubble').forEach((bubble) => {
        bubble.style.opacity = '0';
        bubble.style.transform = 'translateY(12px)';
      });
    }
  });
}

function fetchProfiles() {
  fetch('docs/demo-profiles.json')
    .then((response) => response.json())
    .then((data) => {
      profiles = data;
    })
    .catch(() => {
      profiles = [
        { name: 'Alex', fact1: 'Enjoys improv nights', fact2: 'Brews kombucha' }
      ];
    });
}

function smoothScrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

heroStartBtn.addEventListener('click', () => {
  document.getElementById('record').scrollIntoView({ behavior: 'smooth' });
  setTimeout(() => {
    recordBtn.focus();
  }, 500);
});

recordBtn.addEventListener('click', () => {
  startRecording();
});

stopBtn.addEventListener('click', stopRecording);
generateFactsBtn.addEventListener('click', () => {
  const transcript = "Hi I'm Avi I like chai and coding.";
  const facts = generateFacts(transcript);
  displayFacts(facts);
});
tryAgainBtn.addEventListener('click', smoothScrollToTop);

async function init() {
  await loadAssets();
  positionWheelCards();
  observeSections();
  fetchProfiles();
}

init();

window.addEventListener('resize', positionWheelCards);
