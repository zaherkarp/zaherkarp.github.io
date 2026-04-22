---
title: "Two States, One Pathogen: A Browser-Side Stochastic SEIRV Simulator"
description: "Methodology and intuition behind the browser-based SEIRV epidemic simulator on this site. Poisson tau-leaping, state-level coverage, and why the ribbon matters more than any single run."
publishDate: 2026-04-22
tags: ["epidemiology", "stochastic-modeling", "seirv", "tau-leaping", "measles", "interactive"]
---

## TL;DR

- **What it does:** The [interactive simulator](/epidemic-simulation/) runs a stochastic SEIRV outbreak in the browser for any two US states, seeded with state-level vaccination coverage for either measles or seasonal flu.
- **Why it matters:** Same virus, same seeds, same population — different coverage. The curves diverge, and the gap between them is what coverage thresholds actually buy you.
- **What the ribbon means:** One stochastic run is not a forecast. A hundred runs, summarized as a median and a 95% band, is an honest picture of the distribution of plausible outcomes.

---

A claim that sounds too strong, but isn't: in one US state a measles introduction smolders out in a week, and in another state two weeks later it has infected thirty thousand people. Same virus, same five index cases, same population. The only difference is the fraction of the population that carries protective immunity. The simulator on this site runs that experiment live, in your browser, using a stochastic compartment model seeded with state-level vaccination coverage data.

This post documents the model, the arithmetic behind the `R_eff` number printed under each curve, and the honest caveats that come with a well-mixed population model.

## The Model

The engine is a discrete-time stochastic **SEIRV** model simulated by **Poisson tau-leaping**. Each person in the simulated population lives in one of five compartments:

- **S** — susceptible
- **E** — exposed (infected but not yet infectious)
- **I** — infectious
- **R** — recovered (immune)
- **V** — vaccinated (immune by prior immunization)

At each short time step \(\tau\), the model draws Poisson random numbers for the count of new exposures, new infections, and new recoveries given the current state, then updates the compartments. We run the same outbreak a hundred times by default and plot the **median** and the **95% band** across replicates. The ribbon is what most matters. A single stochastic run is a coin flip wearing a lab coat; an ensemble of runs is the distribution itself.

## Measles versus Flu

Measles is the most contagious infectious disease in routine circulation. Its basic reproduction number is around 15, meaning that in a fully susceptible population one case seeds roughly fifteen more. The herd-immunity threshold implied by that number is about 93%, which is why MMR coverage in the mid-80s is a genuine public health alarm and coverage above 95% is a hard-won victory.

Seasonal flu sits at the other end. With an R of about 1.5 and a vaccine that prevents roughly 45% of infections in a typical year, flu fades out on its own in small populations more often than not. The interactive makes those statements visual rather than numerical: in a low-coverage state a measles introduction explodes; in the same state a flu introduction usually dies quietly.

Parameters used in the simulator:

| Disease | \(R_0\) | Latent (\(1/\sigma\)) | Infectious (\(1/\gamma\)) | Vaccine efficacy |
|---------|------:|--------------------:|------------------------:|-----------------:|
| Measles | 15.0  | 10 days             | 8 days                  | 0.97 (MMR)       |
| Flu     | 1.5   | 2 days              | 4 days                  | 0.45             |

These are textbook values. Real estimates vary by strain, season, and study, and a defensible range for each is easy to find in the literature; these are chosen because they reproduce the qualitative shape correctly.

## Deterministic Skeleton

The deterministic analog of this model is the standard SEIR ODE with a pre-vaccinated subpopulation:

\[
\begin{aligned}
\tfrac{dS}{dt} &= -\beta\, S\, I\, /\, N \\
\tfrac{dE}{dt} &= \beta\, S\, I\, /\, N - \sigma E \\
\tfrac{dI}{dt} &= \sigma E - \gamma I \\
\tfrac{dR}{dt} &= \gamma I
\end{aligned}
\]

\(V\) is constant. \(N = S + E + I + R + V\). We use frequency-dependent mixing — dividing the hazard by the full population \(N\), including \(V\). Vaccinated individuals do not participate in infection events but they still occupy the mixing pool, so their presence dilutes the per-contact hazard on the susceptibles. **That dilution is the mechanical origin of herd immunity in this formulation.**

## Stochastic Tau-Leaping

The stochastic version replaces each rate with a Poisson-distributed count of events in a short window \(\tau\):

\[
\begin{aligned}
n_{SE} &\sim \text{Poisson}(\beta\, S\, I\, /\, N \cdot \tau) \\
n_{EI} &\sim \text{Poisson}(\sigma E \cdot \tau) \\
n_{IR} &\sim \text{Poisson}(\gamma I \cdot \tau)
\end{aligned}
\]

\[
S \mathrel{-}= n_{SE}, \quad E \mathrel{+}= n_{SE} - n_{EI}, \quad I \mathrel{+}= n_{EI} - n_{IR}, \quad R \mathrel{+}= n_{IR}
\]

Each count is clamped to the current compartment size before applying, so tau-leaping cannot take more people from a compartment than are in it. The integration step is fixed at \(\tau = 0.1\) days, short enough that the Poisson approximation to the event-driven Gillespie trajectory is tight for the \(R\)-values we run.

Why tau-leaping and not an exact Gillespie algorithm? Gillespie is the gold standard — it advances time to the next event — but for a population of \(10^5\) and an \(R_0\) of 15, "the next event" happens roughly every second of simulated time, and running 100 replicates to 180 days inside a Pyodide kernel inside a browser tab is not a fight worth picking. Tau-leaping trades exactness for two orders of magnitude of speedup, and at \(\tau = 0.1\) days the bias is well below the stochastic variance across replicates. The ribbon absorbs it.

## The \(R_{\text{eff}}(0)\) Printed Under Each Curve

The effective reproduction number at the start of the outbreak, given pre-existing vaccinated protection, is:

\[
R_{\text{eff}}(0) = R_0 \cdot \frac{S(0)}{N} \approx R_0 \cdot (1 - \text{coverage} \cdot \text{ve})
\]

That is the number reported under each epidemic-curve plot. It's the single most important thing on the chart.

- **\(R_{\text{eff}}(0) < 1\)** — the outbreak is subcritical in expectation. Fade-out dominates. Most runs never produce an outbreak at all, and the ones that do are small.
- **\(R_{\text{eff}}(0) \approx 1\)** — the dynamics are bimodal. Whether any given introduction takes off is genuinely stochastic: it depends on which way the first few Poisson draws fall. You'll see this in the histogram as a spike at zero and a separate mass at high attack rates.
- **\(R_{\text{eff}}(0) \gg 1\)** — almost every introduction produces an outbreak, and the only remaining question is how large. The histogram concentrates around the \(R\)-dependent final-size threshold.

The measles-vs-flu contrast is essentially this: in the same state, measles lands solidly in the third regime while flu lands in the first or second. One pathogen, one population, one picture of coverage — three different dynamical regimes.

## Reading the Ensemble

The **epidemic curve** shows the number of currently infectious people across the outbreak, per state. The solid line is the median across replicates at each day, and the shaded ribbon is the central 95% band. When two states' ribbons barely overlap, that gap is the signal: their outbreaks really are different, not just noise. When the ribbon is very wide and starts near zero, the state is in the fade-out regime; many runs never produced an outbreak at all.

The **attack-rate histogram** shows the final share of the population that was ever infected, across replicates. A narrow spike near zero means most runs fizzled. A broad mass near the \(R\)-dependent attack-rate threshold means almost every seeded introduction became an outbreak. A bimodal distribution — spike at zero plus mass at high attack rates — is the signature of a pathogen near its takeoff threshold.

The order here matters. Summary → distribution → threshold. Anyone who reports only "the curve" from a single stochastic run and calls it a forecast is reporting one sample from the ribbon.

## Honest Caveats

The model is **well-mixed**. Everyone in a state contacts everyone else with equal probability, which is wrong in ways that matter. Real outbreaks propagate through households, schools, workplaces, and commuting networks, and unvaccinated people cluster within those structures. A state-average coverage of 94% can coexist with schools at 70%, and that is usually where measles outbreaks actually start. A well-mixed model with the state-average coverage will systematically understate the risk in a state with high between-school variance.

The model has no age structure, no waning immunity, no imported cases beyond the initial seed, and no behavior change in response to an outbreak. The coverage numbers are approximate 2022–2023 CDC figures (SchoolVaxView for MMR; FluVaxView for flu) and will drift as new seasons are reported.

Treat the interactive as a **teaching tool** for why coverage thresholds matter — not as a forecast for any particular state. The value it delivers is the shape of the response: how the ensemble changes when you move from 96% coverage to 88%, holding everything else fixed.

## Why a Browser

The simulator runs entirely in the user's browser via [Pyodide](https://pyodide.org/), with [Plotly.js](https://plotly.com/javascript/) rendering the charts. No server, no API, no data leaves the machine. That's partly a privacy posture and partly a statement about what the tool is for: a public-facing explainer that should survive any future of this website — including the future in which there is no server behind it at all — is best built with the scientific Python stack shipped as WebAssembly.

A hundred tau-leaped SEIRV replicates to day 180 for two states completes in a few seconds on a laptop. That's fast enough that the interaction loop — click two states, toggle the disease, run again — feels like an experiment rather than a render.

---

**Try it:** [Two states, one pathogen →](/epidemic-simulation/)
