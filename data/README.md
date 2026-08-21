# Dataset Acquisition

The Indian Store Data source is not redistributed in this repository. Use this
documented setup sequence:

1. Clone the repository:

   ```bash
   git clone https://github.com/ParthrChandurkar/Retail-IQ.git
   cd Retail-IQ
   ```

2. Create local environment files:

   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. Acquire `indian_store_data.csv` using either option:

   - Manual: download it from
     [Kaggle](https://www.kaggle.com/datasets/abuhumzakhan/store-data), extract
     the upstream `store_sales_data (2).csv`, rename it to
     `indian_store_data.csv`, and place it in `data/raw/`.
   - Automated: set `KAGGLE_USERNAME` and `KAGGLE_KEY`, then run:

     ```bash
     make download-data
     ```

   After extraction, `data/raw/` must contain exactly one dataset payload:
   `indian_store_data.csv`. The automated path performs the upstream filename
   normalization itself. The ETL does not read the Kaggle ZIP, duplicate copies,
   or any Olist-era CSV. Repository control files `.gitignore` and
   `.gitkeep` remain alongside the source payload.

   Verified M1 source identity:

   - Data rows: `100,000` (header excluded)
   - SHA-256: `df1dd4a0d6bd486d34499e87b249e875f2a03bc407f5ffdddddf34bea80e727e`

4. Start the services:

   ```bash
   docker compose up -d
   ```

5. Run ingestion and curation:

   ```bash
   make etl
   ```

6. Generate analytics reports:

   ```bash
   make analytics-reports
   ```

7. Train the selected model:

   ```bash
   make train
   ```

8. Open <http://localhost:3000>.

During migration M1, `make download-data` and `make etl` target Indian Store
Data. Marts, analytics, ML, API, and frontend migration are gated to M2 and
later phases.
