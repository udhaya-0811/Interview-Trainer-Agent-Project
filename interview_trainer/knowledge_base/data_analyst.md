# Data Analyst Interview Knowledge Base
# Role: Data Analyst | Category: Technical

---
## Q1 | difficulty: beginner
**Question:** What is the difference between a data analyst, data scientist, and data engineer?

**Answer:**
- **Data Analyst:** focuses on interpreting existing data to answer business questions using SQL, Excel, Tableau/Power BI, and basic statistics. Output: dashboards, reports, recommendations.
- **Data Scientist:** builds predictive/prescriptive models (ML, statistical modelling), requires Python/R proficiency, stronger maths background. Output: models, insights, prototypes.
- **Data Engineer:** builds and maintains data infrastructure (pipelines, warehouses, lakes). Tools: Spark, Airflow, dbt, Kafka. Output: reliable, scalable data infrastructure.
In practice, roles overlap and many companies use "data analyst" broadly.

---
## Q2 | difficulty: beginner
**Question:** What are different types of SQL JOINs? Explain with examples.

**Answer:**
- **INNER JOIN:** returns rows with matching keys in both tables.
- **LEFT (OUTER) JOIN:** all rows from left table, NULL for non-matching right rows.
- **RIGHT JOIN:** all rows from right table, NULL for non-matching left rows.
- **FULL OUTER JOIN:** all rows from both tables; NULL where no match.
- **CROSS JOIN:** cartesian product (every combination).
- **SELF JOIN:** join a table to itself (e.g., employee-manager hierarchy).
Example: `SELECT o.id, c.name FROM orders o LEFT JOIN customers c ON o.customer_id = c.id` returns all orders including those without a matching customer.

---
## Q3 | difficulty: intermediate
**Question:** What are window functions in SQL? Give examples.

**Answer:**
Window functions perform calculations across a set of rows related to the current row without collapsing the result.
```sql
SELECT
    employee_id,
    department,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg,
    SUM(salary) OVER (ORDER BY hire_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM employees;
```
Common window functions: `RANK()`, `DENSE_RANK()`, `ROW_NUMBER()`, `LAG()`, `LEAD()`, `FIRST_VALUE()`, `LAST_VALUE()`, `SUM()`, `AVG()`.
`PARTITION BY` is like GROUP BY but preserves individual rows.

---
## Q4 | difficulty: intermediate
**Question:** What is data normalisation? Explain 1NF, 2NF, 3NF.

**Answer:**
Normalisation organises relational data to reduce redundancy and improve integrity.
- **1NF (First Normal Form):** atomic values (no repeating groups/arrays), unique rows, primary key exists.
- **2NF:** 1NF + no partial dependencies (non-key columns must depend on the full composite primary key, not just part of it).
- **3NF:** 2NF + no transitive dependencies (non-key columns depend only on the primary key, not on other non-key columns).
- **BCNF (Boyce-Codd NF):** stricter 3NF; every determinant must be a candidate key.
Denormalisation: intentional redundancy for read performance (star schema in data warehouses).

---
## Q5 | difficulty: intermediate
**Question:** What is the difference between OLTP and OLAP systems?

**Answer:**
| Feature | OLTP | OLAP |
|---|---|---|
| Purpose | Transactional operations | Analytical queries |
| Query type | Simple, many small R/W | Complex, aggregations, historical |
| Optimisation | Write throughput, row-based | Read throughput, column-based |
| Schema | Normalised (3NF) | Denormalised (star/snowflake) |
| Examples | MySQL, PostgreSQL, Oracle | Redshift, BigQuery, Snowflake, Teradata |
| Data volume | GB-TB | TB-PB |
OLAP systems use columnar storage for efficient aggregations and compression. ETL/ELT pipelines move data from OLTP to OLAP.

---
## Q6 | difficulty: intermediate
**Question:** Explain the star schema vs snowflake schema in data warehousing.

**Answer:**
**Star schema:** central fact table surrounded by denormalised dimension tables. Simple joins, faster queries, more storage.
**Snowflake schema:** dimensions are normalised into multiple related tables, forming a snowflake shape. More complex joins, saves storage, ensures consistency.
**Fact table:** contains measurable, quantitative data (sales_amount, quantity) and foreign keys to dimensions.
**Dimension table:** descriptive attributes (customer_name, product_category, date_hierarchy).
For BI/analytics, star schema is preferred for query simplicity and performance. Snowflake schema is preferred when storage is a constraint or data changes frequently.

---
## Q7 | difficulty: beginner
**Question:** What is data cleaning? What are common data quality issues?

**Answer:**
Data cleaning transforms raw, messy data into reliable, analysis-ready data.
Common issues:
1. **Missing values:** null/NaN. Handle with imputation (mean/median), deletion, or flagging.
2. **Duplicates:** redundant rows. Remove with `df.drop_duplicates()`.
3. **Inconsistent formats:** dates as strings in mixed formats, inconsistent capitalisation.
4. **Outliers:** extreme values due to errors or genuine anomalies. Use Z-score or IQR method.
5. **Wrong data types:** numbers stored as strings.
6. **Invalid values:** age=-5, email without @.
Rule of thumb: understand the source of data issues before blindly removing/imputing; incorrect cleaning introduces bias.

---
## Q8 | difficulty: intermediate
**Question:** What are the key Python libraries for data analysis and when to use each?

**Answer:**
- **NumPy:** numerical computing, n-dimensional arrays, vectorised operations. Foundation of Python data stack.
- **Pandas:** tabular data manipulation (DataFrames). Data loading, cleaning, grouping, merging.
- **Matplotlib/Seaborn:** static visualisations. Matplotlib for flexibility; Seaborn for attractive statistical plots.
- **Plotly:** interactive charts and dashboards.
- **Scikit-learn:** ML algorithms, preprocessing, model evaluation.
- **SciPy:** statistical tests, signal processing, optimisation.
- **SQLAlchemy:** database connectivity and ORM.
- **Dask:** parallel computation for larger-than-memory datasets.
Typical workflow: SQL/Pandas (ETL) → EDA (Seaborn/Plotly) → Modelling (sklearn) → Communication (Streamlit/Dash).

---
## Q9 | difficulty: intermediate
**Question:** What is A/B testing and how do you design one?

**Answer:**
A/B testing (controlled experiment) measures the effect of a change by randomly assigning users to control (A) and treatment (B) groups.
Design steps:
1. **Define hypothesis:** H₀ (no difference), H₁ (treatment has effect).
2. **Define metric:** primary KPI (conversion rate, CTR, revenue per user).
3. **Calculate sample size:** power analysis (statistical power ≥ 80%, significance level α=0.05).
4. **Run experiment:** equal random assignment; avoid novelty effect bias.
5. **Analyse:** two-sample t-test (continuous), chi-squared test (proportions); report p-value and confidence interval.
6. **Decision:** reject H₀ if p < α; consider practical significance (effect size), not just statistical significance.
Pitfalls: peeking (multiple testing), novelty effect, Simpson's paradox, sample ratio mismatch.

---
## Q10 | difficulty: advanced
**Question:** How do you build a BI dashboard? What are best practices?

**Answer:**
Dashboard design principles:
1. **Know your audience:** executives (KPI summary), analysts (drill-down), operations (real-time alerts).
2. **Define key metrics first:** avoid vanity metrics; focus on actionable, decision-relevant data.
3. **Choose the right chart:** time-series → line chart; comparison → bar chart; composition → pie/stacked bar; correlation → scatter; distribution → histogram/boxplot.
4. **Minimise cognitive load:** 5±2 visuals per page, clear titles, consistent colour palette.
5. **Interactivity:** filters, drill-through, tooltips; not decorative animations.
6. **Performance:** pre-aggregated tables, materialised views, data extracts for large datasets.
7. **Accessibility:** colour-blind-safe palettes, alt text.
Tools: Power BI (Microsoft ecosystem), Tableau (drag-and-drop rich), Looker (LookML, code-based), Streamlit (Python custom apps), Metabase (open-source).

---
## Q11 | difficulty: intermediate
**Question:** What is ETL vs ELT? Explain a typical data pipeline.

**Answer:**
- **ETL (Extract, Transform, Load):** transform data before loading into warehouse. Traditional; good for complex transformations, limited target storage.
- **ELT (Extract, Load, Transform):** load raw data first, transform in the warehouse using SQL. Modern; leverages cloud warehouse compute; enables re-transformation without re-extraction.
Typical ELT pipeline:
1. **Extract:** pull from source (API, databases, files) using tools like Fivetran, Airbyte, custom scripts.
2. **Load:** land raw data in data lake (S3, GCS) or warehouse staging area.
3. **Transform:** dbt models (SQL-based transformations, version-controlled, testable).
4. **Serve:** aggregated tables/views for BI tools.
Orchestration: Apache Airflow (DAGs), Prefect, Dagster.

---
## Q12 | difficulty: intermediate
**Question:** What are common statistical concepts a data analyst should know?

**Answer:**
- **Descriptive statistics:** mean, median, mode, variance, standard deviation, percentiles.
- **Probability distributions:** normal (bell curve), Poisson (event counts), binomial (binary outcomes).
- **Hypothesis testing:** null hypothesis, p-value, significance level (α), Type I/II errors, statistical power.
- **Correlation vs causation:** Pearson correlation (linear), Spearman (rank). Correlation ≠ causation; control for confounders.
- **Regression:** simple/multiple linear regression; interpret coefficients, R², p-values for predictors.
- **Central Limit Theorem:** sample means are normally distributed for large n, regardless of population distribution. Foundation of many statistical tests.
- **Confidence intervals:** range that contains the true parameter with given probability.

---
## Q13 | difficulty: advanced
**Question:** How do you handle time series data? What are common methods for forecasting?

**Answer:**
Time series properties:
- **Trend:** long-term upward/downward movement.
- **Seasonality:** recurring patterns (weekly, monthly, annual).
- **Cyclicality:** irregular, multi-year business cycles.
- **Noise:** random fluctuations.
Stationarity: mean and variance constant over time. Required by many models. Test with ADF (Augmented Dickey-Fuller) test. Achieve via differencing, log-transform.
Forecasting methods:
- **ARIMA:** autoregressive + differencing + moving average. Good for stationary, univariate.
- **SARIMA:** ARIMA + seasonal component.
- **Exponential smoothing (ETS):** weighted avg of past observations; Holt-Winters for trend+seasonality.
- **Prophet (Meta):** additive model; handles holidays and changepoints; robust to missing data.
- **ML methods:** XGBoost/LGBM with lag features, LSTM, Transformer-based models.

---
## Q14 | difficulty: intermediate
**Question:** What is data governance and why is it important?

**Answer:**
Data governance is the framework for managing data availability, usability, integrity, and security across an organisation.
Key components:
- **Data catalogue:** inventory of all data assets with metadata, lineage, descriptions.
- **Data quality:** validation rules, freshness checks, anomaly detection.
- **Data lineage:** tracks data origin and transformations for audit and debugging.
- **Access control:** role-based access, PII masking, GDPR/HIPAA compliance.
- **Master Data Management (MDM):** single source of truth for key entities (customer, product).
Tools: Apache Atlas, Alation, Collibra, dbt (documentation + tests), IBM Watson Knowledge Catalog.
Why it matters: regulatory compliance, trustworthy decisions, reduced data swamps.

---
## Q15 | difficulty: beginner
**Question:** What is the difference between mean, median, and mode? When to use each?

**Answer:**
- **Mean** (average): sum/count. Sensitive to outliers. Use for symmetric distributions without extreme values.
- **Median:** middle value when sorted. Robust to outliers. Use for skewed distributions (income, house prices).
- **Mode:** most frequent value. Use for categorical data or to identify most common occurrence.
Example: if 9 employees earn $50K and 1 earns $500K, mean = $95K (misleading); median = $50K (representative).
A distribution with mean > median is right-skewed (long tail on right); mean < median is left-skewed.

---
## Q16 | difficulty: intermediate
**Question:** Explain GROUP BY vs HAVING in SQL.

**Answer:**
- **GROUP BY** aggregates rows with the same value in specified columns. Use aggregate functions (SUM, COUNT, AVG) in SELECT.
- **HAVING** filters groups after aggregation (like WHERE but for aggregated results).
```sql
SELECT department, COUNT(*) AS emp_count, AVG(salary) AS avg_sal
FROM employees
WHERE status = 'active'          -- filters rows BEFORE grouping
GROUP BY department
HAVING COUNT(*) > 5              -- filters groups AFTER aggregation
ORDER BY avg_sal DESC;
```
Rule: use WHERE to filter rows before grouping; use HAVING to filter aggregated groups.

---
## Q17 | difficulty: advanced
**Question:** What are CTEs (Common Table Expressions) and recursive CTEs?

**Answer:**
CTEs define named temporary result sets within a query, improving readability and enabling recursion.
```sql
WITH monthly_sales AS (
    SELECT DATE_TRUNC('month', order_date) AS month, SUM(amount) AS total
    FROM orders GROUP BY 1
),
ranked AS (
    SELECT *, RANK() OVER (ORDER BY total DESC) AS rnk FROM monthly_sales
)
SELECT * FROM ranked WHERE rnk <= 3;
```
**Recursive CTEs:** reference themselves for hierarchical data (org charts, bill of materials).
```sql
WITH RECURSIVE org AS (
    SELECT id, name, manager_id, 0 AS level FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.manager_id, o.level + 1
    FROM employees e JOIN org o ON e.manager_id = o.id
)
SELECT * FROM org ORDER BY level;
```

---
## Q18 | difficulty: intermediate
**Question:** What is data visualisation best practice for storytelling?

**Answer:**
Data storytelling framework:
1. **Context:** who is the audience? What decision is being supported?
2. **Data:** find the insight, not just present numbers.
3. **Narrative:** craft a clear message (title = takeaway, not "Chart 1").
4. **Visualisation:** choose chart type that best shows the insight.
Chart selection guide:
- **Bar chart:** comparing categories.
- **Line chart:** trends over time.
- **Scatter plot:** correlation between two variables.
- **Heatmap:** matrix relationships, correlation matrices.
- **Boxplot:** distribution comparison across groups.
Best practices: remove chart junk (gridlines, unnecessary labels), use pre-attentive attributes (colour, size) to highlight insight, one insight per chart, start y-axis at zero for bar charts.

---
## Q19 | difficulty: beginner
**Question:** What is an outlier? How do you detect and handle it?

**Answer:**
An outlier is an observation significantly different from other data points. It can be due to data entry errors, genuine anomalies, or natural variation.
Detection methods:
- **Z-score:** |z| > 3 (3 standard deviations from mean). Assumes normality.
- **IQR method:** values below Q1 - 1.5×IQR or above Q3 + 1.5×IQR are outliers. Robust to non-normal distributions.
- **Visual:** box plots, scatter plots.
Handling strategies:
- **Remove:** if clearly a data error.
- **Cap (Winsorize):** replace with 95th/5th percentile value.
- **Impute:** treat as missing value.
- **Keep:** if outliers represent genuine extreme values that matter (fraud detection, VIP customers).
Always investigate the cause before removing.

---
## Q20 | difficulty: intermediate
**Question:** What is the difference between left join and subquery? When to use each?

**Answer:**
Both can achieve similar results but have different use cases:
- **LEFT JOIN:** efficient for one-to-many relationships; preserves all left table rows; may duplicate rows if multiple matches exist.
- **Subquery (correlated):** runs once per row of outer query; can be slower for large tables.
- **EXISTS subquery:** often faster than IN for large sets; stops at first match.
```sql
-- LEFT JOIN approach (check for existence)
SELECT c.* FROM customers c LEFT JOIN orders o ON c.id = o.customer_id WHERE o.id IS NULL;

-- NOT EXISTS approach (often more efficient)
SELECT * FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
```
Modern query optimisers often rewrite subqueries as joins, but EXISTS is generally preferred for existence checks.

---
## Q21 | difficulty: advanced
**Question:** How do you optimise a slow SQL query?

**Answer:**
Optimisation steps:
1. **EXPLAIN / EXPLAIN ANALYZE:** understand query plan; look for sequential scans on large tables.
2. **Add indexes:** on columns used in WHERE, JOIN ON, ORDER BY. Composite indexes for multi-column filters.
3. **Avoid SELECT *:** select only needed columns; reduces I/O.
4. **Filter early:** apply WHERE before JOIN where possible; push predicates into subqueries.
5. **Avoid functions on indexed columns:** `WHERE YEAR(date) = 2023` prevents index use; use range: `WHERE date BETWEEN '2023-01-01' AND '2023-12-31'`.
6. **Materialised views:** pre-compute expensive aggregations.
7. **Partitioning:** partition large tables by date; queries on recent partitions skip older ones.
8. **Analyse statistics:** run ANALYZE (PostgreSQL) to update planner statistics.

---
## Q22 | difficulty: intermediate
**Question:** What is Pandas? Explain key operations.

**Answer:**
Pandas is a Python library for data manipulation using DataFrames (2D labelled tabular data) and Series (1D labelled array).
Key operations:
```python
import pandas as pd
df = pd.read_csv("data.csv")
df.info()                          # dtypes, null counts
df.describe()                      # summary statistics
df.isnull().sum()                  # missing value count per column
df = df.dropna(subset=["salary"]) # drop rows with null salary
df["salary"] = df["salary"].fillna(df["salary"].median())
df_grouped = df.groupby("dept")["salary"].agg(["mean","max","count"])
df_merged = df.merge(dept_df, on="dept_id", how="left")
df.pivot_table(values="sales", index="region", columns="quarter", aggfunc="sum")
```
Performance tips: use vectorised operations (avoid `iterrows`), use `query()`, categorical dtype for low-cardinality strings.

---
## Q23 | difficulty: advanced
**Question:** What is Apache Spark and why is it used for big data analytics?

**Answer:**
Apache Spark is a distributed in-memory computing framework for large-scale data processing.
Key features:
- **In-memory processing:** 100x faster than Hadoop MapReduce for iterative ML algorithms.
- **Unified engine:** batch (Spark Core), SQL (Spark SQL), streaming (Structured Streaming), ML (MLlib), graph (GraphX).
- **Lazy evaluation:** Transformations (map, filter, join) are lazy; only executed when an Action (count, collect, write) is called.
- **Fault tolerance:** RDDs track lineage; can recompute lost partitions.
- **Language support:** Python (PySpark), Scala, Java, R, SQL.
Use cases: ETL on TB+ datasets, feature engineering for ML, real-time event processing.
Data analyst entry point: Spark SQL / PySpark DataFrames for querying large tables in a distributed warehouse.

---
## Q24 | difficulty: beginner
**Question:** How do you present data insights to non-technical stakeholders?

**Answer:**
Communication best practices:
1. **Lead with the insight, not the method:** "Revenue in Q3 dropped 15% due to customer churn in the SMB segment" vs "I ran a cohort analysis…"
2. **Use the simplest chart that conveys the message:** avoid complex visualisations that require explanation.
3. **Quantify the business impact:** translate technical findings into revenue, cost, risk, or customer impact.
4. **Anticipate questions:** prepare to explain how you arrived at the number, caveats, and confidence level.
5. **Tell a story structure:** context → conflict → resolution (recommendation).
6. **Avoid jargon:** p-value, regression, dimensionality reduction — translate to plain English.
7. **One slide, one insight:** don't pack too much; let visuals breathe.

---
## Q25 | difficulty: intermediate
**Question:** What is cohort analysis and when is it useful?

**Answer:**
Cohort analysis groups users by a shared characteristic (usually acquisition time) and tracks their behaviour over time.
Types:
- **Acquisition cohort:** users who signed up in the same week/month. Track retention over time.
- **Behavioural cohort:** users who performed a specific action.
Example: track Month 1, Month 2, Month 3 retention rates for users acquired in Jan vs Feb. Identify if a product change improved long-term retention.
SQL pattern:
```sql
SELECT cohort_month, months_since_signup, COUNT(DISTINCT user_id) AS active_users
FROM (
    SELECT u.id AS user_id, DATE_TRUNC('month', u.signup_date) AS cohort_month,
           DATEDIFF('month', u.signup_date, a.activity_date) AS months_since_signup
    FROM users u JOIN activity a ON u.id = a.user_id
) sub
GROUP BY 1, 2 ORDER BY 1, 2;
```
Used for: churn analysis, retention optimisation, measuring product-market fit.

---
## Q26 | difficulty: advanced
**Question:** What is dbt and how does it improve the analytics workflow?

**Answer:**
dbt (data build tool) is a SQL-first transformation framework that brings software engineering best practices to analytics.
Key features:
- **Models:** SELECT statements as `.sql` files; dbt materialises them as tables/views.
- **Lineage:** auto-builds DAG of model dependencies; `ref()` function creates dependencies.
- **Testing:** built-in tests (`unique`, `not_null`, `accepted_values`, `relationships`); custom tests with SQL.
- **Documentation:** auto-generates data docs from schema.yml; serves as living data catalogue.
- **Version control:** models in Git; enables CI/CD for analytics.
- **Snapshots:** SCD Type 2 (slowly changing dimensions) with built-in snapshot feature.
dbt + data warehouse (BigQuery/Snowflake/Redshift) + orchestrator (Airflow/dbt Cloud) = modern analytics stack.

---
## Q27 | difficulty: intermediate
**Question:** Explain ACID properties in databases.

**Answer:**
ACID ensures database transactions are processed reliably:
- **Atomicity:** a transaction is all-or-nothing. If any step fails, the entire transaction is rolled back.
- **Consistency:** a transaction brings the database from one valid state to another; all constraints (FK, check) must hold.
- **Isolation:** concurrent transactions execute as if sequential; intermediate states are not visible to others. Levels: READ UNCOMMITTED < READ COMMITTED < REPEATABLE READ < SERIALIZABLE.
- **Durability:** committed transactions persist even after system failure (WAL – Write-Ahead Log).
NoSQL databases often relax ACID for performance/scale (BASE: Basically Available, Soft state, Eventually consistent).

---
## Q28 | difficulty: beginner
**Question:** What is the difference between structured, semi-structured, and unstructured data?

**Answer:**
- **Structured data:** organised in rows and columns with a predefined schema. Examples: relational databases (MySQL), CSV files, spreadsheets. Easy to query with SQL.
- **Semi-structured data:** has some organisational structure but no strict schema. Examples: JSON, XML, YAML, Parquet, log files. Query with JSONPath, SparkSQL, or document DBs (MongoDB).
- **Unstructured data:** no predefined structure. Examples: text documents, images, audio, video. Requires NLP, CV, or specialised processing.
Modern data lakes store all three types; data warehouse typically houses structured data; data lakehouse (Delta Lake, Apache Iceberg) handles all three with ACID transactions.

---
## Q29 | difficulty: advanced
**Question:** How do you detect and handle data drift in production analytics pipelines?

**Answer:**
Data drift occurs when the statistical properties of production data change over time, degrading model/analytics quality.
Types:
- **Covariate drift:** input feature distribution changes.
- **Label drift:** target variable distribution changes.
- **Concept drift:** relationship between features and target changes.
Detection methods:
- **Statistical tests:** KS-test (continuous), chi-squared (categorical) between baseline and current windows.
- **PSI (Population Stability Index):** > 0.2 indicates significant drift.
- **Model performance monitoring:** accuracy/AUC degradation on labelled data.
Handling: automated retraining triggers, data freshness checks, alerting pipelines.
Tools: Evidently AI, Arize, WhyLogs, IBM Watson OpenScale/OpenPages.

---
## Q30 | difficulty: intermediate
**Question:** What are slowly changing dimensions (SCD) in data warehousing?

**Answer:**
SCD handles dimension attributes that change over time in a data warehouse.
- **SCD Type 1 (Overwrite):** update the record; no history preserved. Simple, but loses history. Use when history doesn't matter.
- **SCD Type 2 (Add row):** add a new row for each change with effective dates and is_current flag. Preserves full history. Most common. Increases table size.
- **SCD Type 3 (Add column):** add a "previous_value" column. Preserves only one historical value. Simple but limited history.
- **SCD Type 4:** use a separate history table. Fast current-value queries.
Example SCD Type 2 fields: `customer_id, name, address, start_date, end_date, is_current`.
dbt snapshots automate SCD Type 2 implementation.
