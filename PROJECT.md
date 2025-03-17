### Project: Active Patient Follow-Up Alert Dashboard

**Overview:**  
Build a lightweight web application that simulates an automated alert system for abnormal lab results. The dashboard would display a list of patients flagged for follow-up, with risk scores derived from a simple ML model that can be refined through user feedback—hinting at an active learning loop.

---

**Key Components:**

1. **Simulated Data Source:**  
   - Create a small synthetic dataset of patient lab results (e.g., blood tests with various metrics) where some values are outside normal ranges.
   - Include metadata like patient ID, test type, result value, and timestamp.

2. **Abnormality Detection & Risk Scoring:**  
   - Implement a rule-based filter for obvious abnormal values.
   - Integrate a basic risk scoring algorithm (e.g., a logistic regression model or decision tree) to rank the urgency of follow-up needs.
   - Optionally, add a feedback mechanism where a clinician can mark an alert as “correct” or “false positive,” feeding into a rudimentary active learning loop that updates thresholds or re-weights features.

3. **User Interface:**  
   - Develop a single-page application using a modern framework (React/Angular) to present the data in a dashboard.
   - Include key visual elements: a table of flagged patients, risk scores, and interactive buttons for clinician feedback.
   - A clear demo flow: simulate a new batch of test results, trigger the alert generation, and show how feedback adjusts the risk ranking in near real time.

4. **Integration & Extensibility:**  
   - Mimic an integration with EMR systems by setting up a simple API that serves the synthetic data.
   - Show how the system could be extended to handle live data streams, aligning with Anima’s experience integrating with EMIS/SystmOne.

---

**Why This Project Stands Out:**

- **Direct Impact on Patient Safety:**  
  Demonstrates your ability to address real-world issues (missed follow-ups and misdiagnoses) that Anima is focused on.
  
- **Active Learning & Rapid Iteration:**  
  Incorporates an initial version of an active learning loop, showing your vision for evolving a static system into a dynamic, self-improving one.
  
- **Technical Breadth:**  
  Combines front-end development, API integration, and a simple machine learning model—mirroring the full-stack, technical, and UX-focused environment at Anima.
  
- **Scalability & Extensibility:**  
  The project is designed to be a proof-of-concept that can be quickly iterated upon and expanded, much like the rapid deployments described in the job ad.

---

**Demo Outline (5 Minutes):**

1. **Introduction (1 minute):**  
   Briefly explain the problem (missed abnormal results) and how the dashboard aims to mitigate this with automated alerts.

2. **Live Demo (3 minutes):**  
   - Walk through the dashboard UI, highlighting the list of patients and their risk scores.
   - Simulate incoming lab results and show how the system flags a patient.
   - Demonstrate the feedback mechanism by marking an alert, then show a quick update on the dashboard reflecting the active learning adjustment.

3. **Wrap-Up (1 minute):**  
   Discuss potential future enhancements (integration with live EMR APIs, more advanced ML models, deeper active learning mechanisms) and how this aligns with the mission of saving lives.

---

This project is ambitious enough to catch the attention of a team that values rapid, impactful solutions and technical depth, yet it’s scoped to be completed in 1-2 days with a clear, impressive demo.