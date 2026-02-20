export const siteConfig = {
  name: "Zaher",
  title: "Healthcare Analytics & Data Engineering",
  description: "Portfolio website of Zaher Karp - Healthcare Analytics with SQL and Python",
  accentColor: "#3b82f6",
  colors: {
    light: {
      accent: "#3b82f6",
      accentHover: "#2563eb",
      text: "#1f2937",
      textLight: "#6b7280",
      border: "#e5e7eb",
      background: "#f9fafb",
      backgroundAlt: "#f3f4f6",
    },
    dark: {
      accent: "#60a5fa",
      accentHover: "#93c5fd",
      text: "#f9fafb",
      textLight: "#9ca3af",
      border: "#374151",
      background: "#111827",
      backgroundAlt: "#1f2937",
    },
  },
  social: {
    email: "email@zaherkarp.com",
    linkedin: "https://linkedin.com/in/zkarp",
    github: "https://github.com/zaherkarp",
    researchgate: "https://www.researchgate.net/profile/Zaher-Karp",
    tableau: "https://public.tableau.com/app/profile/zaher.karp/vizzes",
    blog: "/blog",
  },
  aboutMe:
    "I build healthcare analytics as products, not reports. I work across population health, data engineering, and clinical operations to create scalable systems that connect revenue, cost, and quality in real-world complexity. I'm always open to conversations about analytics designed to integrate cleanly into complex software and real workflows.",
  skills: [
  "AWS (S3, Glue)",
    "Azure Data Factory",
    "Databricks",
    "SQL (Postgres, Redshift, SQL Server, MariaDB)",
    "Python (pandas, PySpark)",
    "dbt",
    "Bash",
    "Tableau",
    "Power BI",
    "Sisense",
    "Epic Clarity Analytics",
    "Veradigm Analytics",
    "Cerner Analytics",
    "athenahealth Analytics",
    "SAS",
    "Stata"
  ],
  projects: [
    {
      name: "Client-Side Stars Analytics Dashboard (Single-File HTML)",
      description:
        "Standalone, in-browser dashboard implemented as a single HTML file using Chart.js 4.4.1, PapaParse 5.4.1, jsPDF 2.5.1, and chartjs-plugin-datalabels to visualize local CSV data and generate PDF reports with no server dependency and no data leaving the user's machine.",
      skills: ["Chart.js", "PapaParse", "jsPDF", "JavaScript", "HTML", "Client-Side Analytics"],
    },
    {
    name: "Skill-Based Job Transition Discovery Platform (O*NET-Powered MVP)",
    description: 
        "Production-minded MVP web application built with FastAPI, PostgreSQL, and Redis/Celery that leverages O*NET occupation and skill data plus baseline deterministic matching and logistic-regression calibration to generate Ready Now, Trainable, and Long-Term Reskill job transition recommendations with skill gap analysis, training path suggestions, and a feedback-driven learning system.",
        link: "https://github.com/zaherkarp/skillsprout",
        skills: ["FastAPI", "PostgreSQL", "SQLAlchemy", "Redis", "Celery", "scikit-learn", "Logistic Regression", "O*NET", "Python", "Pydantic"],
    },
    {
      name: "Lessons Learned from healthfinch's Charlie Practice Automation: A Case Study",
      description:
        "Analytics used in case study at OCHIN, Inc. examining healthfinch's Charlie Practice Automation Platform implementation across multiple community health centers. Focus on workflow optimization and return on investment achieved through data-driven decision making.",
      link: "https://www.chcf.org/wp-content/uploads/2019/04/LessonsLearnedImplementingCharlieCaseStudy.pdf",
      skills: ["Linear Regression", "Statistics", "Sisense", "Epic Clarity"],
    },
    {
      name: "Clinic Environment & Team Interaction Research",
      description:
        "Led comprehensive research study on how environmental design influences team interactions in family medicine clinics. Secured $18,000 grant, conducted 120 hours of observations, facilitated 9 focus groups with 40 participants, and published peer-reviewed findings on communication, efficiency, and privacy perceptions.",
      link: "https://journals.sagepub.com/doi/abs/10.1177/1937586719834729",
      skills: ["Mixed Methods Research", "Grant Writing", "Human Subjects Protocols", "NVivo"],
      citations: {
        googleScholar: { url: "https://scholar.google.com/scholar?cites=11399498824498589520", label: "Citations" },
        researchGate: { url: "https://www.researchgate.net/publication/331570926_Clinic_Environments_and_Interactions_Examination_of_a_Community_Health_Center", label: "Reads" },
        pubmed: { url: "https://pubmed.ncbi.nlm.nih.gov/30894019/", label: "PubMed" },
      },
    },
    {
      name: "UW Health Patient Relations Survey Redesign",
      description:
        "Redesigned primary care patient survey for UW Health Patient Relations/Resources department. Conducted pretesting with patient interviews to ensure survey validity and usability improvements.",
      link: "",
      skills: ["Survey Design", "Patient Experience", "Healthcare Quality", "Qualtrics"],
    },
    {
      name: "Care Delivery Workflow Changes",
      description:
        "Analyzed organization-wide care delivery changes using interrupted time series analysis on clinic panel data. Measured impact of change initiatives with segmentation and regression modeling.",
      link: "",
      skills: ["Stata", "SAS", "Time Series Analysis", "Outpatient Analytics"],
    },
    {
      name: "Cancer Prevention in Mental Health Populations",
      description:
        "Conducted research studying cancer prevention screening rates in patients with co-morbid severe mental illness using logistic regression and the Elixhauser Comorbidity Index.",
      link: "",
      skills: ["Logistic Regression", "Population Health", "Healthcare Disparities", "SAS"],
    },
    {
      name: "Depression Curriculum Evaluation",
      description:
        "Evaluation of a medical student depression curriculum. Published peer-reviewed research on broadening medical students' exposure to the range of illness experiences with a focus on depression education.",
      link: "https://github.com/zaherkarp/depression-curriculum-evaluation",
      skills: ["Univariate Statistical Analysis", "Medical Education", "Stata"],
      citations: {
        googleScholar: { url: "https://scholar.google.com/scholar?cites=15568564972028498984", label: "Citations" },
        researchGate: { url: "https://www.researchgate.net/publication/280717178_Depression_Curriculum", label: "Reads" },
        pubmed: { url: "https://pubmed.ncbi.nlm.nih.gov/26107169/", label: "PubMed" },
      },
    },
    {
      name: "Medicare Shared Savings Program Analysis",
      description:
        "Analysis examining the relationship between Medicare Shared Savings Program (MSSP) Accountable Care Organization savings and baseline expenditures. Published findings on cost patterns in value-based care.",
      link: "https://github.com/zaherkarp/medicare-shared-savings-analysis",
      skills: ["Logistic Regression", "Healthcare Economics", "Value-Based Care", "ACO Analytics", "Stata", "SAS"],
      citations: {
        googleScholar: { url: "https://scholar.google.com/scholar?cites=5765814482786120498", label: "Citations" },
        researchGate: { url: "https://www.researchgate.net/publication/303684652_Medicare_Shared_Savings_Program", label: "Reads" },
      },
    },
    {
      name: "Law School Graduation Rates Analysis",
      description:
        "Statistical analysis of law school graduation rates using multivariate regression modeling. Conducted as part of research work at the Center for Patient Partnerships.",
      link: "https://github.com/zaherkarp/law-graduation-rates",
      skills: ["Regression Analysis", "Education Analytics", "Stata", "SAS"],
    },
  ],
  experience: [
    {
      company: "Baltimore Health Analytics",
      title: "Lead Data Engineer",
      dateRange: "Nov 2025 - Present",
      bullets: [
        "Data engineering and technical leadership for analytics to proactively monitor, measure, and improve Medicare Star Rating scores",
      ],
    },
    {
      company: "Sustainable Clarity",
      title: "Principal",
      dateRange: "Sep 2025",
      bullets: [
        "Providing data engineering consulting",
      ],
    },
    {
      company: "Health Catalyst",
      title: "Healthcare Analytics Manager, Embedded Refills and Care Gaps",
      dateRange: "Aug 2020 - Aug 2025",
      bullets: [
        "Built SQL views and dashboards and led analytics incident response",
        "Reduced storage costs by half by optimizing legacy storage (Amazon Web Services S3)",
        "Designed and implemented systems and workflows to support self-service of labels for aggregation and comparison",
        "Redesigned legacy analytics, reducing code by 75% for major customer segments using common procedures and shared stored parameters",
        "Designed and implemented systems and workflows for analytic security and identity, allowing for enhanced protection, SSO integration, and insight into user activity and flow",
      ],
    },
    {
      company: "healthfinch",
      title: "Healthcare Analytics Manager",
      dateRange: "Jan 2019 - Jul 2020",
      bullets: [
        "Developed 0-1 analytics systems across storage, warehouses, SQL dashboards, and analytic security/governance systems",
      ],
    },
    {
      company: "healthfinch",
      title: "Healthcare Analytics Specialist",
      dateRange: "Dec 2017 - Dec 2018",
      bullets: [
        "Designed analytics for customers to optimize their protocol use and clinical workflows as a data analyst/engineer",
        "Performed Epic Clarity, athenahealth, Cerner, and Veradigm data wrangling in varieties of SQL for healthfinch's Practice Automation Platform",
        "Helped healthcare systems achieve 4-6x return on investment through data-driven workflow optimization",
      ],
    },
    {
      company: "University of Wisconsin-Madison, Department of Family Medicine and Community Health",
      title: "Assistant Researcher",
      dateRange: "Dec 2015 - Jun 2018",
      bullets: [
        "Measured results of organization-wide change initiatives with segmentation and regression after modeling data using Stata and SAS",
        "Determined care delivery changes in clinic panel data using interrupted time series",
        "Studied cancer prevention in those with co-morbid severe mental illness using logistic regression and the Elixhauser Comorbidity Index",
        "Evaluated behavioral health care management program fidelity and reported recommendations",
        "Presented research findings at national conferences",
      ],
    },
  ],
  education: [
    {
      school: "University of Wisconsin-Madison",
      degree: "Master of Public Health (MPH), Biostatistics",
      dateRange: "2013 - 2015",
      achievements: [
        "Health Innovation Program Research Trainee",
        "Trained in dissemination & implementation research, qualitative interviewing, and focus group facilitation",
        "Designed, wrote grant proposal (awarded $18,000), and published peer-reviewed research on clinic environments"
      ],
    },
    {
      school: "University of Wisconsin-Madison",
      degree: "Industrial & Systems Engineering Graduate Certificate, Patient Safety",
      dateRange: "2014 - 2015",
      achievements: [
        "Trained through AHRQ-funded Systems Engineering Initiative for Patient Safety",
        "Completed quality improvement projects in medication safety using root cause and job analysis"
      ],
    },
    {
      school: "University of Wisconsin-Madison",
      degree: "Bachelor of Arts (BA), English Literature",
      dateRange: "2003 - 2007",
      achievements: [],
    },
  ],
};
