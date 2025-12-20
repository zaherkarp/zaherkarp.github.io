export const siteConfig = {
  name: "Zaher",
  title: "Healthcare Analytics & Data Engineering",
  description: "Portfolio website of Zaher Karp - Healthcare Analytics with SQL and Python",
  accentColor: "#1d4ed8",
  colors: {
    accent: "#1d4ed8",
    accentHover: "#1e40af",
    text: "#1f2937",
    textLight: "#6b7280",
    border: "#e5e7eb",
    background: "#ffffff",
    backgroundAlt: "#f9fafb",
  },
  social: {
    email: "zaherkarp@gmail.com",
    linkedin: "https://linkedin.com/in/zkarp",
    github: "https://github.com/zaherkarp",
    researchgate: "https://www.researchgate.net/profile/Zaher-Karp",
    blog: "/blog",
    tableau: "https://public.tableau.com/app/profile/zaher.karp/vizzes",
  },
  aboutMe:
    "I care deeply about the distinction between products and services as it pertains to the healthcare analytic space and optimizing the experiences of all users. I am always interested in discussions around population health analytics and related opportunities, especially in the health technology/digital health space.",
  skills: [
    "Amazon Web Services (S3, Glue)",
    "Microsoft Azure (Data Factory)",
    "SQL (Postgres, Redshift, SQL Server, MariaDB)",
    "Python (pandas, PySpark)",
    "Shell scripting (bash)",
    "dbt",
    "Databricks",
    "Tableau",
    "Power BI",
    "Sisense",
    "Epic Clarity analytics",
    "Veradigm analytics",
    "Cerner analytics",
    "athenahealth analytics",
    "SAS",
    "Stata"
  ],
  projects: [
    {
      name: "Lessons Learned from healthfinch's Charlie Practice Automation: A Case Study",
      description:
        "Analytics used in case study at OCHIN, Inc. examining healthfinch's Charlie Practice Automation Platform implementation across multiple community health centers. Focus on workflow optimization and return on investment achieved through data-driven decision making.",
      link: "https://www.chcf.org/wp-content/uploads/2019/04/LessonsLearnedImplementingCharlieCaseStudy.pdf",
      skills: ["Statistical Analysis", "Sisense", "Epic Clarity"],
    },
    {
      name: "Clinic Environment & Team Interaction Research",
      description:
        "Led comprehensive research study on how environmental design influences team interactions in family medicine clinics. Secured $18,000 grant, conducted 120 hours of observations, facilitated 9 focus groups with 40 participants, and published peer-reviewed findings on communication, efficiency, and privacy perceptions.",
      link: "https://journals.sagepub.com/doi/abs/10.1177/1937586719834729",
      skills: ["Mixed Methods Research", "Grant Writing", "IRB Protocol", "NVivo"],
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
      skills: ["Stata", "SAS", "Time Series Analysis", "Healthcare Analytics"],
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
    },
    {
      name: "Medicare Shared Savings Program Analysis",
      description:
        "Analysis examining the relationship between Medicare Shared Savings Program (MSSP) Accountable Care Organization savings and baseline expenditures. Published findings on cost patterns in value-based care.",
      link: "https://github.com/zaherkarp/medicare-shared-savings-analysis",
      skills: ["Logistic Regression", "Healthcare Economics", "Value-Based Care", "ACO Analytics", "Stata", "SAS"],
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
        "Performed Epic Clarity data wrangling in varieties of SQL for healthfinch's Practice Automation Platform",
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
        "Focused on human factors in healthcare settings",
        "Completed projects in medication safety including root cause analysis and job analysis in pharmacy settings",
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
