# Data Analytics & Communication Assignments

[![CI](https://github.com/RajdipDhar2007/data-analytics-assignments/actions/workflows/ci.yml/badge.svg)](https://github.com/RajdipDhar2007/data-analytics-assignments/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-FF4B4B)

My submissions for Assignments 1 to 4: two Streamlit apps (a COVID-19 dashboard and a CSV ingestion page) and two Word write-ups on explaining results and professional communication. The assignment text below is reproduced as given; each one has a **My submission** section underneath it.

**Jump to:** [Assignment 1](#assignment-1-covid-19-dashboard) · [Assignment 2](#assignment-2-ingestion-page) · [Assignment 3](#assignment-3-explain-a-result-in-30-seconds) · [Assignment 4](#assignment-4-apply-the-pyramid-principle-and-the-7-cs) · [Quick start](#quick-start) · [Repository structure](#repository-structure)

---

## Assignments

> **Tools:** Use **Streamlit** and **ReportLab** for Assignments 1 and 2. Use **MS Word** for Assignments 3 and 4.

---

### Assignment 1: COVID-19 Dashboard

Create a dashboard using a COVID-19 dataset from [Kaggle Datasets](https://www.kaggle.com/datasets) that includes:

- Bar chart
- Line chart
- Pie chart

#### ✅ My submission

**Folder:** [`Assignment_1_COVID_Dashboard/`](Assignment_1_COVID_Dashboard/) · Streamlit + ReportLab · [dashboard README](Assignment_1_COVID_Dashboard/README.md)

```bash
streamlit run Assignment_1_COVID_Dashboard/app.py
```

| Bar chart | Line chart | Pie chart |
|---|---|---|
| <img src="docs/images/dashboard_bar.png" width="280"> | <img src="docs/images/dashboard_line.png" width="280"> | <img src="docs/images/dashboard_pie.png" width="280"> |

*Charts exactly as the dashboard draws them. A sample PDF export is in [`sample_outputs/`](sample_outputs/covid19_dashboard_report.pdf).*

---

### Assignment 2: Ingestion Page

Create an ingestion page which:

- Handles file uploading
- Uploads a CSV file to a database
- Generates a summary report using ReportLab

#### ✅ My submission

**Folder:** [`Assignment_2_Ingestion_Page/`](Assignment_2_Ingestion_Page/) · Streamlit + SQLite + ReportLab · [ingestion README](Assignment_2_Ingestion_Page/README.md)

```bash
streamlit run Assignment_2_Ingestion_Page/app.py
```

<img src="docs/images/ingestion_report.png" width="320" alt="First page of the generated ingestion summary report">

*First page of the PDF summary report the page generates. Full sample: [`sample_outputs/ingestion_summary_country_wise_latest.pdf`](sample_outputs/ingestion_summary_country_wise_latest.pdf).*

---

### Assignment 3: Explain a Result in 30 Seconds

**Mini activity:** Pair up, practise, and give one kind, specific suggestion.

#### Scenario

Your model predicts whether a customer will leave a service.

#### Your Result

| Metric | Value |
|---|---|
| Recall | 82% |
| Precision | 69% |
| Baseline recall | 70% |

#### Your Task

Explain:

1. What improved
2. What the trade-off is
3. Why it matters

#### Peer Feedback

- Was it clear?
- Was it accurate?
- Was the next step obvious?

#### Challenge

Explain it to a non-technical manager, without saying "the algorithm is better."

#### ✅ My submission

**Document (MS Word):** [`Assignment_3_Explain_a_Result_in_30_Seconds.docx`](Assignment_3_Explain_a_Result/Assignment_3_Explain_a_Result_in_30_Seconds.docx)

In short: the model now catches 82 of every 100 customers who are about to leave, up from 70. The price is that roughly 3 in 10 flagged customers would have stayed anyway. The document also has the version for a non-technical manager and a peer-feedback table.

---

### Assignment 4: Apply the Pyramid Principle and the 7 Cs

#### A1. Pyramid Principle Exercise

**Task:** Take a small dataset or case study and prepare a pyramid-structured explanation:

**Headline → Supporting points → Evidence → Details**

**Learning outcome:** Storytelling with data

#### A2. Communication Etiquette with 7 Cs

**Task:** Draft an email to convey information (for example, rescheduling a meeting, sharing an update, or requesting documents). Ensure the draft follows the 7 Cs of communication.

**Learning outcome:** Strengthen professional communication in formal contexts

#### ✅ My submission

**Documents (MS Word):**

- **A1, Pyramid Principle:** [`Assignment_4A_Pyramid_Principle.docx`](Assignment_4_Pyramid_and_7Cs/Assignment_4A_Pyramid_Principle.docx), a case study on coding by AI, structured Headline → Supporting points → Evidence → Details.
- **A2, 7 Cs email:** [`Assignment_4B_7Cs_Email.docx`](Assignment_4_Pyramid_and_7Cs/Assignment_4B_7Cs_Email.docx), a rescheduling email to Bidisha Dobe, with a note on how it meets each of the 7 Cs.

---

## Quick start

```bash
git clone https://github.com/RajdipDhar2007/data-analytics-assignments.git
cd data-analytics-assignments

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

streamlit run Assignment_1_COVID_Dashboard/app.py     # Assignment 1
streamlit run Assignment_2_Ingestion_Page/app.py      # Assignment 2
```

Run the automated tests with:

```bash
python -m unittest discover -s tests -v
```

## Repository structure

```
.
├── Assignment_1_COVID_Dashboard/     # Streamlit dashboard + ReportLab export
│   ├── app.py
│   ├── covid_charts.py
│   ├── data/                         # country_wise_latest.csv, full_grouped.csv
│   └── README.md
├── Assignment_2_Ingestion_Page/      # CSV -> SQLite ingestion + ReportLab report
│   ├── app.py
│   ├── ingest_core.py
│   ├── sample_data/
│   └── README.md
├── Assignment_3_Explain_a_Result/    # Word document
├── Assignment_4_Pyramid_and_7Cs/     # Word documents (4A and 4B)
├── sample_outputs/                   # example PDFs made by the two apps
├── docs/images/                      # images used in the READMEs
├── tests/                            # unit tests for both apps
├── .github/workflows/ci.yml          # runs the tests on every push
├── requirements.txt
├── LICENSE
└── .gitignore
```

## Data

The dashboard uses the COVID-19 dataset from [Kaggle Datasets](https://www.kaggle.com/datasets) (Johns Hopkins CSSE and Worldometer data, snapshot as of 27 July 2020). Only the two small files the dashboard needs are included. The data belongs to its original authors, so check the Kaggle page for its licence terms.

## Author

**Rajdip Dhar** · [@RajdipDhar2007](https://github.com/RajdipDhar2007)

## License

The code in this repository is released under the [MIT License](LICENSE).
