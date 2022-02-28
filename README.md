tts-core
========
The core TTS models that power FakeYou.

I'm in the progress of pulling these out of the service monorepo so we can iterate faster.

TODO
----

Core cleanup

- [ ] Cleanup Tacotron code 
  - [ ] Integrate WaveGlow and HifiGan more cleanly
  - [ ] Define the HTTP server interface
  - [ ] Define the model checking interface
  - [ ] Clean up in-memory LRU caching
  - [ ] There are two copies of Nemo. Why? Clean this up.
- [ ] Deployability
  - [ ] Clean up requirements.txt and upgrade packages 
  - [ ] Clean up Dockerfile

Make the models sound better

- [ ] Arpabet
  - [ ] G2P
  - [ ] Arpabet custom dictionary
  - [ ] User-supplied Arpabet strings in braces

- [ ] Word break down 888 -> eight hundred eighty eight

- [ ] Support I18N
  - [ ] Accent character support

Introduce new models

- [ ] TalkNet
- [ ] GlowTTS + MelGan (vocoder)
- [ ] Make these work under the same venv

Lots more I haven't covered yet...
