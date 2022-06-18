storyteller-ml
==============
The core TTS models that power FakeYou.

I'm in the progress of pulling these out of the service monorepo so we can iterate faster.

**This code sucks and doesn't run yet**. 

1. Please do not think this is indicative of the kind of code I work on or maintain. 
   This was a hermetic module that the FakeYou service called out to, and I want to improve it now. 
   The rest of the frontend and backend are in a good state.
 
2. I'll spend some time getting this cleaned up and working before getting any help with it.

How This Works
--------------
We have a Rust monolith that controls the user interface, account system, and all the database CRUD operations.
It doesn't do any ML work itself or have any attached GPUs.

There are a series of worker pods ("jobs") that pull from work queues and run inference, then upload the results.

![](docs/diagrams/microservices.png)

The jobs are written in Rust and either shell out to Python code or call an in-container Python server that attempts 
to LRU cache models in memory.

![](docs/diagrams/jobs1.png)

![](docs/diagrams/jobs2.png)

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

Docker image cleanup

- [ ] Remove docker-base-images-nvidia-cuda-experimental
- [ ] Remove inessential build pieces

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
