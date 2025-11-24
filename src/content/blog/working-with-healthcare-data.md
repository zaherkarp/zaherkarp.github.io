---
title: "Working with Healthcare Data: Lessons Learned"
description: "Key insights and best practices from years of working with electronic health records and clinical data."
publishDate: 2025-01-20
tags: ["healthcare", "data engineering", "best practices"]
---

After years of working with healthcare data across various EHR systems like Epic, Cerner, and athenahealth, I've learned several important lessons that I wish someone had told me when I started.

## Understanding the Data Model

Healthcare data is inherently complex. Unlike traditional business data, EHR data models reflect the messy reality of clinical care:

- **Temporal complexity**: Everything has timestamps, but determining "when" something happened can be surprisingly difficult
- **Multiple sources of truth**: The same clinical concept might appear in different tables with subtle differences
- **Denormalization**: Many EHR analytics databases are heavily denormalized for query performance

## Common Pitfalls

### 1. Assuming Data Quality

Never assume data is clean or complete. Always:

- Check for nulls and unexpected values
- Validate date ranges
- Look for duplicate records
- Understand how deletions and updates are handled

### 2. Ignoring Temporal Relationships

```sql
-- Don't do this
SELECT COUNT(*) FROM encounters
WHERE diagnosis_code = 'E11.9'

-- Do this instead
SELECT COUNT(DISTINCT patient_id)
FROM encounters e
INNER JOIN diagnoses d ON e.encounter_id = d.encounter_id
WHERE d.diagnosis_code = 'E11.9'
  AND d.diagnosis_datetime BETWEEN e.check_in_time AND e.check_out_time
```

### 3. Not Understanding Your Denominator

In healthcare analytics, the denominator matters enormously. Are you calculating rates based on:

- Active patients?
- Patients with visits in the last year?
- Patients in a specific panel?

The choice dramatically affects your results and interpretation.

## Best Practices

1. **Document assumptions**: Healthcare data requires many assumptions. Write them down.
2. **Version your queries**: SQL queries are code. Treat them accordingly.
3. **Test against known cases**: Find patients whose records you understand and verify your queries return expected results.
4. **Collaborate with clinicians**: They understand the clinical context you might miss.

## Tools That Help

Over the years, I've found these tools invaluable:

- **dbt**: For transformation logic and documentation
- **Great Expectations**: For data quality testing
- **SQL formatter**: Readable SQL is maintainable SQL
- **Version control**: Always. No exceptions.

## Conclusion

Working with healthcare data is challenging but rewarding. The key is approaching it with humility, rigorous testing, and collaboration with clinical stakeholders.

What lessons have you learned working with healthcare data? I'd love to hear from you!
