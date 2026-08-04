# Dataset Acquisition

The Olist Brazilian E-Commerce dataset is not redistributed in this
repository. Use this documented setup sequence:

1. Clone the repository:

   ```bash
   git clone <repo>
   ```

2. Create local environment files:

   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. Download the dataset using either option:

   - Manual: download it from
     [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
     and place all nine CSV files in `data/raw/`.
   - Automated: set `KAGGLE_USERNAME` and `KAGGLE_KEY`, then run:

     ```bash
     make download-data
     ```

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

During Phase 1, `download-data`, `etl`, `analytics-reports`, and `train` are
stable interface placeholders and do not perform their later-phase work.
