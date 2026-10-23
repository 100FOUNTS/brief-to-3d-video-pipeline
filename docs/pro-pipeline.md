# The project's pipeline at a professional level (v2): a concrete tool per stage

v1 used generic words ("human editor", "compositor", "hosting and analytics", "several formats"). This version names, at every stage, **the concrete product or model that leads today (15 October 2026)**, the alternatives, **how it is automated** and what we did.

**Done** = complete for this size · **Partial** · **Missing**.
**[P]** official source or measured ranking (Artificial Analysis, Adobe, ACM) · **[S]** blog or comparison (they contradict each other) · **[mine]** my own general knowledge, not verified today · **not researched** = I did not look it up and I do not invent the figure.

**Method warning:** "leader today" means *first in a measured ranking* or *the most cited*, not "what every studio uses". I found no reliable data on what each studio uses; what does exist are published rankings and prices.

```
PREPARE             3D + WEB                                   VIDEO AND SOUND                   CLOSE
1 Brief ─ 2 Script ─ 3 Art ─► 4 Modeling ─ 5 Materials ─ 6 Optimize ─ 7 Viewer ─ 17 Publish ─ 18 Analytics
                              └► 8 Render ─► 9 Video ─ 10 Voice ─ 11 Music ─ 12 Mix ─ 13 Edit
                                              14 Formats and subtitles ─ 15 Review and QC ─ 16 Rights and provenance
19 ORCHESTRATION (runs through everything)
```

## Summary table

| # | Stage | Leader today (tool / AI) | How it is automated | What we use | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Brief | **Claude Opus 5.5** (1st in Artificial Analysis's intelligence index, 58; Sonnet 5.5 is at 56) [P] | Claude API / Claude Code → `brief.json` | `brief.json` written by Sonnet 5.5; no client | Partial |
| 2 | Script and storyboard | Claude Opus 5.5 for the script; **LTX Studio, Boords, Katalist** for the storyboard [S] | Script through the API; storyboard generated from the script [S] | 41-word script, no storyboard | Partial |
| 3 | Art direction | **GPT Image 2.5 Sunburst** (1st in image, 1217) [P]; **Figma Make, Google Stitch, Midjourney, Recraft** [S] | HyperFrames's `/figma` skill imports assets, tokens and components from Figma [P: installed skill] | A 10-color palette + 2 fonts in the brief | Done (basic) |
| 4 | 3D modeling | **Blender 5.2** (from CAD) or generated 3D: **Tripo, Meshy, Rodin** [S] | `bpy` scripts; **Blender MCP** server | Blender by script and by MCP (7 parts) | Done (basic) |
| 5 | Materials and textures | **Adobe Substance 3D** (Painter 12, Sampler with Firefly: text→texture and image→material) [P: Adobe] | Little: the generative features belong to the application and spend Firefly credits | Flat PBR colors | Partial |
| 6 | Optimize 3D for the web | **gltf-transform** (CLI), meshopt or Draco, KTX2 [S] | Command line, fits in CI | Nothing (250 KB without textures) | Missing |
| 7 | Web viewer | **Three.js** (ours), Babylon.js, PlayCanvas; **Threekit** platform [S] | Code in a repository + deployment | Three.js 0.186, 18 tests | Done (basic) |
| 8 | 3D rendering | **Blender Cycles** + color management; render farms [S] | `blender -b` from the command line | Local Eevee, 120 frames in 61 s | Done (basic) |
| 9 | Video | Code engine: **HyperFrames, Remotion, Shotstack, Creatomate**. AI video: **Wan 3.0** (1st, 1174, 12 USD/min), **Seedance 2.5** (1160), **MiniMax H3** (1159, open weights) [P] | CLI and APIs; HyperFrames brings 11 skills for Claude Code | HyperFrames, 20 s at 1080p30 | Done |
| 10 | Voice | **ElevenLabs v4 Turbo** (1st in speech synthesis, 1328) [P] | REST API | Local Kokoro-82M, verified with Whisper large-v3 | Done |
| 11 | Music | **ElevenLabs Music v2.5** (0.15 USD/min; commercial licenses), **Suno v6** (best at vocals), **Google Lyria 3.5** (0.08 USD/song through the API), **Mureka V9** (instrumental), **Stable Audio 3** [S] | ElevenLabs and Google APIs | Music synthesized with numpy | Partial |
| 12 | Mixing and mastering | Voice: **Auphonic** (EBU R128, ATSC A/85). Music: **iZotope Ozone 12**, **LANDR**, **RoEx Automix** [S] | Auphonic and LANDR have a cloud service; **Ozone**: I did not check | FFmpeg: sidechain + `loudnorm` −16 LUFS | Done (automatic) |
| 13 | Editing and color | **Adobe Premiere + Firefly**, **DaVinci Resolve**, **Descript** (text-based editing) [S] | Adobe connector through MCP [S]; I did not try it | Automatic `mux` with FFmpeg | Partial |
| 14 | Formats, subtitles and dubbing | Subtitles: HyperFrames's `/embedded-captions` skill (36 styles, local transcription) [P: skill]. Vertical cuts: **OpusClip, Reap** [S]. Dubbing: **ElevenLabs Dubbing v2**, **HeyGen** (with lip sync), **Rask AI** [S] | HyperFrames derives the aspect ratio from the destination: 16:9, 9:16 (TikTok/Reels/Shorts), 1:1 (feed) [P: skill]; dubbing through the API | A single 1920×1080 MP4, no subtitles | Missing |
| 15 | Review and quality control | Review: **Frame.io**, **Wipster**, **Ziflow** [S]. Technical QC: **Telestream Baton** (not researched) | Frame.io integrates with Premiere and Resolve [S] | 21 own checks + mutants + contact sheets | Partial |
| 16 | Rights and provenance | **C2PA Content Credentials** + invisible watermark (Google's **SynthID**). Art. 50 of the EU AI Act [S] | Sign on export; check that the platform does not strip the metadata [S] | No provenance; model licenses not fully verified | Partial |
| 17 | Publishing | Viewer: **Cloudflare Pages, Vercel, Netlify**. Video: **Cloudflare Stream, Mux, Vimeo** [S] | Deployment through the CLI from CI [mine] | `localhost:5173` | Missing |
| 18 | Analytics | **PostHog, Mixpanel, Amplitude, GA4, Plausible** [S] | SDK in the viewer + events (e.g. "changed the color") [mine] | Nothing (only a dashboard of our own metrics) | Missing |
| 19 | Orchestration | **Claude Code with Opus 5.5**, skills and MCP servers; **n8n + ComfyUI** (ComfyUI is called over REST with `--listen` and `/history/{id}` is queried) [S]. Real case: **Ubisoft**, with agents over USD [P: ACM] | Everything above chained together | `make studio`, worktrees, hooks, subagents | Done (very well) |

## Detail per stage: what it does, where it breaks, what it costs

**1–2. Brief and script.** The most powerful language model in the independent measurement is Claude Opus 5.5 (58 points; Sonnet 5.5, 56) [P]. Opus 5.5 API price: 4 / 20 USD per million tokens (input / output) [P]. For the storyboard I did not measure quality: I only found that LTX Studio, Boords and Katalist exist and generate storyboards from a script [S]. **Prices of the three: not researched.**

**3. Art.** The first in the image-generation ranking is GPT Image 2.5 Sunburst [P]. For interface design, Figma Make and Google Stitch are the ones cited [S]. What can be checked locally: HyperFrames's `/figma` skill, which is already installed, imports whatever is in Figma (assets, tokens, components). **Prices: not researched.**

**4–5. Modeling and materials.** Blender is free. AI 3D generation costs 0.05–0.80 USD per model [S]. Substance 3D: the "image → material" feature **requires the Substance 3D Collection subscription** and everything generative spends Firefly credits; the cheap Steam license (Indie) **does not include them** [P: Adobe and Meshy]. **Price of the Collection: I did not find it.**

**6. Optimize.** A real product goes down from 8–15 MB to 1–2 MB with meshopt or Draco (one of the two) and KTX2 [S]. Free tools; the cost is time.

**7. Viewer.** Custom is free plus time. Threekit: from 999 USD/month up to 30,000–100,000+ USD/year; Vectary, 25–79 USD per user/month (not a configurator) [S]. WebGPU has been standard in all browsers since January 2026 [P].

**8. Rendering.** Render farm: 0.65–9 USD per GPU hour [S]. Our animation: ≈ 0.01–0.15 USD. **Real-time engine (Unreal Engine 5.8) versus Cycles for product: I could not compare them, not researched.**

**9. Video.** By code: Remotion Lambda ≈ 0.02 USD/min; Shotstack 0.20–0.30 USD/min [S]. With AI, the first one (Wan 3.0) costs 12 USD per generated minute [P]; a 20 s clip ≈ 4 USD per attempt. MiniMax H3 has **open weights**, so in theory it could be run locally; **I did not check whether it fits on a Mac with 36 GB**.

**10. Voice.** ElevenLabs: 0.04–0.08 USD per 1,000 characters [S]; our script costs ≈ 0.01 USD. The free tier **does not allow commercial use**; Business, 990 USD/month [S].

**11. Music.** The sources contradict each other and are blogs [S]. What they agree on: Udio ended up limited (downloads turned off after the deal with record labels), ElevenLabs is the most recommended option with a commercial license, Google Lyria is the practical choice through the API. A single source claims that Suno moved to v6 (9 September) and that ElevenLabs launched Music v2.5 (11 September): treat it as unconfirmed. **There is no measured ranking for music: I could not get the Artificial Analysis page.**

**12. Mixing.** Ozone 12: 249–499 USD one-time payment [S]. LANDR: from ≈ 9 USD/month (sources vary) [S]. Auphonic levels with the EBU R128, ATSC A/85 and Apple standards [S]; **I did not verify their exact values or their price**. **Adobe Podcast Enhance: no useful results.**

**13. Editing.** Premiere with Firefly, DaVinci Resolve, Descript. **Prices: not researched.** Our editing was automatic; no color grading.

**14. Formats, subtitles and dubbing.** API prices (August 2026, a single comparison [S]): ElevenLabs Dubbing v2 2.20 USD/min **without** lip sync; HeyGen 2.00 USD/min (fast) or 4.00 (precise) **with** lip sync; Rask 0.78–2.40 USD/min. Subscriptions: ElevenLabs Starter 6 and Creator 22 USD/month; HeyGen Creator 24–29 USD/month; Rask locks it behind the 150 USD/month plan (another source says 60 USD) [S]. For this project, dubbing the 20 s into 2 languages would cost ≈ 1.5 USD with ElevenLabs or ≈ 2.7 USD with HeyGen precision [mine, calculation on prices [S]].

**15. Review.** Frame.io: 15 USD per member/month; Team, 25 USD per member; free tier with 2 members and 2 GB [S]. Wipster: from ≈ 10–12 USD/month for one person (another source says a flat 25 USD/month up to 3 seats; **they do not agree**) [S]. **Automatic VMAF and delivery QC (Telestream Baton): not researched.**

**16. Rights and provenance.** Art. 50 of the EU AI Act requires machine-readable marking of AI-generated content; **it does not name C2PA**, but the Code of Practice uses it as an example alongside an invisible watermark such as SynthID [S]. The sources disagree on the date of application (2 August 2026 for everything, or until 2 December for systems already on the market): **the official text must be consulted**. Maximum fines cited: 15 million euros or 3% of turnover [S]. Adobe Firefly and others already embed C2PA; some platforms strip it on upload [S]. **My current project does not output AI-generated video, but it does use synthetic voice: I do not know whether that falls in scope, it requires a lawyer.**

**17–18. Publishing and analytics.** The names come from the earlier research; **I do not note prices because I do not have them checked today.**

**19. Orchestration.** Claude: Pro 20 USD/month (17 annual), Max 100–200, Team 25–125 USD per seat [S/P]. The n8n lesson: agents without a person approving the steps with external effects fail (one source tells of an agent that sent 47 extra emails); it is an anecdote from a blog, not a measured fact [S].

## What we did and what was missing

| | Stages |
| --- | --- |
| **Done** (8) | 3 Art (basic) · 4 Modeling · 7 Viewer · 8 Rendering · 9 Video · 10 Voice · 12 Mix · 19 Orchestration |
| **Partial** (7) | 1 Brief · 2 Script · 5 Materials · 11 Music · 13 Editing · 15 Review · 16 Rights |
| **Missing** (4) | 6 Optimize 3D · 14 Formats, subtitles and dubbing · 17 Publishing · 18 Analytics |

## Costs together
| Item | What we did | With the most powerful on the list |
| --- | --- | --- |
| Exercise tools | **0 USD** beyond the Pro plan (20 USD/month) | Voice 0.01 USD + music (0.08–0.15 USD) + rendering (≈ 0.15 USD) ≈ **< 1 USD** per piece [mine, sum] |
| If the video were AI-generated | Does not apply | Wan 3.0: ≈ 4 USD per 20 s attempt |
| Dubbing the 20 s into 2 languages | Does not apply | ElevenLabs (no lips): 2.20 × 0.33 min × 2 ≈ **1.5 USD**. HeyGen precision (with lips): 4.00 × 0.33 × 2 ≈ **2.7 USD** [mine, calculation on prices [S]] |
| Fixed subscriptions if one wanted everything | Pro plan 20 USD/month | Claude Max 100–200 + Frame.io 15–25/member + ElevenLabs Creator 22 + HeyGen 24–29 ≈ **160–280 USD/month** [mine, sum of ranges [S]] |
| People (brief, script, art, editing, review, legal) | The author and Claude | **Not researched; I do not invent figures** |

## What remains unresearched
Prices of storyboard, Premiere, Resolve, Descript, Substance Collection, hosting and analytics; the music ranking; Unreal Engine 5.8 versus Cycles; automatic delivery QC (VMAF, Baton); Claude Agent SDK or Temporal in creative production; what each studio really uses.
