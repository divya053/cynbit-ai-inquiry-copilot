# AI Opportunity Report: Cynbit Technologies

**Prepared by:** Divya Lalwani, AI/ML Engineer Intern assessment
**Date:** 29 October 2026
**Sources:** the public pages of cynbit.in (Home, Services, Products, Case Studies, BitElevate, Contact). No internal Cynbit data was used. Where a number below is an assumption rather than a fact, it is labelled as an assumption.

---

## 1. Summary

Cynbit sells AI automation, software, cloud and marketing services, runs three SaaS products (Revio, TenantEase, Cynbit Studio) and trains interns through BitElevate. I mapped where AI/ML can add value across four areas and found **10 opportunities**. Each one is scored for impact and feasibility.

**Recommended first project: the AI Inquiry Copilot.** It reads every message that reaches Cynbit (website form, email, WhatsApp) and then:

- works out what the sender wants
- extracts the budget, timeline and scope
- scores the lead and routes it to the right team
- drafts a reply that only mentions real Cynbit services and case studies

A salesperson approves the reply before it is sent.

Why this one first:

1. **It removes a visible bottleneck.** The contact form has a single free-text box (no service, budget or timeline fields) and promises a reply within 24 hours. Today someone has to read and sort every message by hand. With the copilot the first reply can go out in minutes, and the best leads are handled first.
2. **Cynbit already sells this.** Its services page offers *"Smart AI assistants that manage leads and coordination."* Running the same assistant in-house makes it a live demo and case study for sales, and it can later become a product next to Revio.
3. **Low risk, quick to build, easy to measure.** A person approves every reply. A working prototype exists in this repository. Success is measured with response time, lead conversion and hours saved.

---

## 2. Cynbit today (from public information)

| Area | What the website says | Where AI fits |
|---|---|---|
| **Services** | AI Automation Suite (autonomous agents, LLM document automation, AI voice agents, AI stack integration), Custom IT (full-stack, backend, AWS/Azure cloud, legacy migration), Digital Marketing (performance ads, technical SEO, CRM automation, funnels) | Cynbit's own sales and delivery workflows; what it sells to clients |
| **Products** | **Revio**: AI review replies, sentiment, crisis detection, multi-location. **TenantEase**: rent, tenants, dues, reminders, occupancy dashboard (no AI mentioned). **Cynbit Studio**: AI code evaluation, mock interviews, resume, job matching | Product features and differentiation |
| **BitElevate** | 60-day remote internship, 1 pull request a day, 6 labs, line-by-line PR review by senior reviewers, Rs 3,999, "1,000+ interns graduated" | Reviewer time grows with every intern |
| **Clients and case studies** | 13 case studies across health (WizHealth, Pragya, CarePlus), retail (Urban Wardrobe, EliteVogue, TrendMart), fintech (GlobalPay), edtech (EContentPrep), events (Evento) and more | Knowledge to reuse in proposals and replies |
| **Sales channel** | Contact form with 5 fields (name, email, company, industry, free-text message), 3 phone numbers, one email address, "24 H response", discovery call as the next step | Inquiry handling, the subject of the PoC |
| **Stack** | Python, TypeScript; FastAPI, NestJS, Next.js; OpenAI, LangChain, PyTorch, Pinecone; AWS, Azure, Docker, Kubernetes; Postgres, MongoDB, Redis, Supabase | The prototype uses the same tools (Python, FastAPI), so the team can adopt it easily |

**What stands out:**

- Cynbit has many ways in (three businesses, three phone numbers, one form, social media), and everything lands in **one unstructured stream**. Client leads, internship questions, job seekers, vendors and spam all arrive mixed together.
- The careers portal this assessment came from shows the same pattern: one applicant can hold several applications across roles.
- Cynbit's growth depends on a few kinds of skilled human time: sales, senior engineers and PR reviewers. The best AI opportunities save exactly that time.

---

## 3. How I evaluated the opportunities

Each opportunity is scored from 1 (low) to 5 (high) on:

- **Impact:** revenue, hours saved or better customer experience.
- **Feasibility:** data available today, technical risk, time to a first version.
- **Strategic fit:** does it strengthen what Cynbit sells? Can it become a case study or product?

**Priority = Impact × Feasibility, with fit used as the tie-breaker.**

---

## 4. Opportunity map

### A. Internal operations and sales

| # | Opportunity | Problem today | AI/ML approach | Impact | Feasibility | Fit |
|---|---|---|---|---|---|---|
| **A1** | **AI Inquiry Copilot** (chosen) | Free-text inquiries from several channels; sorting, qualifying and replying are manual; 24-hour promise | LLM structured extraction + retrieval over Cynbit's offerings + rule-based lead score + human-approved grounded reply | 4 | 5 | 5 |
| A2 | Discovery-call to proposal generator | Proposals are written by hand after each discovery call | Speech-to-text (Hindi/English) → LLM scope extraction → estimate based on past similar projects (retrieval over past SOWs) → proposal draft | 5 | 3 | 4 |
| A3 | Delivery risk radar | Projects slip without early warning | Signals from GitHub, Jira and Slack (PR age, reopened bugs, overtime) → risk classifier + weekly LLM summary for project managers | 3 | 3 | 3 |
| A4 | Hiring assessment pre-screen | Many applications per role (this portal) | Rubric-based LLM first pass on submissions and code repositories, scores with evidence, human final decision; fairness checks | 3 | 4 | 3 |

### B. BitElevate (education)

| # | Opportunity | Problem today | AI/ML approach | Impact | Feasibility | Fit |
|---|---|---|---|---|---|---|
| **B1** | AI PR pre-reviewer | Seniors review about 1 PR per intern per day, and the 60-day programme has 1,000+ graduates. Review time grows with every intern | Static analysis + LLM review against each lab's rubric → line comments posted as a first pass; seniors review only flagged PRs and edit the AI's comments | 5 | 4 | 5 |
| B2 | Intern drop-out prediction | Streaks break, interns quietly stop | Gradient-boosted model on commit cadence, review turnaround and war-room scores → nudge mentors early | 3 | 3 | 3 |

### C. Products

| # | Opportunity | Problem today | AI/ML approach | Impact | Feasibility | Fit |
|---|---|---|---|---|---|---|
| C1 | **Revio**: Hinglish and regional-language replies + aspect-based sentiment | Indian reviews mix Hindi and English; one overall sentiment score hides *what* is wrong (food, staff, wait time) | Multilingual LLM replies in the reviewer's language; aspect extraction → per-branch aspect dashboard; fake-review signals | 4 | 4 | 5 |
| C2 | **TenantEase**: late-payment risk + smart reminders | Reminders are the same for everyone, and dues pile up | Late-payment classifier on payment history; best reminder time and channel; OCR + face match for tenant ID verification | 4 | 3 | 4 |
| C3 | **Cynbit Studio**: skill-gap to job-match embeddings | Matching students to jobs by keywords is weak | Embed skill radar + projects and job descriptions; explainable match ("missing: Docker, SQL joins") linked to learning paths | 3 | 3 | 4 |

### D. Marketing

| # | Opportunity | Problem today | AI/ML approach | Impact | Feasibility | Fit |
|---|---|---|---|---|---|---|
| D1 | Case-study and SEO content engine | Case studies on the site are headlines without detail | LLM drafts long-form case studies and industry pages from delivery notes, with human editing; technical SEO checks | 3 | 4 | 3 |

### Priority ranking

| Rank | Opportunity | Impact × Feasibility | Why this rank |
|---|---|---|---|
| 1 | **A1 Inquiry Copilot** | 20 | Fastest to value, no historical data needed, dogfoods a service Cynbit sells |
| 2 | B1 PR pre-reviewer | 20 | Big savings in reviewer time; needs lab rubrics and access to past PR reviews |
| 3 | C1 Revio multilingual + aspects | 16 | Clear product differentiation in the Indian market |
| 4 | A2 Proposal generator | 15 | High value, but needs past proposals and estimates as training data |
| 5 | A4 Hiring pre-screen | 12 | Useful but needs careful fairness and transparency work |
| 6 | C2 TenantEase risk + reminders | 12 | Needs months of payment history per property |
| 7 | D1 Content engine | 12 | Low risk, moderate value |
| 8–10 | A3, B2, C3 | 9 | Need more data |

A1 and B1 score the same. **A1 goes first** because it needs no historical data: it works on day one with public information. It also feeds A2 directly: the requirements the copilot extracts become the input to the proposal generator. B1 is the recommended second project.

---

## 5. The chosen opportunity: AI Inquiry Copilot

### What it does

```
Message (form / email / WhatsApp, in English, Hindi or Hinglish)
   → intent: client project | internship | job | partnership | support | spam
   → details: services needed, industry, company, budget (Rs), timeline, urgency, decision maker, requirements
   → missing information + discovery-call questions
   → lead score 0–100 with reasons → priority P1/P2/P3 → team + response time target
   → reply draft that cites only real Cynbit services and case studies → a person approves and sends
```

### Expected value

These are **assumptions to check with Cynbit's real numbers**. The formula is the point, not the exact figures.

| Driver | Assumption | Result |
|---|---|---|
| Inquiries per month (all three businesses) | 300 | — |
| Manual handling per inquiry (read, sort, look up, draft) | 6 min | 30 hours/month |
| Handling with copilot (review and send) | 1.5 min | 7.5 hours/month, about **22 hours saved** |
| Time to first response, hot leads | from up to 24 h → under 1 h | Faster replies win more deals, a widely reported effect in B2B sales |
| Non-sales messages handled without sales (internship, jobs, spam) | ~25% of volume (8 of 30 in the test set) | Sales sees only real leads |
| LLM cost per inquiry (Claude Opus 5.5, low effort, ~1.5k input + ~0.6k output tokens at $4/$20 per million) | ≈ $0.018 ≈ **Rs 1.5** | ≈ Rs 450/month for 300 inquiries |

**If even one extra project a quarter is won because the reply went out within the hour, the copilot pays for itself many times over.**

### How success is measured

- **Model quality**, on a labelled set that grows over time:
  - intent accuracy ≥ 95%
  - service-line F1 ≥ 0.90
  - budget extraction ≥ 95%
- **Operations:**
  - median time to first reply
  - share of drafts sent with light or no edits
  - fallback rate (how often the offline rules had to take over)
- **Business:**
  - inquiry → discovery call conversion
  - discovery call → signed project conversion, compared with before the rollout

### Risks and how they are handled

| Risk | Mitigation in the design |
|---|---|
| The reply promises something Cynbit doesn't offer (hallucination) | The reply may only use retrieved Cynbit content; the prompt forbids prices, dates and unlisted clients; a person approves every send |
| Prompt injection inside an inquiry ("ignore your instructions…") | The inquiry is wrapped as data with delimiters; output is limited to a fixed JSON schema; the model has no tools and cannot take actions |
| Personal data (DPDP Act 2023) | Only the needed fields are kept; retention limits; the provider is configured for no training on the data; contact details masked in logs |
| Wrong priority for a good lead | Lead score is transparent code with reasons; every inquiry is still visible in the inbox; weights tuned on real conversion data |
| API outage or cost spike | Automatic fallback to the offline rules (tested); per-inquiry cost logged; a cheaper model can be swapped in with one setting |

### Roadmap

| Phase | Weeks | Deliverable |
|---|---|---|
| 0. PoC | done | This repository: pipeline, Streamlit demo, REST API, 30-inquiry evaluation, tests |
| 1. Pilot | 1–3 | Connect the website form + Gmail; run in shadow mode (drafts only); sales labels 200 real inquiries |
| 2. Rollout | 4–6 | Human-approved sending; CRM sync (HubSpot/Zoho); WhatsApp Business API; dashboard |
| 3. Learn | 7–12 | Re-weight the lead score from won/lost deals; hybrid search with embeddings; feed extracted requirements into A2 (proposal generator) |
| 4. Productize | 12+ | Offer the copilot as a Cynbit product to clinics, coaching institutes and agencies, next to Revio |
