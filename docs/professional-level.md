# How this is done at a professional and frontier level, and what it costs

Researched on 15 October 2026. **How to read it:** every figure carries its source. Almost all are blogs and comparisons (marked **[S]**, secondary), which contradict each other on prices; official pages or magazine articles are **[P]** (primary). What comes from my own reasoning and not from a source I mark **[mine]**. Prices change every month: they are indicative, not quotes.

## Summary
1. **What we did is a real and current workflow**, not a toy: video and 3D "as code" (HyperFrames/Remotion, Three.js, Blender through Python) is exactly what teams that automate production use.
2. **The frontier passes through three places**: AI-generated video (Veo, Kling, Runway, Seedance), AI-generated 3D (Rodin, Tripo, Meshy) and agents that orchestrate tools (ComfyUI, Claude Code, USD).
3. **At a professional level the money is not in the tools** (almost all cost cents per piece) **but in the license and the human review**. The latter **I could not quantify**: I found no reliable rates for studios or freelancers, and I do not invent them.
4. **What separates our exercise from a studio most** is not the technology but quality control, rights (voice, music, models) and delivery to standards.

---

## 1. Video and motion graphics

### Video as code (what we did)
| Option | What it is | Cost |
| --- | --- | --- |
| **HyperFrames** (the one we used) | HTML + GSAP → MP4, Apache 2.0, plugin for Claude Code | 0 USD, no pay per render. Source: [repository](https://github.com/heygen-com/hyperframes) **[P]** |
| **Remotion** | Video from React components | Free for individuals and organizations of up to 3 people. Creators 25 USD per seat per month; **Automators 0.01 USD per render with a minimum of 100 USD per month**; Enterprise from 500 USD per month. Source: [pricing](https://www.remotion.dev/docs/license/pricing) **[P/S]** |
| **Remotion Lambda** | Distributed rendering in your own AWS account | Examples from its documentation: a 1-minute HD video ≈ 0.017–0.021 USD and a 10-minute one ≈ 0.10 USD (from an old version; measure again). [Docs](https://www.remotion.dev/docs/lambda/cost-example) **[P]** |
| **Shotstack** | Video API with JSON templates | From ≈ 39 USD per month (200 credits at 0.20 USD per rendered minute) or 0.30 USD per minute without a subscription. [Comparison](https://www.wireflow.ai/blog/creatomate-vs-shotstack) **[S]** |
| **Creatomate** | Video API with templates | From ≈ 41–54 USD per month (2,000 credits); the cost per minute at 1080p ranges from 0.10 to 0.84 USD depending on the source. [Comparison](https://www.plainlyvideos.com/blog/best-video-editing-api) **[S]** |

**How a professional team does it [mine, general knowledge, not verified today]:** After Effects or Remotion templates fed with data, rendering on a farm, version control of the scripts and human review before delivery.

### AI-generated video (frontier)
It costs per second of video and serves for **people and realistic shots**, exactly what our method cannot do (the source document already warned about it).
| Model | Approximate price per second | Note |
| --- | --- | --- |
| Veo (Google) | 0.05 – 0.60 USD (typical 0.40 with audio) | Each pass reaches 8 s |
| Kling 3.0 | 0.07 – 0.126 USD | The "economy" one |
| Runway Gen-4.5 | 0.12 USD (12 credits at 0.01) | No upscaling extras |
| Seedance 2.0 | 0.07 (480p) – 0.37 USD (1080p) | Billing by tokens in 2.5 |
| Sora | 0.10 – 0.75 USD depending on the source | **Uncertain status**: one source says it shuts down on 24 Sep 2026 and another that the web and app shut down on 26 April; check with OpenAI |

Sources **[S]**: [fluxnote](https://fluxnote.io/guides/ai-video-model-pricing-comparison-2026), [Crazyrouter](https://crazyrouter.com/en/blog/ai-video-generation-api-pricing-may-2026-comparison), [AI Video Cost Calculator](https://aivideotoolbox.com/cost-calculator). Each provider's prices differ depending on resolution, audio and whether you go through an aggregator.

### How it is orchestrated at a studio level
- **ComfyUI** (node graphs) appears as the backbone for fine control: chaining fill, depth maps and relighting until clean frames for compositing. Source: [Comfy blog](https://blog.comfy.org/p/the-8-best-ai-creative-workflow-platforms) **[S, from the manufacturer itself]**.
- **Ubisoft** describes a pipeline with agents on its USD microservices (n8n + ComfyUI) that turns briefs into asset lists and previews. It is the most solid example I found: an [ACM article](https://dl.acm.org/doi/10.1145/3819990.3820033) **[P]**.
- **Utopai Studios** produces an animated feature film that combines traditional animation and generative video ([Wikipedia](https://en.wikipedia.org/wiki/Text-to-video_model), **[S]**).
- One document claims that DNEG uses its own ComfyUI nodes inside Nuke: it is an unverified secondary source, do not take it as true.

---

## 2. Web 3D and product configurators

### Technology
- **Three.js** is what we use (r186). Today the renderer recommended in the guides is **WebGPURenderer** (since r171, with an automatic fallback to WebGL2). WebGPU reached "Baseline" in January 2026 in Chrome/Edge 113+, Safari 26+ and Firefox 141+ on Windows; Firefox on Macs with Apple Silicon and Linux/Android lag behind. Global support ≈ 87% (caniuse, August 2026) according to one source and ≈ 70% according to another. Sources **[S]**: [vr.org](https://vr.org/articles/webgpu-baseline-2026-three-js-webxr-default), [utsubo](https://www.utsubo.com/blog/frontier-web-apis-2026-production-ready). **This answers the doubt I left open: yes, WebGPU is already used in production** (Three.js, Babylon.js, Figma, according to the sources).
- **Note for this code:** the migration guide warns that r186 removed `PCFSoftShadowMap` for WebGPURenderer, exactly the warning we got in Phase 3.

### Optimizing a 3D model for the web (what we did NOT do)
Our `.glb` weighs 250 KB because it carries no textures. A real product does, and the professional flow is:
- **`gltf-transform optimize`**: reduce textures first (they are usually 80% or more of the file), quantize vertices, compress geometry, simplify and clean up duplicates.
- **Meshopt or Draco, never both at once.** Meshopt is the usual choice with animations; Draco compresses a bit more but decodes slower.
- **KTX2** to save GPU memory on mobile.
- Indicative references from a single source: a typical product model goes down from 8–15 MB to 1–2 MB; under 800 KB for "hero" scenes. Always keep the unoptimized original (it is lossy). Source **[S]**: [GLB optimization guide](https://svilenkovic.com/3d/glb-optimization).
- For AR (Apple's USDZ, `model-viewer`) I found no reliable information: you have to go to each one's documentation.

### Commercial configurator platforms
| Platform | Cost according to the sources | Note |
| --- | --- | --- |
| **Threekit** (enterprise) | By quote: from 999 USD/month (old) up to 30,000–100,000+ USD per year | Implementation of 3 to 6 months. [Capterra](https://www.capterra.com/p/181527/3D-Product-Configurator/), [cpq3d](https://cpq3d.com/3d-product-configurator-cost/) **[S]** |
| **Vectary** | Pro 25–29 USD per user per month; Business 79 | It is a design tool and viewer, **not** a configurator with prices. **[S]** |
| **Zakeke** | Accessible alternative for SMEs | **[S]**, no reliable figures |
| **CPQ3D** | 3–12 € per quote request after 10 free ones | **[S]** |
| **Three.js / Babylon.js / PlayCanvas** | Open source; the cost is hosting and development time | I found no figures: I note it as a gap |

**Where our viewer fits [mine]:** it is the basis of what these platforms offer (model, parts, color, exploded view), but **without** what large customers really pay for: pricing and variant logic, orders, ERP and catalog integration.

### Generating the 3D with AI (frontier)
| Service | Cost per model (approx.) | License/note |
| --- | --- | --- |
| Tripo | 0.05 – 0.20 USD; Pro plan 19.90 USD per month for 3,000 credits | The free tier is **non-commercial** |
| Meshy | 0.10 – 0.30 USD | The free one comes out with CC BY 4.0: it can be sold but they must be credited |
| Rodin (Hyper3D) | 0.40 – 0.80 USD (credits at 1.50 USD) | One source requires a business subscription (120 USD per month) for the API; another contradicts it |

Sources **[S]**: [3D AI Studio](https://www.3daistudio.com/3d-generator-ai-comparison-alternatives-guide/how-much-does-ai-3d-model-generation-cost), [comparison on DEV](https://dev.to/trify3dhq/best-ai-3d-model-generator-tripo-vs-meshy-vs-rodin-2026-34cl). The first one is from a competitor that sells its own aggregator. **This is exactly the method the Blender MCP server has built in** (`generate_3d` with Tripo, Hunyuan3D and Hyper3D Rodin).

---

## 3. Blender and rendering

| Cloud render service | Price per GPU hour |
| --- | --- |
| Sky Render Farm | ≈ 0.65 USD (RTX 5090, per second) |
| RenderJuice | 1.27 – 1.73 USD (plans from 49 USD per month) |
| Blender.farm | ≈ 3 USD (2.25 in the larger package) |
| RenderStreet | 4.49 USD per server hour (L40S) |
| iRender | 8.20 – 9 USD (dedicated servers) |

Sources **[S]**: [Blender.farm](https://www.blender.farm/pricing), [RenderJuice](https://www.renderjuice.com/pricing), [Sky Render Farm](https://www.skyrenderfarm.com/blog/render-farm-pricing-in-2026-how-much-does-cloud-rendering-cost), [RenderStreet](https://render.st/plans-pricing/). Each one bills in different units and one comparison says that a farm charged 42% more than another for the same RTX 5090 hour: **always test with your own scene**.

**Our case [mine, arithmetic with those rates]:** the 120-frame animation took 61.5 s on the author's Mac (≈ 0.017 GPU hours). On a farm at 3 USD per hour it would be ≈ 0.05 USD; between 0.01 and 0.15 USD depending on the farm. For this size of job, **rendering is not a relevant cost**.

**What a studio does and we do not [mine, general knowledge, not verified today]:** Cycles instead of Eevee for final quality, color management (ACES/OCIO), **USD** scenes between programs (Houdini/Solaris, Maya, Omniverse), asset tracking and shot review. I found no reliable sources on Omniverse or on Firefly in studio pipelines.

---

## 4. Voice and music

### Voice
- **ElevenLabs** (commercial reference): according to a source dated 12 October 2026, **0.08 USD per 1,000 characters** with Eleven v4 and **0.04** with v4 Turbo; earlier guides gave 0.10 and 0.05. The free tier **does not allow commercial use**; the Starter plan is the cheapest with a commercial license; Business costs 990 USD per month. Sources **[S]**: [puter](https://developer.puter.com/tutorials/elevenlabs-api-pricing/), [cekura](https://www.cekura.ai/blogs/elevenlabs-pricing), [official prices](https://elevenlabs.io/pricing/api) **[P]** (which I could not load).
- **Our case [mine]:** the script has 206 characters, so it would be **≈ 0.008–0.017 USD**.
- **Perceived quality:** in the [Artificial Analysis](https://artificialanalysis.ai/text-to-speech/leaderboard) arena **[P]**, Eleven v4 Turbo is first (Elo 1328, proprietary), followed by several proprietary Qwen and Gemini models. The best open-weight one is Fish Audio Drama 3 (1242), but **it weighs 24 GB and its license is for research**; Kokoro, the one we used, is 56th (Elo 1061). By ear, for this Spanish script, **you liked Kokoro more than Qwen3-TTS**.

### Music
- **AI-generated (Suno, Udio):** the rights landscape is **half-resolved**. Udio and Suno signed deals with Universal (only Udio) and Warner (both) between October and November 2025; Universal and Sony with Suno remain unresolved according to the [Financial Times](https://www.musicbusinessworldwide.com/sunos-licensing-talks-with-major-labels-in-limbo-with-no-path-forward-report/) **[P]**. On Suno, Pro (10 USD per month) and Premier (30 USD) include commercial rights for new songs, but a single source says that from 3 September 2026 commercial use depends on a permitted download: **unverified**. Udio is a "walled garden": what is created barely leaves the platform. Sources **[S]**: [Undetectr](https://undetectr.com/blog/suno-commercial-use), [genre-ai](https://genre-ai.app/blog/suno-vs-udio-licensing-deals-2026).
- **ElevenLabs Music:** billed in credits (900 per minute, according to one source **[S]**).
- **What we did [mine]:** music synthesized by code, without samples or models: there is no rights problem, at the cost of sounding simple.

---

## 5. Orchestrating it with AI agents

| Concept | Data |
| --- | --- |
| Claude plans | Pro 20 USD (17 annual) · Max 5x 100 USD · Max 20x 200 USD · Team: Standard ≈ 25 USD/seat (20 annual), Premium ≈ 125 (100 annual), minimum 5 members · Enterprise custom. Source **[S]**: [superblocks](https://www.superblocks.com/blog/claude-code-pricing); the Pro plan is confirmed by [Anthropic's pricing page](https://claude.com/pricing) **[P]**. Whether Team Standard includes full Claude Code **is a discrepancy between sources** |
| Price per million tokens (input / output) | Opus 5.5 4 / 20 USD [P, Anthropic] · Sonnet 5.5 2 / 10 [S] · Haiku 5.5 0.10 / 0.50 [S] · GPT-6.1 Sol 2 / 10 [P, OpenAI] · GPT-6 Astra 10 / 50 (unconfirmed) |
| Performance on coding tasks (frontier) | Opus 5.5: 66.4% on Terminal-Bench 4.0 versus Astra's 57.9%, according to [Anthropic](https://www.anthropic.com/claude-opus-5-5) **[P]**, which warns that at this level the margins are misleading |
| Cost per task (a single data point) | Rails benchmark: Opus 5.5 got 65.3% right at 10.53 USD per task; GPT-6.1 Sol 60.8% at 0.80 **[S, post on X]** |
| "Frontier" cases | From the source document (secondary sources): migration of HAProxy from C to Rust in 9.5 h, 40 chained PRs at Stripe, audit of 200,000 lines in under 3 h |
| Our experiment | The local model did the task well but ~7 times slower than Sonnet; **a single attempt per model**, not statistics |

**How teams do it [mine, with the exception of Ubisoft above]:** they orchestrate with a workflow tool (n8n, ComfyUI or code), version everything, measure with automatic evaluators and leave the approval to a person. It is the same shape we built on a small scale.

---

## 6. How much it would cost to make THIS promo with paid services [mine, illustrative]
Arithmetic on the rates above. **It is not a quote**: it does not include human work, which is the real cost and for which I have no figures.

| Piece | What we did | With paid services (order of magnitude) |
| --- | --- | --- |
| 20 s video | HyperFrames, free | Remotion Lambda ≈ 0.007 USD; Shotstack 0.07–0.10 USD |
| AI-generated video (if a realistic 20 s shot were wanted) | Does not apply | 1.00–12.00 USD **per attempt** (0.05–0.60 USD/s); with 10 attempts, 10–120 USD |
| 3D | Blender with code, free | One AI-generated model: 0.05–0.80 USD |
| Render | 61.5 s on an M4 Max Mac | 0.01–0.15 USD on a farm |
| Voice | Kokoro, free | 0.008–0.017 USD |
| Music | Code, free | Suno Pro 10 USD/month, or a library license |
| AI model | Pro plan (20 USD/month) | Opus 5.5 through the API: depends on the tokens |
| **Total of tools** | **0 USD beyond the Pro plan** | **Under ≈ 30 USD per month for this volume**, unless generated video is used |

---

## 7. What our exercise lacks to be "pro" [mine, analysis]
1. **Delivery to standards:** codec and color profiles agreed with the client, and the sound level each destination requires (we use −16 LUFS, reasonable for the web; I did not check it against any platform specification).
2. **Rights and traceability:** where each voice, music and model comes from, with their licenses (Kokoro Apache 2.0 yes; Whisper and Qwen I did not verify).
3. **`.glb` optimization** (textures, compression) and tests on real phones.
4. **Automatic visual regression tests** and human review of every delivery (we look at contact sheets by hand).
5. **Measured accessibility and performance** of the viewer (I took care of it, but not with an audit).
6. **Several repetitions of the model experiment**, larger tasks and one more model: the comparison we made has one attempt per model.
7. **The human side:** art direction, script and judgment. The tools make it cheaper, they do not replace it.

## Main sources
[Anthropic · Opus 5.5](https://www.anthropic.com/claude-opus-5-5) · [Claude pricing](https://claude.com/pricing) · [Artificial Analysis · TTS](https://artificialanalysis.ai/text-to-speech/leaderboard) · [Remotion · pricing](https://www.remotion.dev/docs/license/pricing) · [HyperFrames](https://github.com/heygen-com/hyperframes) · [ACM · Ubisoft](https://dl.acm.org/doi/10.1145/3819990.3820033) · [Music Business Worldwide](https://www.musicbusinessworldwide.com/sunos-licensing-talks-with-major-labels-in-limbo-with-no-path-forward-report/) · [Blender.farm](https://www.blender.farm/pricing) · [RenderJuice](https://www.renderjuice.com/pricing) · [Sky Render Farm](https://www.skyrenderfarm.com/blog/render-farm-pricing-in-2026-how-much-does-cloud-rendering-cost) · [vr.org · WebGPU](https://vr.org/articles/webgpu-baseline-2026-three-js-webxr-default) · [fluxnote · AI video](https://fluxnote.io/guides/ai-video-model-pricing-comparison-2026) · [3D AI Studio](https://www.3daistudio.com/3d-generator-ai-comparison-alternatives-guide/how-much-does-ai-3d-model-generation-cost) · [Comfy](https://blog.comfy.org/p/the-8-best-ai-creative-workflow-platforms)
