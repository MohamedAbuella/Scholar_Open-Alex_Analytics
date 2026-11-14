# OpenAlex Review Dashboard

[![Live Dashboard Preview](https://img.shields.io/badge/📊_Explore_Interactive_Dashboard-Click_Here-blue?style=for-the-badge)](https://MohamedAbuella.github.io/Scholar_Open-Alex_Analytics/)

A browser-based, client-side academic literature search and review dashboard powered by the free [OpenAlex API](https://openalex.org). It collects scholarly works for any search query or metadata filter, performs bibliometric profiling, NLP text mining, and Latent Dirichlet Allocation (LDA) topic modeling, and exports the highest-ranked papers as a clean `.bib` database.

---

## Key Features

- **Zero-Setup Client-Side Execution:** Runs directly in your browser using pure HTML5, CSS, and JavaScript—no backend server or Python environment required.
- **Live OpenAlex Search & Advanced Filtering:** Supports Boolean operators (`AND`, `OR`, `NOT`), exact phrases, wildcards (`*`), year ranges, and filters by author, affiliation, publication venue, country code, work type, and minimum citations.
- **Bibliometric & Outlier Profiling:** Automatically ranks top journals/conferences, leading authors, yearly publication counts, and annual citation outliers using the $1.5 \times \text{IQR}$ rule.
- **NLP Text Mining & Correlations:** Extracts top TF-IDF terms, frequent bigrams, domain abbreviations (via neighborhood-search matching), and pairwise word correlations.
- **Interactive LDA Topic Modeling:** Discovers 4, 6, 8, or 10 latent research topics directly in the browser with customizable re-runs and mean publication years.
- **Alignment Ranking & `.bib` Export:** Scores papers by corpus cosine similarity, query coverage, and citation rate, allowing one-click download of `.bib` files.

---

## 🛠️ How to Use

1. **Launch Online:** Click the **[Explore Interactive Dashboard](https://MohamedAbuella.github.io/Scholar_Open-Alex_Analytics/)** badge above to open the dashboard directly in your browser.
2. **Run Locally (Optional):** Clone this repository and open `OpenAlex Analytics/index.html` in any modern web browser.
3. **Search & Collect:** Enter a search query (or use the advanced filters), set your year range and maximum results, and click **"▶ Run search & analysis"**.
4. **Explore & Export:** Navigate through the sidebar tabs to inspect bibliometrics, text mining, and LDA topics, then click **"💾 Save .bib database"** to download your curated BibTeX file.

---

## License

This project is open-source and available under the [MIT License](LICENSE).
