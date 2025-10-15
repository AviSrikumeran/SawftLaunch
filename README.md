# SawftLaunch  
*Go from cold open to sawft launch.*

## Overview  
SawftLaunch is a voice-based icebreaker game built for live dating events such as Cupid Dating. Attendees record a short voice intro that generates fun facts and mystery cards, turning spectators into participants and lowering social barriers.

## Live Demo  
https://YOURUSERNAME.github.io/sawftlaunch  

## How It Works  
1. Press Record — speak for 5 seconds.  
2. AI (simulated) creates two fun facts from your voice.  
3. A mystery card appears with your QR code.  
4. Spin the wheel to find your match.  
5. Scroll to see a sample connection scene.  

## Tech Stack  
– HTML / CSS / JavaScript  
– Tailwind CSS CDN  
– qrcode.js for QR generation  
– MediaRecorder API for audio  

## What’s Real vs Simulated  
✅ Real: recording, playback, QR display, animations.  
🌀 Simulated: AI fact generation, match logic.  

## Purpose  
To demonstrate how SawftLaunch can make Cupid Dating events more interactive, boost audience engagement, and create sponsor-ready moments.

## Future Steps  
– Integrate OpenAI Whisper + GPT for real voice→fact generation.  
– Add Firebase storage for profiles and matches.  
– Create event dashboard for organizers.  

## Deployment  
```bash
git add .  
git commit -m "Initial POC"  
git push origin main  
# Enable GitHub Pages from main branch (root folder)
```

Author

Built by Avinash Sri-Kumeran — contact [your email]
Built for kupid Dating events, 2025.

Once code generation is complete, push all files to the new GitHub repo, enable Pages from the **main/root** branch, confirm the HTTPS site works (mic permissions must be granted), test on phone and desktop, and you’ll have a polished live POC showing voice → facts → mystery card → spinning match → connection scene, ready to send to Cupid Dating with your demo link and video capture.
