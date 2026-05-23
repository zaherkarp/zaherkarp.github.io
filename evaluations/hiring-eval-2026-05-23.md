# Hiring evaluation of `./index.html`

Generated: 2026-05-23
Iterations: 1
Changes applied: no (APPLY_CHANGES=false)

---

## Decision summary

| Evaluator | Role context | Depth | Decision | Level read |
|-----------|--------------|------:|---------:|------------|
| First-impression scanner | Unknown role (pure first glance) | 10s | **ADVANCE** | Senior IC or first-line manager in healthcare data, specifically the CMS/Medicare quality-measurement corner |
| Recruiter screen | Mid-to-senior healthcare data | 60s | **ADVANCE** | Recently-promoted first-line manager with deep IC chops and 7+ years of healthcare data work; solid mid-to-senior IC, credible early-stage manager, not yet a director |
| Executive fit check | Senior-to-director | 60s | **HOLD** | Strong senior IC / tech lead who has just started managing, with unusual craft but no director-level scope evidence |
| Healthcare analytics manager HM | Healthcare Analytics Manager role | 5min | **HOLD** | Strong senior IC who recently stepped into a manager title; methodology real, people-management evidence functionally absent |
| Director-level HM | Director of Data Analytics / Engineering | 5min | **PASS** | Strong senior IC / first-line manager; the work is good, the level is wrong |
| Senior/Staff IC HM | Senior or Staff Data Engineer | 5min | **HOLD** | Engineering Manager with strong recent hands-on writing, not a Staff IC who's been shipping production data infrastructure at scale |
| Peer engineer | Technical credibility | 5min | **ADVANCE** | Senior IC with credible manager promotion; depth signals concentrated in the Stars/Medicare lane and thinner outside it |
| Healthcare domain expert | Domain credibility | 5min | **ADVANCE** | Real practitioner with hands-on Stars/HEDIS production experience; portfolio prose abstracts away from specific measures and CMS algorithms |

**Convergence and divergence.**

- **Depth-symmetric ADVANCE:** the 10s scanner and the 60s recruiter both advance; the meta + h1 + subtitle + stack lines do enough work to clear the funnel's first two stages.
- **Lens divergence at 60s:** recruiter ADVANCE, executive HOLD. The page reads as a credible candidate to a checklist-driven recruiter and as an under-scoped one to an executive looking for leadership signal.
- **Role-specific HMs all gate (HOLD or PASS):** manager-track HOLD, director-track PASS, Staff-IC-track HOLD. Three different role contexts, three different "this doesn't quite fit my req" reactions, for three different reasons.
- **Credibility-only evaluators both ADVANCE:** peer engineer and healthcare domain expert both clear the bar. The page's technical and domain claims survive expert scrutiny — what fails is role calibration, not credibility.

The page is in the funnel. It does not fall out of the funnel anywhere. But for every role-specific HM the answer is "want to talk before deciding," not "schedule the loop."

---

## Per-evaluator critiques

## First-impression scanner, Unknown role (pure first glance), 10 seconds

### What hit me in my reading window
- Browser tab and title (line 5): "Zaher Karp, Healthcare Data Engineering." Named person + specific discipline. Not "Data Professional," not "Engineer | Analyst | Storyteller." Clean.
- Meta description (line 6): "15+ years... regulated healthcare. Medicare Star Ratings, HEDIS pipelines, data integration across claims and eligibility sources." Specific verticals, specific artifacts. Reads like someone who has actually shipped this stuff.
- JSON-LD (lines 30-62): "Manager of Data Science & Engineering" at "Baltimore Health Analytics," UW-Madison alum, knowsAbout list mixes domain (HEDIS, CMS, VBC) with tools (dbt, SQL, Python, AWS). Coherent.
- sameAs (lines 57-61): LinkedIn + GitHub + ResearchGate. The ResearchGate link is a small but meaningful signal, this person has published.
- Custom ETBook @font-face (lines 76-89) with a Tufte-lineage comment. Whoever owns this site cares about typography to a level most candidates don't. Visual seriousness signal before I've even seen the body.

### What I expected to see but didn't
- No hero h1, subtitle, or any visible body content in my window. Everything I have is meta and CSS prelude. For a 10-second scan that's a structural risk; if the head is this long, the above-the-fold paint may be slower than expected.
- No OG image preview that I can evaluate, just a default path. Can't judge whether the social share would draw a click.
- No location/availability hint anywhere in the meta. Recruiter-relevant.

### Red flags or hesitation points
- Bing verification TODO comment left in production HTML (lines 13-16). Tiny, but a gatekeeper notices "REPLACE_WITH_TOKEN" and pattern-matches "unfinished."
- "15+ years" in the description is the kind of phrasing that pings as resume-ese; the rest of the line saves it, but it's the weakest phrase in the otherwise specific copy.
- I never reached an h1 or a hero in 90 lines. A first-impression visitor sees a rendered page, but the depth of the head suggests a designed page rather than a punchy one, fine for a careful reader, risky for a 10-second scan.

### Level read
Senior individual contributor or first-line manager in healthcare data, specifically the CMS/Medicare quality-measurement corner.

### Decision
ADVANCE. The title, description, and JSON-LD are specific enough and credentialed enough (named employer, named university, publications, a real tool stack) that I'd give this 60 more seconds.

### What would change my mind
If the above-the-fold I can't see turns out to be a wall of generic "passionate technologist" prose, a buzzword cloud, or another restatement of "15+ years in healthcare data," the credit I'm extending from the meta evaporates fast. Conversely, a single concrete artifact visible on first paint, a named project, a measurable outcome, a chart that reads in two seconds, would convert ADVANCE into "schedule a conversation." The TODO comment should also come out of production before a more cynical reviewer sees it.

---

## Recruiter screen, Mid-to-senior healthcare data, 60 seconds

### What hit me in my reading window
- Title tag and h1 land cleanly: "Healthcare Data Engineering" and the subtitle "Healthcare data engineering and Medicare Advantage analytics" — domain matches my req on first paint.
- Current role surfaces fast and reads senior: "Manager of Data Science & Engineering, Baltimore Health Analytics, Nov 2025 to Present (promoted from Lead Data Engineer, April 2026)." Promotion-in-place is a stability signal I like.
- Stack lines are present per role and parse instantly — current role: "pandas · scipy · numpy · dbt · SQL · Selenium · Python." Health Catalyst stack: "dbt · Redshift · AWS to Azure · Databricks · Python · Tableau · Power BI." Hits a lot of my checklist boxes.
- Keyword density on domain: Medicare Star Ratings, HEDIS, CMS, RxNorm, Epic, Cerner, athenahealth, Veradigm, HIPAA, HITRUST. This is core healthcare, not adjacent.
- Tenure pattern reads clean: healthfinch Dec 2017 to Jul 2020, Health Catalyst Aug 2020 to Aug 2025 (acquisition continuity, not a job change), BHA Nov 2025 to present. Plus 9 years at UW-Madison before that. No job-hopping.

### What I expected to see but didn't
- No headline "Years of experience" number near the h1. The meta description says "15+ years" but I didn't see that surfaced visually on the page in my scan window.
- No team size on the current manager role. "I lead a data function" and "spans direct management, code review, coordination across two geographies" — but how many ICs? Recruiters and HMs ask this in the first screen.
- No location anywhere I caught. Baltimore Health Analytics name implies Baltimore, but the margin note says "Madison WI." Remote/hybrid/onsite is unanswered.
- No cloud certifications, no explicit mention of Snowflake, Airflow, or Spark (Databricks is there, which partially covers it). If my req is Snowflake-specific I bounce here.

### Red flags or hesitation points
- Lead Data Engineer to Manager "promoted April 2026" with a current date of 2026-05-23 means the manager title is six weeks old. That's a real promotion, but it's fresh, and for a senior manager req I'd want to confirm scope.
- "Manager of Data Science & Engineering" at a company I haven't heard of (Baltimore Health Analytics) — small-shop manager titles inflate. I'd need to verify the headcount.
- First two experience entries are heavy on methodology prose (Huber psi-function, robust exponential smoothing, medallion architecture). At 60 seconds this reads as substantive, but a less-patient screener could call it academic.
- Long editorial/writing past (Sustainable Clarity 2007-2014, "wrote articles syndicated through Thomson Reuters") plus 9 years academic research is a non-traditional path into data engineering. Some HMs will read this as "career-changer who got there late," even though the timeline says otherwise.

### Level read
Reads as a recently-promoted first-line manager with deep IC chops and 7+ years of healthcare data work post-research — solid mid-to-senior IC, credible early-stage manager, not yet a director.

### Decision
ADVANCE. Domain, stack, tenure, and current title all clear my screen; the page surfaces what I need to make a 60-second call.

### What would change my mind
If my req is specifically a Senior Manager or Director with 5+ direct reports owning P&L or a multi-team org, I'd downgrade to HOLD pending a recruiter call to confirm team size and scope at BHA — the manager title is six weeks old and the page never states headcount under management. Conversely, if my req is a senior IC data engineer on Snowflake/Airflow, the dbt/Redshift/Databricks profile is close but not exact, and the management framing might over-shoot what the role wants; I'd want to know whether they'd take an IC role after just being promoted. A one-line "team of N across US and [geo]" near the BHA role title, plus location and work-mode, would resolve both branches without a call.

---

## Executive fit check, Senior-to-director level, 60 seconds

### What hit me in my reading window
- Title is "Manager of Data Science & Engineering" at Baltimore Health Analytics, with a Nov 2025 start and an April 2026 promotion from Lead Data Engineer noted parenthetically. That reads as roughly six months in seat at the manager level, in a company I don't recognize.
- The whole page is visually disciplined Tufte cream + ETBook + hand-drawn SVG charts (career arc, dot plot, Stars cliff density curve). It signals craft and taste, which is rare. It does not signal scale.
- About lead is reflective and methodological ("the methodological thread runs from grounded theory ... through time series analysis in Stars forecasting"), framing identity around technique, not outcomes. The one leadership line, "I lead a data function, because the decisions I want to influence happen above the individual contributor level," reads as aspirational rather than evidenced.
- Experience prose is consistently first-person tactical: "I built it under HIPAA and HITRUST," "RxNorm validation ... cut client-audit discrepancies from roughly 30% to under 5%," "ROI modeling ... supported over a million dollars in recurring revenue." Concrete, but the dollar figure is small and the framing is IC-with-a-team rather than function-owner.
- Projects section is six items, two featured. Stars Cliff Simulator is a public teaching demo, the rest are GitHub side projects or blog posts. No enterprise system, no team-built platform, no "we shipped X to N customers."

### What I expected to see but didn't
- Any quantified team or org scope at the current role: how many reports, what budget, what P&L or revenue line the function supports. "Direct management" and "two geographies" is the most I get.
- Strategic framing of impact at the Health Catalyst chapter (Aug 2020 - Aug 2025, five years, the longest tenure). I get "RxNorm validation" and "migrating infrastructure from AWS to Azure" but no platform-level outcome, no customer count, no retention or ARR signal, no cross-functional leadership story commensurate with five years.
- Thought leadership beyond the personal blog. Publications and speaking are entirely 2010-2019 academic, predating the data-engineering chapter. No industry conference talks (HIMSS, RISE, Stars Summit), no podcasts, no LinkedIn presence cited, nothing post-2019 in the formal record.
- A "what I'm building / what I believe" surface. The page is a portfolio, not a point of view. For a director-track candidate I want to see opinions about Stars, MA, HEDIS architecture that I can disagree with.

### Red flags or hesitation points
- Title trajectory is light for the level. Two manager titles back-to-back (Healthcare Analytics Manager, Specialist at healthfinch; Healthcare Analytics Manager, Embedded Refills at Health Catalyst), then a Lead Data Engineer step at BHA, then a six-month promotion to Manager. That's competent but doesn't show director-level scope progression across 8 years in industry.
- "Promoted from Lead Data Engineer, April 2026" with a Nov 2025 start = promoted at ~5 months. That can be a great signal or a small-company signal. With Baltimore Health Analytics being a name I don't know, I lean toward the latter without more.
- The italicized formula in the Experience section (Huber's psi-function) and the inline grounded-theory sidenote read as someone signaling "I am intellectually serious." For a hands-on senior IC role that's a plus. For a director where I need political and organizational range, it's neutral-to-mildly-concerning.
- Academic publication record is genuinely impressive but all pre-2020. Combined with no post-2019 industry talks, the public thought-leadership signal has a five-plus year gap.

### Level read
A strong senior IC / tech lead who has just started managing, presenting with unusual craft and methodological depth but without the scope evidence of someone who has run a function at director level.

### Decision
HOLD. The craft and substance are real, but nothing on this page demonstrates director-level operating scope, and the manager title is six months old at a company I'd need to size.

### What would change my mind
A clearly stated current-role scope line: team size, the systems or contracts the function owns, the business outcome it's accountable to. One concrete five-year outcome from the Health Catalyst tenure framed at platform or customer level, not pipeline level (clients served, ARR supported, measure rates improved across N plans). Any post-2020 external thought-leadership signal: a RISE/Stars Summit talk, a guest podcast, a widely-shared LinkedIn essay, a named industry working group. If two of those three exist and just aren't surfaced here, I move to ADVANCE for a screen. If the current scope is genuinely "small function at a small company, less than ten total people," I move to PASS for a director seat and reconsider for a senior IC or founding-data-lead role.

---

## Healthcare analytics manager hiring manager, Healthcare Analytics Manager role, 5 minutes

### What hit me in my reading window
- The Stars/HEDIS methodology depth is unusual for a portfolio. The Huber psi-function formula sitting visible in the BHA entry (lines 1881-1892), the line about CMS Technical Notes "hundreds of pages" requiring round-tripping through analytics without drift (sidenote at 1860), and "30% to under 5% audit discrepancy" (line 1912) all read as someone who has actually been in the spec. That is rarer than it should be.
- The cross-EHR claim is concrete and defensible. Epic, Cerner, athenahealth, Veradigm with the explicit "medication adherence rate is not portable" sidenote (line 1912) is the kind of statement a fake-it manager doesn't write. The acquisition-driven AWS-to-Azure-to-Databricks migration on the same entry is a real-shaped migration story.
- The compliance-as-architecture frame around the client-side Stars predictor (BHA fold, line 1900, plus the linked blog post in the Writing section) is a strong signal. The reasoning "browser-side compute sidesteps the data-transit review a server-side version would trigger" is the kind of trade-off articulation I want my managers making for me.
- Star Ratings Cliff Simulator (project 01, lines 1998-2128) being a working public demo with a methodology post backing it is the rare portfolio artifact I can actually go poke at. Ordinal logistic regression calibrated to CMS 2025 weights, client-side, is a concrete teaching artifact, not a screenshot.
- Writing cadence in the last week is conspicuous: 6 posts between May 17 and May 20, 2026, mostly on CI/CD for SQL developers (lines 1779-1826). Either he is teaching downward to engineers or he is interviewing. Probably both. Either way it tells me how he thinks about leveling up ICs.

### What I expected to see but didn't
- **No headcount, no span of control, no direct-report number anywhere.** The BHA "Manager of Data Science & Engineering" entry (line 1852) says "I lead the data engineering and analytics methodology function" and "coordination of data science and QA across two geographies." It never says how many people, how many directs, what the org chart looks like. The Health Catalyst entry (line 1908) is titled "Healthcare Analytics Manager, Embedded Refills and Care Gaps" but the prose under it (1911-1923) is entirely about platform, RxNorm, governance. Not one named person managed. For a manager role this is the central absence.
- **No hiring, firing, performance management, or conflict story.** The healthfinch entry (lines 1929-1943) says "Promoted to manager after one year to lead cross-functional work across product, engineering, and customer success" and stops. The fold (1936-1941) is about ROI modeling and dashboards. The messy parts of managing — backfilling a departure, putting someone on a PIP, mediating a product-engineering fight, a vendor that missed an SLA — none of it is here.
- **No upward-management evidence.** Plenty of CMS-to-engineer translation. Nothing about board reports, exec readouts, contract-level conversations with payer clients, or how he prioritizes against a product roadmap. The line at 1856 mentions "coordination of … the product roadmap and translation between CMS requirements and organizational priorities" but it's stated, not demonstrated.
- **The testimonials don't testify to management.** Both quotes (lines 2505-2529) are about Zaher as an IC: "thoughtful, high-quality work," "the only engineer on the team," "delivered high-quality work … intelligent, thorough." Joanna Laucirica is Director of Customer Operations and Jessica McCay is Director of Customer Success — both are downstream consumers of his work, not people he managed or peers who watched him manage. No testimonial from a direct report, a peer manager, or his own manager.

### Red flags or hesitation points
- **Title inflation suspicion at BHA.** Line 1853 says "Nov 2025 to Present (promoted from Lead Data Engineer, April 2026)." Read literally: he started Nov 2025, was promoted from Lead Data Engineer in April 2026, and the page is dated May 2026. That's roughly six months in seat and one month into the management title. Calling it "Manager of Data Science & Engineering" in the h1 metadata and JSON-LD (lines 31-64) when he just got there is the kind of self-presentation choice that makes me want to ask his prior manager what actually happened.
- **The Health Catalyst title is "Healthcare Analytics Manager, Embedded Refills and Care Gaps" but the prose is solo-engineer-shaped.** Testimonial from Jessica McCay (line 2520): "Despite being the only engineer on the team, Zaher consistently delivered high-quality work." That contradicts the manager title or at least narrows it severely — he was managing-the-work, not managing-people. Five years in a "Manager" title that may have been individual contributor work in practice is exactly the pattern that produces a bad manager hire.
- **Methodology references skew academic-old.** The publications (lines 2345-2450) top out in 2019 with 24 citations on a 2014 paper. The dot plot figure (lines 1507-1612) explicitly visualizes "cessation after transition to industry." Fine on its own, but combined with the Star Ratings claims being entirely self-attested with no client name, no scale, no contract-count, the depth signal is mostly the formula and the sidenote. I'd want him to walk me through one production Star Ratings pipeline at the whiteboard before I believed it.
- **Project 02 (Healthcare Workforce Transition Platform / SkillSprout) and the four index tiles are thin.** GitHub repos exist (and I'd click them in a real screen) but the prose on the page for ECDS Shock Index and Medicare Advantage Insight Engine tiles (lines 2287-2310) reads as side-project-shaped. None of them demonstrate "managed a team that built this." They look like things he built solo to stay sharp.

### Level read
Strong senior IC who recently stepped into a manager title and is presenting himself for the next manager job; the methodology and translation skills are real, the people-management evidence is functionally absent.

### Decision
HOLD. The methodology depth and writing cadence are strong enough that I want a screen, but I won't advance to a hiring loop until I hear concrete management stories.

### What would change my mind
A 30-minute screen where he walks me through: how many people report to him today and what their roles are; the last time he hired (what the loop was, who he passed on and why); the last time he had to performance-manage someone out or onto a PIP; a vendor or partner conflict he owned end-to-end; and one example of translating a Star Ratings methodology change into a sprint plan with named engineers and dates. If those answers are concrete and the headcount is real (3+ directs, not "I led a function"), I move to ADVANCE. If the answers are abstract or the headcount turns out to be one or two people he coordinated with rather than managed, this is a PASS for the manager role but I might keep him in mind for a senior IC track.

---

## Director-level hiring manager, Director of Data Analytics/Engineering, 5 minutes

### What hit me in my reading window
- The current title is "Manager of Data Science & Engineering" at Baltimore Health Analytics (line 1852), promoted from "Lead Data Engineer" in April 2026. Six months in the manager title, off an IC role. That is a manager-of-ICs scope at best.
- Every preceding title is also "Manager" or "Analytics Manager, Specialist." Three consecutive manager titles, none with the word Director, Head, or VP, and none with a stated headcount or budget. The career arc never passes through a director-prep crucible.
- The Health Catalyst entry (line 1908) describes a five-year manager tenure inside a substantial company but the prose is entirely about the work, not the org: "RxNorm validation cut client-audit discrepancies from roughly 30% to under 5%," "migrating infrastructure from AWS to Azure." This is senior-IC-with-coordination prose, not org-building prose.
- The healthfinch entry (line 1932) explicitly says "First analytics hire" and "Promoted to manager after one year to lead cross-functional work across product, engineering, and customer success." Cross-functional, but as the analytics function of one, then a function of three (line 1912: "three-person analytics function"). Three people is a team, not an org.
- About-section line 1487 reads: "I lead a data function, because the decisions I want to influence happen above the individual contributor level." That is the sentence of someone reaching for the next level, not someone speaking from it. A director would phrase it as the work, not the aspiration.

### What I expected to see but didn't
- A headcount number, anywhere. Not "managed a team of N," not "grew the function from X to Y," not "hired N engineers across two managers." The page is silent on org scale. For a director role asking to manage 20-40 across multiple managers, this absence is dispositive.
- Any evidence of managing managers. The Health Catalyst fold mentions code review, governance, EHR-specific work — all peer-of-engineer or manager-of-engineers framing. No "my managers," no "skip-levels," no "leveling rubric I rolled out."
- Budget ownership or P&L exposure. The healthfinch fold (line 1939) gestures at "over a million dollars in recurring revenue" the ROI work supported, but that's revenue influence as an analyst, not a budget the candidate owned.
- Hiring at scale, performance management of leaders, org design, function rebuild narrative. None of it. The closest is "first analytics hire" at healthfinch, which is the opposite signal: this is someone who has been the function, not someone who has built and run one.
- External thought leadership at the strategic level. There are six pubs (newest 2019, line 2417) and 17 talks (all 2010-2017, line 2469). Academic output ceased seven years ago. The blog is prolific recently (six posts in May 2026 alone, lines 1779-1825) but the titles are all tactical engineering pieces — "CI/CD for SQL Developers," "Compliance as Architecture," "expand, migrate, contract." That is senior-engineer voice, not director voice. I would expect "How I rebuilt the analytics function at..." or "Hiring rubric for healthcare data engineers" before I'd believe director-level external presence.

### Red flags or hesitation points
- The promotion timeline at BHA is suspicious for level claim. April 2026 promotion to Manager, this is May 2026. Six weeks. If they are positioning for a Director external move six weeks after their first Manager title, the title aspiration is racing ahead of the experience. This is the textbook bad-hire pattern I underwrite for.
- The Sustainable Clarity entry (line 1971) says "Managed up to eight copy editors, graphic designers, and photographers" — the largest reported span in the entire document is from a 2007-2014 editorial services practice, not from anything in healthcare data. That is not transferable management experience to a 20-40 person director seat.
- The Huber psi-function block (line 1881) and the medallion-architecture sidenote (line 1918) are signals of someone who wants to be read as a deep practitioner. Both are correctly proud-of-the-craft signals for a senior IC or a tech lead. A director candidate showing me a piecewise psi-function on the homepage in 2026 is telling me where their identity actually sits.
- "Manager of Data Science & Engineering" at a company small enough that its name doesn't show up in any of the testimonials, project list scale, or org-size markers. BHA could be five people or fifty; the page never says. Given the 2025 founding implied by "Nov 2025 to Present," I assume small. Director of a small thing is not director of a large thing.

### Level read
Strong senior individual contributor or first-line manager with five years of competent execution; the title page, the writing voice, and the org-scope evidence all read at the manager-of-ICs level, not the manager-of-managers level the search needs.

### Decision
PASS. The candidate is mis-leveled for this role and would be a six-to-twelve-month bad hire of exactly the type I have made before; the work is good, the level is wrong.

### What would change my mind
A real conversation in which the candidate could quantify span of control today (people, managers reporting to them, budget) and walk me through a concrete instance of building or rebuilding an analytics function — hiring plan, leveling rubric, performance calibration, a manager they coached out, a re-org they led. If the BHA role is in fact a player-coach seat at a 30-person company and they are actually running engineering and analytics there with managers underneath, the page is dramatically underselling and I'd reconsider. Absent that, the trajectory is a strong manager of small teams and the next sensible step is a senior-manager or director seat at a company where the function is still being built from the floor, not a director seat over 20-40 with multiple managers. I'd advance them for an Analytics Manager or Senior Manager role today without hesitation; for Director, I need one more crucible role first.

---

## Senior/Staff IC hiring manager, Senior or Staff Data Engineer role, 5 minutes

### What hit me in my reading window
- Current title is **Manager of Data Science & Engineering** (line 1852), promoted from Lead Data Engineer in April 2026. The subtitle and h1 frame this as engineering, but the role chain is consistently "Manager" or "Healthcare Analytics Manager" across the last three jobs (lines 1908, 1929). That's a manager career, not an IC career, regardless of how the title reads.
- The Writing section is genuinely active and technical right now: six posts between 2026-05-17 and 2026-05-20 (lines 1779-1825), and the topical center is CI/CD for SQL developers, schema migrations (expand/migrate/contract), and compliance-as-architecture. That's hands-on practitioner content, not management thought leadership. This is the strongest signal on the page.
- The featured projects have inspectable artifacts. Stars Cliff Simulator has a live demo (`/star-rating-predictor/`, line 2123) and methodology post, stack listed as ordinal logistic regression in vanilla JS, no deps. SkillSprout has a GitHub repo (line 2256) with FastAPI/PostgreSQL/scikit-learn. Both small-multiple tiles (Medicare Advantage Insight Engine, ECDS Shock Index) also link to GitHub repos (lines 2292, 2305).
- The Huber psi-function block (lines 1881-1892) sitting inside the BHA experience entry, with the sidenote about robust exponential smoothing for Stars time-series forecasting (line 1860), is the cleanest "I still know what I'm doing under the hood" signal in the Experience section. It's specific, falsifiable, and tied to a real production problem.
- BHA fold mentions a client-side Stars rating predictor where cut-point projection runs in-browser so member-level data never transits (line 1900), and there's a 2026-05-19 blog post titled "Compliance as Architecture" (line 1798) that's apparently the methodology essay for it. That's an architectural decision with a defensible "why," which is what I want from Staff.

### What I expected to see but didn't
- No production data-engineering system at scale described with numbers I can pressure-test. The BHA section talks about "translating regulatory text into executable Python and SQL" (line 1860) and the Health Catalyst entry mentions "AWS to Azure and Databricks" migration (line 1912) and "medallion architecture" in a sidenote (line 1918), but no volumes, latencies, SLAs, schema counts, or pipeline DAG sizes. For a Staff role I want one paragraph that proves the person has actually owned a 10TB+ warehouse or a multi-hundred-model dbt project.
- No dbt project depth despite dbt appearing in two stack lines (1904, 1925) and the knowsAbout JSON-LD. No mention of model count, test coverage, exposures, semantic layer, or anything that would distinguish "used dbt" from "led a dbt program." Same for Databricks, Redshift, and the Azure migration: named but not detailed.
- No system-design write-up. The blog titles are good practitioner pieces (CI/CD for SQL, schema migration patterns) but I don't see a "here's how I designed and rolled out X across N teams" essay. Staff candidates usually have at least one.
- No code in the featured project stacks that I'd consider modern data-engineering tooling. The two featured project stacks are vanilla JS / FastAPI + scikit-learn. The tiles are Python + webhook, Python + Stars methodology, Stata + SAS (interrupted time series), and linear regression + Sisense + Epic Clarity. Nothing about streaming, orchestration (Airflow/Dagster/Prefect), warehouse-native transforms at scale, or event-driven pipelines.

### Red flags or hesitation points
- Every post-2017 role is titled "Manager." The page tries hard to reframe this as IC work ("I lead a data function, because the decisions I want to influence happen above the individual contributor level," line 1487), which actually concedes the point: this person has chosen management over IC for nine years. The April 2026 promotion was *to* Manager, not away from it.
- Half the publications and the entire UW research arc are 2009-2019 (lines 1947-1965, 2345-2449). The peer-reviewed work is healthcare services research with Stata/SAS/NVivo/SPSS/REDCap (line 1967), not data engineering. Useful context, but it's eating real estate that a Staff candidate would use to demonstrate engineering scope.
- The featured projects are good for a personal portfolio but read as side projects, not production work. The Stars Cliff Simulator is explicitly "a public demo" (line 2003); SkillSprout is FastAPI plus a logistic regression on O*NET data. The real production system at BHA (the client-side Stars predictor) is described but not inspectable, by design. For a hiring filter that's a wash: I'll have to take it on faith.
- Stack lines lean dated and shallow. "pandas · scipy · numpy · dbt · SQL · Selenium · Python" (line 1904) for the current role is a generic Python data-analyst stack with dbt sprinkled in; Selenium for web automation reads as a workaround, not a platform choice. The Stata/SAS/NVivo/SPSS/REDCap line (1967) and "Sisense · Epic Clarity · SQL" (2332) underscore the trailing-edge tooling.

### Level read
Reads as an Engineering Manager with strong recent hands-on writing and a credible compliance-architecture instinct, not as a Staff IC who's been shipping production data infrastructure at scale.

### Decision
HOLD. The recent writing cadence and the Huber/compliance-architecture depth are real, but the title trajectory and the absence of production-scale system-design evidence don't clear the Staff bar; I'd want a 30-minute call before deciding between Senior IC and pass.

### What would change my mind
A 30-minute deep-dive on one production system at BHA or Health Catalyst, with the engineering director listening for: pipeline scope (model counts, data volumes, freshness SLOs), how the candidate made architectural calls without formal authority on cross-team work, and a walkthrough of the client-side Stars predictor's threat model and failure modes. If the answers are concrete and the candidate visibly defaults to IC framing under technical pressure, advance for Senior with a Staff conversation contingent on a system-design loop. If the answers stay at the "I led a function" altitude, pass; the page is then accurately representing a manager who writes well, not a Staff IC.

---

## Peer engineer, Technical credibility evaluator, 5 minutes

### What hit me in my reading window
- The Stars Cliff Simulator (Project 01) names a specific methodology ("ordinal logistic regression calibrated to CMS 2025 weights") and has a live demo plus methodology post link. The "no data leaves the user's machine" architecture isn't just claimed in the project card, it's restated as a thesis in the linked blog post "Compliance as Architecture: A Stars Rating Predictor That Never Sees Member Data" (writing entry 2026-05-19). Two surfaces telling the same story consistently is a credibility tell.
- The Huber psi-function block in the BHA experience entry (lines 1881-1892) is rendered inline with a caption that explains *why* it's there ("a single COVID-era shock cannot dominate the smoothing parameter estimates"). That's a real motivation, not formula-as-decoration. Whoever wrote that caption has thought about robust loss functions in a specific operational context.
- Health Catalyst entry (line 1912): "RxNorm validation across the platform cut client-audit discrepancies from roughly 30% to under 5%." Concrete before/after numbers, scoped to a specific normalization problem across four named EHRs (Epic, Cerner, athenahealth, Veradigm). The "roughly" hedging on the 30% reads as honest measurement rather than rounded marketing.
- The medallion architecture sidenote (line 1918) makes the right framing call: "The redesign was an auditability and governance decision, not a performance one. Same-day runtime was a side effect of the design, not the goal." That's a senior signal. Junior engineers brag about the perf win; people who've actually shipped governance work know it's the audit trail that matters and lead with that.
- Writing cadence is real and recent. Six posts in three days (2026-05-17 through 2026-05-20), four of them a coherent "CI/CD for SQL developers" series. Either this is someone actively thinking out loud about a domain they work in, or someone front-loading their portfolio right before a job hunt. The series structure (commits → pipelines → schema changes → observability) is the right curriculum for the audience.

### What I expected to see but didn't
- Inspectable code for the Stars work. The headline project (Stars Cliff Simulator) is a "live demo" but I see no GitHub link for it on this page. The two repos that *are* linked (medicare-advantage-insight-engine, ecds-shock-index) are the small-multiple tiles, not the featured pieces. For "ordinal logistic regression in the browser, no dependencies," I want to read the JS. Without it, I'm trusting that the math under the demo matches the claim.
- The SkillSprout repo link points to github.com/zaherkarp/skillsprout but the project card describes "FastAPI, PostgreSQL, scikit-learn, logistic regression, O*NET" with no inspectable artifact on this page beyond the link. Sankey diagram numbers are explicitly labeled "Illustrative shares" in the caption, which I respect, but it means the figure is a teaching diagram, not a model output. I'd want to see one real run on real O*NET data.
- dbt is in three stack lines (BHA, Health Catalyst) but never described in the prose. No mention of model layering decisions, test coverage, exposures, snapshots, dbt-utils vs custom macros, or how dbt slotted into the Databricks/Redshift transitions. For someone listing dbt on two roles, the absence of any opinion about it is notable.
- The healthfinch entry (line 1939) claims "sevenfold growth in internal user adoption and eliminated four hundred hours of annual manual reporting preparation" but it's hidden inside a "More detail" fold and unbacked by any methodology. The 7x number is the kind of thing I'd ask about in an interview because the denominator matters a lot.

### Red flags or hesitation points
- The prose across blog summaries reads very smooth and very consistent in voice ("The pipeline shipped the change. Friday morning the dashboard went red. Observability closes the loop."). Short declarative sentences, parallel structure, no rough edges. This pattern repeats across all six recent writing entries. Could be a deliberate house style; could be LLM-assisted polish. I can't tell from the homepage alone, and that itself is the concern.
- The medallion architecture sidenote (line 1918) is correct-sounding but generic: "bronze for raw ingestion, silver for documented business logic, gold for analytic output. Every transformation has a name, a location, and a test." That's the Databricks marketing page definition. I'd want one specific story: which silver-layer model caused the most pain, what test caught what bug, what they wish they'd done differently. Without that, it's vocabulary not experience.
- "Robust exponential smoothing for time series forecasting" with the Huber formula is well-presented, but Huber's psi is the standard textbook robustification. Pairing it with "scipy and numpy" rather than naming a specific implementation (statsmodels? a custom Kalman filter? PyMC?) leaves the actual model under-specified. For Stars forecasting against CMS Technical Notes the implementation choices matter and I'd press on them.
- The Selenium mention in the BHA paragraph (line 1860) sits in a list alongside pandas/scipy/numpy with no context. Selenium-for-Stars-work usually means scraping HPMS or display pages because CMS doesn't expose machine-readable feeds. If that's what it is, say so; otherwise it looks like an odd tool to leave undefended in a paragraph otherwise about regulatory text translation.

### Level read
Senior IC with credible manager promotion, with the depth signals concentrated in the Stars/Medicare lane and thinner outside it.

### Decision
ADVANCE. The Huber motivation, the 30%-to-5% RxNorm result, and the matched architecture-to-blog story on the client-side Stars predictor clear the bar for a deeper conversation.

### What would change my mind
A 30-minute look at the Stars Cliff Simulator's actual JS source (or the methodology blog post, which I haven't navigated) would resolve most of my hesitation: either the ordinal logistic implementation is real and the calibration to CMS 2025 weights is defensible, in which case the rest of the credibility rises with it, or it's a hand-rolled approximation dressed up in regression vocabulary, in which case the gap between the Huber-formula presentation and the actual modeling work becomes the story. Same test for one BHA artifact, even sanitized: a single dbt model layout, one test failure post-mortem, one Technical Notes change they had to round-trip through their analytics layer. The page promises depth in specific places (the formula, the medallion sidenote, the compliance-as-architecture thesis) and I want to verify the depth is uniform underneath the polish, not concentrated at the surfaces that catch the eye.

---

## Healthcare domain expert, Domain credibility evaluator, 5 minutes

### What hit me in my reading window
- **The 4.0 QBP cliff framing is correct and specific** (lines 2003, 2034). Calling out "at the 4.0 QBP threshold, a tenth of a star is worth $50 million" is the right mechanism: QBP (Quality Bonus Payment) eligibility, county benchmark uplift, 5% bonus applied through bid-to-benchmark, the whole regulatory machinery hangs on that ≥4.0 cutoff. The "$50M" is plausible at-magnitude for a mid-size MA contract; not stated as universal, which is correct (it varies by membership and benchmark).
- **Technical Notes reference is mechanism-level, not topic-level** (line 1860, sidenote at 1860). "Denominator logic, significance testing, and improvement score calculation" plus the sidenote naming "denominator changes, hold-harmless logic changes, and cutpoint regeneration" reads like someone who has actually opened the document and traced a measure rewrite through. Hold-harmless and improvement-measure logic are exactly the things that bite you in a rebuild year; naming them unprompted is a credibility signal.
- **Robust exponential smoothing with Huber psi for Stars forecasting** (lines 1860, 1881-1892). This is a defensible, non-trivial choice. The COVID disaster-relief year created exactly the kind of structural outliers that destroy naive ETS forecasts of cutpoints; Huber-clipping the residuals is the right family of fix. The formula being rendered correctly and the caption naming "COVID-era shock" as the failure mode tells me the person has thought about why, not just what.
- **HEDIS hybrid measure framing is correct** (line 1897). Hybrid measures (e.g., CBP, COA) blend administrative claims with medical-record review; the audit-trail framing "treating every source format as a suspected deviation from the specification until proven otherwise" is the right disposition for someone who has actually reconciled NCQA HEDIS Volume 2 specs against vendor extracts.
- **The four-EHR list is operationally honest** (line 1912). Epic / Cerner (Oracle Health) / athenahealth / Veradigm with the sidenote "A medication adherence rate is not portable across these systems until someone sits down and defines it in a source-specific way" is the kind of statement only someone who has lived through MPR/PDC reconciliation across vendors will write unprompted.

### What I expected to see but didn't
- **No named Stars measures.** Nowhere does the text mention a specific measure: no SUPD, no MAH/MAC/MAD (medication adherence triplet), no Plan All-Cause Readmissions, no CAHPS/HOS, no Part D Medication Therapy Management CMR Completion Rate. For someone forecasting Stars cutpoints, the measure portfolio is the work. The Cliff Simulator description names QBP and weights but never a measure that contributes to those weights.
- **No reference to the Tukey outlier deletion / clustering methodology CMS actually uses for cutpoints.** CMS uses hierarchical clustering with mean resampling (and historically Tukey fences) to set cut-points. If you forecast cutpoints, you forecast against that specific algorithm. The page talks about "ordinal logistic regression calibrated to CMS 2025 weights" for the simulator and "robust exponential smoothing" for forecasting, but never the clustering machinery that produces the thresholds in the first place. That's a notable gap.
- **No mention of the Categorical Adjustment Index (CAI) or the disaster adjustment provisions.** These are the two regulatory levers that most directly move a contract across the 4.0 line in any given year. Someone whose role is "translation between CMS requirements and organizational priorities" would normally surface at least one.
- **No member-level data scale anchor.** "Claims and eligibility sources" appears repeatedly but no covered-lives count, no number of contracts supported, no measure count, no HEDIS rate-cell scale. The reader has to take "regulated healthcare" on faith.

### Red flags or hesitation points
- **"Ordinal logistic regression calibrated to CMS 2025 weights" for the Cliff Simulator** (line 2003). The CMS Star Ratings weights are applied to measure scores to produce a contract-level summary; they are not coefficients you "calibrate" an ordinal logit against in any direct sense. The page is clear elsewhere that the simulator is teaching-oriented with synthetic weights, but as written this phrasing could be read as overclaiming methodological alignment with the CMS process. The methodology post may clarify; on-page it is loose.
- **"ECDS Shock Index" tile description is correct in shape but thin** (line 2300-2302). ECDS (Electronic Clinical Data Systems) is a real NCQA reporting standard increasingly mandated for measures like Depression Screening and Follow-Up; the shift from claims-based to ECDS-based reporting genuinely moves rates and therefore cutpoints. The tile names the right concept but in 30 words you cannot tell whether the author understands ECDS data sources (EHR, HIE, case management, registries) versus just the acronym. I would want to click through.
- **"30% to under 5% RxNorm validation discrepancies"** (line 1912). RxNorm normalization is real and important, but "client-audit discrepancies" is doing a lot of work in one phrase. Discrepancies on what (NDC-to-RxCUI mapping? ingredient-level rollups? therapeutic class assignment?) and against what audit standard? Plausible number, under-specified mechanism.
- **HITRUST framed as something he "built under"** (line 1933). HITRUST CSF is a certification framework; an individual contributor designs to its controls but does not personally "build under HITRUST" in the way the sentence reads. Minor, and the surrounding language about "HIPAA compliance was an architectural constraint, not a certification" (line 1921) shows he knows the difference, so this reads more as compression than confusion.

### Level read
Reads as a real practitioner with hands-on Stars/HEDIS production experience and methodological depth, but with portfolio prose that abstracts away from specific measures and CMS algorithms in a way that occasionally underclaims and occasionally overclaims.

### Decision
**ADVANCE.** The Technical Notes mechanism language, the four-EHR portability sidenote, the hybrid-measures framing, and the Huber-psi rationale together clear the domain-credibility bar; the gaps are specificity, not knowledge.

### What would change my mind
I would want a 20-minute conversation where I ask three questions: (1) walk me through how CMS sets the 4.0 cutpoint for a specific measure this year, and where in that pipeline your forecast intervenes; (2) name a HEDIS hybrid measure you actually built the denominator for and tell me where the medical-record-review sample lives in your architecture; (3) when a contract sits at 3.875 going into the rating year, what are the three levers you watch. If the answers come back with measure abbreviations, hierarchical clustering language, hit-rate framing for the chase list, and CAI/disaster-adjustment awareness, this is a strong hire. If the answers stay at the level of the page's prose, the page is a ceiling rather than a floor and the rating drops to HOLD. The bigger structural concern is that nothing in the public artifact lets me verify against real measure work; the BHA Stars predictor is private (correctly), the Cliff Simulator is intentionally synthetic, and the publications are from the UW research era, not the Stars era. The blog posts at /blog/star-rating-predictor-methodology/ and /blog/compliance-as-architecture-stars-predictor/ are where this would either harden or crack.

---

## The four gaps

### Gap 1 — First-impression gap

The page wins on metadata and loses on the rendered hero. The 10-second scanner extracted strong signal from the `<title>` tag, the meta description ("15+ years... Medicare Star Ratings, HEDIS pipelines"), the JSON-LD coherence (named employer, named university, knowsAbout list mixing domain and tools), and the ETBook typography prelude — enough to ADVANCE. But the same evaluator explicitly noted "I never reached an h1 or a hero in 90 lines... the depth of the head suggests a designed page rather than a punchy one, fine for a careful reader, risky for a 10-second scan." The recruiter's 60-second pass confirmed this from the other direction: the subtitle "Healthcare data engineering and Medicare Advantage analytics" is a category description, and the recruiter never found the "15+ years" claim or a team size or a location on the rendered page. The metadata is doing rhetorical work the rendered hero is not. A first-impression visitor lands on the h1 + subtitle, not the meta description; the page needs the latter's specificity at the former's position. The Bing verification TODO comment (lines 13-16) is a small but tangible cleanup item the scanner flagged as a "gatekeeper bounce" signal.

### Gap 2 — Depth-dependency gap

The page's most credibility-building content lives at 5 minutes and never makes it to 60 seconds. The peer engineer's case for ADVANCE rests on the Huber psi-function block (lines 1881-1892), the 30%→5% RxNorm result (line 1912), the medallion-architecture-as-governance framing (line 1918), and the compliance-as-architecture thesis (line 1900 + blog post). The healthcare domain expert's ADVANCE rests on the Technical Notes mechanism language, the four-EHR portability sidenote, and the hybrid-measures audit framing — all of it inside `<details class="fold">` expanders that the 60-second evaluators do not open. The 60-second recruiter caught the keyword surface (Star Ratings, HEDIS, RxNorm, EHR vendor names) but not the mechanism depth; the 60-second executive caught the methodology prose and read it as "engineer-y" rather than as evidence of leadership-grade rigor. Three depth-related fixes are visible: (a) promote at least one mechanism claim out of the BHA fold into the always-visible lead paragraph; (b) treat the writing-cadence pattern as load-bearing — the recent six-post burst is the strongest "still hands-on" signal on the page and it lives below the writing section's `<details>` fold; (c) the testimonials at lines 2505-2529 sit behind a `<details>` and never reach the 60-second eye, even though they would help the manager-track HM if one of them spoke to management work.

### Gap 3 — Role-calibration gap

The page is trying to read as manager, director, AND staff-IC simultaneously and the three role-specific HMs each penalized it for being calibrated to the other two. The director-track HM PASSED with the most consequential read: "Every preceding title is also 'Manager' or 'Analytics Manager, Specialist.' Three consecutive manager titles, none with the word Director, Head, or VP, and none with a stated headcount or budget. The career arc never passes through a director-prep crucible." The manager-track HM HELD: "Strong senior IC who recently stepped into a manager title and is presenting himself for the next manager job; the methodology and translation skills are real, the people-management evidence is functionally absent." The staff-IC-track HM HELD with the inverse complaint: "Every post-2017 role is titled 'Manager.' The page tries hard to reframe this as IC work... which actually concedes the point: this person has chosen management over IC for nine years." The 60-second recruiter's read is the most accurate diagnosis the panel produced: "Solid mid-to-senior IC, credible early-stage manager, not yet a director." The page's level signal is ambiguous because the page is hedging. Two structural absences drive most of the role-calibration damage: no team size or headcount on the BHA role (5 of 8 evaluators flagged this), and no scope language differentiating "managed people" from "managed work" at Health Catalyst (the Jessica McCay testimonial — "the only engineer on the team" — actively contradicts the "Healthcare Analytics Manager" title under that role and was caught by the manager-track HM). The page must pick: a manager-pitch portfolio that names headcount and tells management stories, OR a senior-IC-pitch portfolio that owns the title-and-prose mismatch and leads with system-design depth. It cannot be both.

### Gap 4 — Credibility gap

The page survives expert scrutiny but does not exceed it. Both 5-minute expert evaluators (peer engineer + healthcare domain expert) ADVANCED, and their reasoning converges: the page contains specific, falsifiable, mechanism-level claims that no faker would write. The healthcare domain expert: "The kind of statement only someone who has lived through MPR/PDC reconciliation across vendors will write unprompted." The peer engineer: "Whoever wrote that caption has thought about robust loss functions in a specific operational context." But both flagged the same asymmetry between the page's surface depth and its verifiable artifact set. The most damaging shared finding: **the Stars Cliff Simulator (the headline featured project, the page's most prominent "real artifact") has no GitHub link**. The peer engineer: "For 'ordinal logistic regression in the browser, no dependencies,' I want to read the JS. Without it, I'm trusting that the math under the demo matches the claim." The domain expert echoed this from a different angle: "The Cliff Simulator description names QBP and weights but never a measure that contributes to those weights... 'Ordinal logistic regression calibrated to CMS 2025 weights' — as written this phrasing could be read as overclaiming methodological alignment with the CMS process." Smaller credibility-cost items: dbt named in three stack lines but never discussed in prose; Selenium in the BHA stack undefended; medallion-architecture sidenote correct-sounding but generic enough to read as Databricks-marketing-page material; no named Stars measures (SUPD, MAH/MAC/MAD, PACR, CAHPS/HOS, MTM-CMR); no reference to CMS's hierarchical clustering / Tukey-fence cutpoint algorithm; no CAI or disaster-adjustment mention; HITRUST framed as "built under" rather than "designed to controls." None of these individually would cost an interview. Together they tell a reader who actually understands the domain that the page is real but un-pressure-tested — and that the deepest signal in the corpus lives in the two recent blog posts (`/blog/star-rating-predictor-methodology/`, `/blog/compliance-as-architecture-stars-predictor/`) rather than on the homepage itself.

---

## Prioritized changes

Ordering within each list: (a) number of evaluators flagging, then (b) brutality of the flag. Counts shown in brackets.

### Top-of-page changes (10s leverage)

These govern whether anyone reaches the rest of the page.

1. **Remove the Bing verification TODO comment from production HTML (lines 13-16).** [1 eval; high brutality on a tiny item.] The 10s scanner pattern-matched it as "unfinished" — gatekeeper bounce signal. Five-character change.

2. **Rewrite the subtitle (line 1253) to surface scope or level signal, not just domain.** [Flagged implicitly by 3 evaluators: executive HOLD, manager-track HM HOLD, director-track HM PASS.] Currently "Healthcare data engineering and Medicare Advantage analytics" describes a category. The recruiter would benefit from a verb-claim + denominator ("Builds Medicare Star Ratings and HEDIS pipelines for plans covering N members," "Leads data engineering at Baltimore Health Analytics," or similar). Note: `CLAUDE.md` §Hero marks the subtitle text as locked; this fix requires explicit discussion before edit.

3. **Add a location / work-mode line near the h1 or in the hero region.** [1 eval; medium brutality.] Recruiter flagged: "No location anywhere I caught. Baltimore Health Analytics name implies Baltimore, but the margin note says 'Madison WI.' Remote/hybrid/onsite is unanswered." A single line (e.g., "Madison, WI · remote / hybrid") resolves the ambiguity without committing structural space.

### Mid-page changes (60s leverage)

These govern whether the 60-second scan reaches the conclusion the 5-minute reader would.

1. **Add a team-size / span-of-control line on the BHA role (line 1852).** [5 of 8 evaluators flagged this; universal across all 5-min HMs plus the recruiter and executive.] Highest-leverage single change in the entire evaluation. Recommended phrasing the manager-track HM essentially dictated: "Manager of Data Science & Engineering · Nov 2025 to Present (promoted from Lead Data Engineer, April 2026) · team of N across [geographies]." If the answer is "small player-coach function," say so explicitly; the director-track HM's PASS would re-open to a different role if "small player-coach at 30-person company" were on the page rather than left to inference.

2. **Reframe the April 2026 promotion timeline to defuse the "title aspiration racing ahead" reading.** [3 evaluators flagged: executive, manager HM, director HM.] One option: lead the BHA entry with the Lead Data Engineer title and treat the Manager promotion as a recent event in the body. Another: surface the scope that justifies the new title in the same sentence (team headcount, function ownership). The current parenthetical reads as "six weeks into a new title" to half the panel.

3. **Surface one Health Catalyst outcome at platform/customer level, not pipeline level** (current entry lines 1908-1923). [2 evaluators flagged with high brutality: executive ("five-year tenure with no platform-level outcome"), manager-track HM ("five years in a 'Manager' title that may have been individual contributor work in practice").] One sentence with a customer count, a measure-rate improvement, an ARR-influenced figure, or a deployed-across-N-contracts anchor would change the read.

4. **Replace at least one testimonial with one that speaks to management work** (current entries lines 2505-2529). [1 evaluator flagged with high brutality: "The testimonials don't testify to management. Both quotes are about Zaher as an IC."] If a former direct report, peer manager, or own manager will write something, that surface is more load-bearing than two downstream-consumer quotes.

5. **Open the writing-section `<details>` fold or move the six recent posts above it.** [2 evaluators implicitly flagged: peer engineer ("strongest signal on the page"), Staff IC HM ("the strongest signal on the page is the recent practitioner content").] The 60-second eye does not open `<details>`; the most credibility-building current content is invisible at 60 seconds.

### Detail changes (5min leverage)

These govern whether the deep-read evaluator's ADVANCE becomes the loop's "schedule the interview now" rather than the loop's "schedule a screen call."

1. **Add a GitHub link to the Stars Cliff Simulator featured project (Project 01, around line 2123).** [2 evaluators flagged: peer engineer ("For 'ordinal logistic regression in the browser, no dependencies,' I want to read the JS. Without it, I'm trusting that the math under the demo matches the claim"); domain expert (the Cliff Simulator phrasing's verifiability is a load-bearing concern).] The single highest-leverage detail-level fix in the evaluation.

2. **Name specific Stars measures in BHA or Health Catalyst prose.** [Healthcare domain expert flagged hard: "Nowhere does the text mention a specific measure: no SUPD, no MAH/MAC/MAD (medication adherence triplet), no Plan All-Cause Readmissions, no CAHPS/HOS, no Part D Medication Therapy Management CMR Completion Rate."] One or two named measures, in passing, would convert "knows the topic" to "has shipped the work."

3. **Tighten the "ordinal logistic regression calibrated to CMS 2025 weights" claim on the Cliff Simulator card (line 2003).** [Domain expert: "as written this phrasing could be read as overclaiming methodological alignment with the CMS process."] Either rephrase to acknowledge the simulator's teaching scope ("synthetic weights matched to the CMS 2025 weighting scheme"), or commit to the implication and link to a methodology post that documents the calibration choice.

4. **Add one production-system anchor with numbers a Staff candidate can pressure-test.** [Staff IC HM flagged: "no volumes, latencies, SLAs, schema counts, or pipeline DAG sizes... For a Staff role I want one paragraph that proves the person has actually owned a 10TB+ warehouse or a multi-hundred-model dbt project."] Inside the BHA or Health Catalyst fold; one paragraph.

5. **Defend or contextualize specific stack items.** [Peer engineer flagged 3: Selenium in BHA stack (undefended), dbt program depth (named in 3 stacks but never described), medallion-architecture sidenote (reads as Databricks-marketing-page generic).] One sentence each.

6. **Add CMS clustering / CAI / disaster-adjustment awareness to a Stars project description or BHA fold.** [Domain expert: "No reference to the Tukey outlier deletion / clustering methodology CMS actually uses for cutpoints... No mention of the Categorical Adjustment Index (CAI) or the disaster adjustment provisions."] Together these are "the two regulatory levers that most directly move a contract across the 4.0 line in any given year"; surfacing either converts performance into mechanism.

7. **Fix the HITRUST "built under" framing (line 1933).** [Domain expert flagged as minor.] Change to "designed to HITRUST CSF controls" or similar; the surrounding HIPAA-as-architectural-constraint line already shows the distinction is understood.

---

## The unsoftened summary

The page is a strong-IC-pretending-to-be-a-strong-manager portfolio in a market that punishes the gap. The craft, the methodological depth, and the domain mechanism-language all clear the bar for advancing to a conversation — both peer engineer and healthcare domain expert say so without much hesitation. The recruiter agrees: this is a credible mid-to-senior IC with early-management instincts. But every role-specific hiring manager hits the same wall: the page never says how many people you manage, never tells a hiring or firing or conflict story, and never demonstrates the scope evidence the title is reaching for. The current "Manager of Data Science & Engineering" title is six weeks old, the prior "Manager" titles read as senior-IC-with-coordination in the prose (the Jessica McCay testimonial — "the only engineer on the team" — actively contradicts the Health Catalyst manager title under that role), and the largest reported span of control on the entire page is from a 2007-2014 editorial-services practice. The director-track hiring manager refused to advance. The manager-track hiring manager will only advance after a screen that confirms scope. The Staff IC hiring manager said the page sells management hard enough that it undersells the IC depth that's actually there. The most damaging single absence is a team-size line on the BHA role; five of eight evaluators flagged it, including all three role-specific HMs. The second most damaging absence is a GitHub link on the most prominent featured project; without it, the page's most public artifact is unverifiable for any reader who actually understands the methodology. You are writing prolifically right now, your domain mechanism language is unusual for the corpus, and you are presenting with more craft than 95% of healthcare-data portfolios — and the page is still costing you director interviews because it has chosen to leave the level signal ambiguous.

---

Report file: `evaluations/hiring-eval-2026-05-23.md`
