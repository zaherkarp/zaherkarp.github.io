---
title: "Law School Graduation Rates Analysis"
description: "Statistical analysis of law school graduation using multivariate regression modeling and educational analytics"
pubDate: 2024-01-10
tags: ["Stata", "SAS", "Regression Analysis", "Education Analytics", "Statistical Methods", "Policy Research"]
---

## Project Background

This statistical analysis project was conducted during my time at the **Center for Patient Partnerships** at the University of Wisconsin-Madison. While the Center primarily focuses on healthcare advocacy, this project examined educational outcomes in legal education—an example of how analytical skills transfer across sectors.

The research investigated factors associated with law school graduation rates, with implications for educational policy, student support services, and admissions practices.

## Research Context

### Why Law School Graduation Rates Matter

Law school represents a significant investment:
- **Financial**: High tuition costs and opportunity costs
- **Time**: Three years of intensive study
- **Career**: Bar passage and professional licensure

Non-completion has serious consequences:
- Debt without degree benefits
- Career disruption
- Psychological impact
- Lost professional development

### The Educational Pipeline

Understanding graduation rates requires examining the entire pipeline:
- Admissions criteria and processes
- Student characteristics and preparation
- Institutional support structures
- Financial aid and work requirements
- Academic standards and progression policies

## Research Questions

This project addressed several key questions:

1. What student characteristics predict successful graduation?
2. How do institutional factors affect graduation rates?
3. Are there interaction effects between student and institutional characteristics?
4. What is the relative importance of different predictive factors?

## Data Sources

### American Bar Association Data

The ABA collects comprehensive data on law schools:
- Admissions statistics (LSAT scores, undergraduate GPA)
- Student demographics
- Graduation and attrition rates
- Employment outcomes
- Institutional characteristics

### National Center for Education Statistics

Supplementary data from NCES provided:
- Financial aid information
- Institutional resources
- Geographic and regional factors

### Data Integration Challenges

Merging data across sources required:
- Careful matching of institutional identifiers
- Handling of missing data
- Validation of merged results
- Temporal alignment across datasets

## Statistical Methodology

### Dependent Variable

**Graduation Rate**: Percentage of students completing JD within expected timeframe

Considerations:
- Some students take longer than 3 years (part-time programs)
- Transfer students complicate calculations
- Leave of absence and returning students
- Definition varies by institution

### Independent Variables

#### Student-Level Factors
- LSAT score percentiles
- Undergraduate GPA
- Demographic characteristics
- Full-time vs. part-time enrollment

#### Institutional Factors
- Public vs. private status
- Geographic region
- Student-faculty ratio
- Financial resources per student
- Library resources
- Bar passage rates

### Multivariate Regression Modeling

#### Model Specification

We tested multiple regression specifications:

```stata
* Basic model
regress grad_rate lsat_median ugpa_median

* Extended model with institutional factors
regress grad_rate lsat_median ugpa_median ///
        student_faculty_ratio resources_per_student ///
        public_private region, robust

* Full model with interactions
regress grad_rate c.lsat_median##i.public_private ///
        controls, robust
```

#### Statistical Software

**Stata** was the primary tool for modeling:
- Flexible regression procedures
- Excellent diagnostics
- Publication-quality graphics
- Reproducible analysis scripts

**SAS** supplemented Stata for:
- Data cleaning and merging
- Descriptive statistics
- Supplementary analyses

## Key Analytical Techniques

### Variable Transformation

Several variables required transformation:
- Logged financial variables (right-skewed distributions)
- Standardized test scores (for interpretability)
- Created categorical versions of continuous variables for non-linearity testing

### Interaction Terms

Tested whether relationships varied by institutional type:
```stata
* Does the effect of LSAT differ by public/private status?
regress grad_rate c.lsat##i.public_private controls
margins public_private, at(lsat=(145(5)170))
marginsplot
```

### Model Diagnostics

Comprehensive diagnostic testing:

**Linearity**: Examined residual plots and tested quadratic terms
```stata
rvfplot, yline(0)
```

**Homoscedasticity**: Tested constant variance assumption
```stata
estat hettest
```

**Multicollinearity**: Examined variance inflation factors
```stata
vif
```

**Influential Observations**: Identified potential outliers
```stata
predict leverage, leverage
predict residuals, residual
scatter residuals leverage
```

### Model Comparison

Used information criteria to compare models:
```stata
estimates store model1
* ... fit model2 ...
estimates store model2
estimates stats model1 model2
```

## Key Findings

### Student Characteristics

As expected, pre-admission metrics strongly predicted graduation:

1. **LSAT Scores**: Strong positive association with graduation rates
2. **Undergraduate GPA**: Significant predictor, though weaker than LSAT
3. **Part-time Status**: Part-time students showed lower completion rates

### Institutional Factors

Several institutional characteristics mattered:

1. **Student-Faculty Ratio**: Lower ratios associated with higher graduation rates
2. **Resources**: Financial resources per student showed positive association
3. **Regional Variation**: Significant geographic differences persisted after controlling for other factors

### Interaction Effects

Important interactions emerged:
- The relationship between LSAT and graduation rates was stronger at less-resourced institutions
- Public vs. private status moderated several relationships
- Regional effects varied by institutional characteristics

### Effect Sizes

Beyond statistical significance, we calculated practical significance:
- A 1-point increase in median LSAT associated with X% increase in graduation rate
- Effect sizes placed in context of typical variation across schools

## Challenges and Solutions

### Challenge: Aggregated Data

Working with institution-level rather than student-level data:
- Ecological fallacy concerns
- Cannot examine individual student trajectories
- Reduced statistical power for some analyses

**Solution**: Clearly communicated limitations and focused on institution-level research questions

### Challenge: Selection Effects

Students aren't randomly assigned to law schools:
- School quality affects admissions selectivity
- Geographic preferences influence school choice
- Financial considerations drive enrollment decisions

**Solution**: Extensive controls and careful interpretation of causal language

### Challenge: Unmeasured Confounders

Many potentially important factors unmeasured:
- Student motivation and commitment
- Quality of pre-law advising
- Family support systems
- Financial pressures

**Solution**: Acknowledged limitations and framed findings appropriately

### Challenge: Changing Landscape

Legal education changed significantly during study period:
- Declining enrollment in some years
- Increased focus on employment outcomes
- Changes in ABA accreditation standards

**Solution**: Sensitivity analyses by time period; focus on consistent patterns

## Skills Demonstrated

### Statistical Analysis
- Multivariate regression modeling
- Interaction term testing
- Model diagnostics and validation
- Effect size calculation
- Sensitivity analyses

### Stata Programming
- Data cleaning and merging
- Regression procedures
- Marginal effects calculation
- Graphics and visualization
- Reproducible workflows with do-files

### SAS Programming
- Data manipulation
- Descriptive statistics
- Supplementary analyses
- Integration with Stata results

### Research Communication
- Translating statistical findings to policy implications
- Creating clear visualizations
- Writing for educational policy audiences
- Acknowledging limitations appropriately

## Policy and Practical Implications

### For Law Schools

Findings suggested several areas for institutional focus:
- Importance of student support services (suggested by faculty ratio findings)
- Value of adequate resourcing for student success
- Need for holistic admissions considering multiple factors

### For Students

Results informed prospective students about:
- Importance of pre-law academic preparation
- Consideration of institutional resources beyond rankings
- Value of full-time vs. part-time enrollment trade-offs

### For Policymakers

Relevant to discussions about:
- Accreditation standards
- Student loan policies
- Educational equity and access
- Outcome-based accountability

## Transferable Analytics Skills

While this project focused on legal education rather than healthcare, it developed skills directly applicable to healthcare analytics:

### Cross-Sector Application

1. **Outcome Prediction**: Modeling completion/success rates transfers to patient outcomes
2. **Multivariate Methods**: Controlling for confounders applies across domains
3. **Data Integration**: Merging disparate sources is universal analytical challenge
4. **Policy Translation**: Communicating findings to decision-makers transcends sector

### Analytical Rigor

The same statistical principles apply whether analyzing:
- Educational outcomes
- Patient outcomes
- Operational metrics
- Quality indicators

### Domain Agnosticism of Methods

This project reinforced that strong analytical skills transfer across domains. What varies is:
- Subject matter expertise
- Relevant confounders
- Policy context
- Stakeholder interests

But the core analytical approach—careful specification, rigorous diagnostics, transparent communication—remains constant.

## Reflections

### On Cross-Disciplinary Research

Working outside my primary domain (healthcare) was valuable:
- Broadened perspective on social policy research
- Reinforced transferability of analytical methods
- Developed ability to quickly gain domain knowledge
- Enhanced communication skills for diverse audiences

### On Educational Analytics

This project revealed parallels between educational and healthcare analytics:
- Both involve predicting and improving human outcomes
- Both require balancing multiple stakeholder interests
- Both face challenges in causal inference
- Both have significant equity implications

### On Statistical Practice

Reinforced several principles of good statistical practice:
- Diagnostics are not optional
- Multiple model specifications test robustness
- Effect sizes matter as much as p-values
- Visualizations aid understanding and communication

## Connection to Healthcare Analytics

The methodological skills developed here translate directly:

- **Risk Adjustment**: Similar to controlling for baseline patient characteristics
- **Outcome Prediction**: Like predicting patient outcomes or readmissions
- **Quality Measurement**: Analogous to measuring institutional quality metrics
- **Policy Analysis**: Informing program design whether in education or healthcare

## Conclusion

This law school graduation rate analysis demonstrated the power of multivariate regression methods to identify factors associated with educational outcomes. While the domain was legal education, the analytical approaches, statistical methods, and communication challenges mirror those in healthcare analytics.

The project reinforced core principles:
- Rigorous methods are domain-agnostic
- Context matters enormously for interpretation
- Statistical findings must translate to actionable insights
- Transparent reporting of limitations builds credibility

These lessons continue to inform my approach to healthcare analytics—applying sophisticated statistical methods while maintaining clear communication and appropriate humility about what data can and cannot tell us.

The work exemplified how analytical skills develop through diverse applications, with each project building capacity that transfers to future challenges across domains.
