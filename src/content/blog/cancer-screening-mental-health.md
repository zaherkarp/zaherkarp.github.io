---
title: "Cancer Prevention in Mental Health Populations"
description: "Examining cancer screening disparities in patients with severe mental illness using advanced statistical methods"
pubDate: 2024-07-05
tags: ["SAS", "Logistic Regression", "Population Health", "Healthcare Disparities", "Public Health"]
---

## The Healthcare Equity Challenge

Patients with severe mental illness face significant health disparities beyond their psychiatric conditions. One critical but often overlooked area is preventive cancer screening. Despite clear clinical guidelines, research has consistently shown that individuals with mental health conditions receive less preventive care.

This project aimed to quantify these disparities and identify factors associated with lower cancer screening rates in this vulnerable population.

## Research Question

**Do patients with co-morbid severe mental illness receive cancer prevention screening at the same rates as those without mental illness, after controlling for other health conditions?**

## Methodological Framework

### Population Definition

We needed to carefully define our cohorts:

- **Severe Mental Illness (SMI)**: Included schizophrenia, schizoaffective disorder, and bipolar disorder
- **Comparison Group**: Age and sex-matched patients without SMI
- **Cancer Screening**: Age-appropriate colorectal, breast, and cervical cancer screening per USPSTF guidelines

### The Elixhauser Comorbidity Index

A key methodological component was using the **Elixhauser Comorbidity Index**, which measures the burden of 31 different comorbid conditions. This was crucial because:

1. Patients with SMI often have higher rates of chronic conditions
2. Comorbidities affect both screening likelihood and clinical priorities
3. We needed to isolate the effect of mental illness from general health complexity

### Statistical Approach: Logistic Regression

We employed multivariable logistic regression to:

```sas
/* Simplified example */
proc logistic data=screening_data;
  class smi_status comorbidity_groups;
  model screening_received = smi_status age sex
                             comorbidity_score /
                             lackfit;
  oddsratio smi_status;
run;
```

This allowed us to estimate the independent association between SMI and screening receipt while controlling for:
- Age
- Sex
- Comorbidity burden
- Insurance status
- Healthcare utilization

## Data Sources and Preparation

### Electronic Health Record Data

Working with EHR data required extensive data wrangling:

- Identifying screening procedures from multiple coding systems (CPT, ICD)
- Determining age-appropriate screening windows
- Handling complex medication histories
- Validating mental health diagnoses

### SAS Programming

SAS was ideal for this project due to:
- Excellent handling of large healthcare datasets
- Robust statistical procedures (PROC LOGISTIC)
- Integration with institutional data warehouses
- Established methods for comorbidity index calculation

## Key Findings

Our analysis revealed significant disparities:

1. **Lower Screening Rates**: Patients with SMI had substantially lower odds of receiving recommended cancer screening, even after controlling for comorbidities

2. **Differential Effects by Screening Type**: Disparities were most pronounced for colonoscopy screening, likely due to procedural complexity and required follow-up

3. **Healthcare Utilization Paradox**: Despite higher overall healthcare utilization, SMI patients received less preventive care

4. **Comorbidity Impact**: The Elixhauser index showed that medical complexity alone didn't explain the screening gap

## Challenges in Health Disparities Research

### Challenge: Confounding by Indication

Patients with SMI might face legitimate clinical reasons for delayed screening:
- Medication interactions
- Difficulty with procedural sedation
- Complex care coordination needs

**Solution**: Carefully documented clinical exclusion criteria and conducted sensitivity analyses excluding patients with clear contraindications

### Challenge: Selection Bias

Patients engaged enough to be diagnosed with SMI might differ from the general population:
- More healthcare system interaction
- Better documentation of conditions
- Potentially different health-seeking behaviors

**Solution**: Multiple sensitivity analyses with different cohort definitions

### Challenge: Temporal Considerations

Screening guidelines changed during our study period:
- Updated age recommendations
- New screening modalities
- Evolving insurance coverage

**Solution**: Restricted analyses to specific guideline-concordant time periods

## Public Health Implications

This research contributed to understanding of healthcare equity by:

1. **Quantifying Disparities**: Provided concrete estimates of screening gaps
2. **Identifying Mechanisms**: Suggested that disparities persist even accounting for medical complexity
3. **Informing Interventions**: Highlighted need for targeted outreach to SMI populations
4. **Policy Relevance**: Supported arguments for integrated behavioral and physical health care

## Statistical Considerations

Important methodological points for future researchers:

### Model Specification
- Tested multiple functional forms for continuous variables
- Evaluated interaction terms (e.g., age × SMI status)
- Checked for collinearity among comorbidity variables

### Diagnostics
- Assessed goodness-of-fit using Hosmer-Lemeshow test
- Examined influential observations
- Validated results with different model specifications

### Interpretation
- Reported both odds ratios and predicted probabilities for interpretability
- Calculated number needed to screen to identify disparities in absolute terms
- Considered clinical significance alongside statistical significance

## Skills and Tools

This project developed expertise in:

- **SAS Programming**: Complex data manipulation, statistical modeling, macro development
- **Epidemiological Methods**: Cohort design, confounding control, bias assessment
- **Comorbidity Measurement**: Elixhauser and Charlson index implementation
- **Health Services Research**: Understanding healthcare delivery patterns
- **Statistical Inference**: Logistic regression, model diagnostics, sensitivity analysis

## Broader Impact

Beyond the immediate research findings, this work contributed to:

- Growing awareness of mental health-related health disparities
- Evidence base for integrated care models
- Quality improvement initiatives targeting preventive care in SMI populations
- Training in rigorous health services research methods

## Reflections

This project exemplified the power of administrative data and statistical methods to reveal health inequities. The combination of:
- Rich EHR data
- Robust comorbidity measurement
- Careful statistical modeling
- Deep understanding of clinical context

...allowed us to generate actionable insights about a vulnerable population.

It also reinforced that healthcare analytics has the potential not just to optimize operations, but to identify and address fundamental inequities in care delivery.

The work demonstrated that sophisticated analytical methods, applied thoughtfully to healthcare data, can reveal patterns that inform both clinical practice and health policy.
