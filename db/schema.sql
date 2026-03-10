-- =========================
-- USERS TABLE
-- =========================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password TEXT NOT NULL
);


-- =========================
-- SESSIONS TABLE
-- =========================

CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    title TEXT,
    CONSTRAINT sessions_user_id_fkey
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id
ON sessions(user_id);


-- =========================
-- MESSAGES TABLE
-- =========================

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT messages_session_id_fkey
        FOREIGN KEY (session_id)
        REFERENCES sessions(id)
        ON DELETE CASCADE,

    CONSTRAINT messages_role_check
        CHECK (role IN ('user', 'assistant', 'system'))
);

CREATE INDEX IF NOT EXISTS idx_messages_session_id
ON messages(session_id);


-- =========================
-- TICKERS TABLE
-- =========================

CREATE TABLE IF NOT EXISTS tickers (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_symbol
ON tickers(symbol);

CREATE INDEX IF NOT EXISTS idx_name
ON tickers(name);


-- =========================
-- EARNINGS TABLE
-- =========================

CREATE TABLE IF NOT EXISTS earnings (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    eps DECIMAL(4,2),
    year TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_earnings_symbol ON earnings(symbol);


-- =========================
-- SHARES TABLE
-- =========================

CREATE TABLE IF NOT EXISTS shares (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    diluted BIGINT,
    basic BIGINT,
    date TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_shares_symbol ON shares(symbol);


-- =========================
-- CASHFLOW TABLE
-- =========================

CREATE TABLE IF NOT EXISTS cashflow (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date TIMESTAMP,                             -- reporting year/quarter
    operating_cashflow BIGINT,                  -- core business cash generation
    capital_expenditures BIGINT,                -- company investment in assets
    cashflow_investing BIGINT,                  -- investing activities cash flow
    cashflow_financing BIGINT,                  -- financing activities cash flow
    dividend_payout BIGINT,                     -- shareholder returns
    stock_based_compensation BIGINT,            -- employee compensation via stock
    net_income BIGINT,                          -- company profitability
);

CREATE INDEX IF NOT EXISTS idx_cashflow_symbol ON cashflow(symbol);


-- =========================
-- INCOME STATEMENT TABLE
-- =========================

CREATE TABLE IF NOT EXISTS income_statement (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date TIMESTAMP,
    gross_profit BIGINT,
    total_revenue BIGINT,
    cost_of_revenue BIGINT,
    operating_income BIGINT,
    research_and_development BIGINT,
    operating_expenses BIGINT,
    income_before_tax BIGINT,
    income_tax_expense BIGINT,
    ebit BIGINT,
    ebitda BIGINT,
    net_income BIGINT
);

CREATE INDEX IF NOT EXISTS idx_income_statement_symbol ON income_statement(symbol);


-- =========================
-- BALANCE SHEET TABLE
-- =========================

CREATE TABLE IF NOT EXISTS balance_sheet (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date TIMESTAMP,
    total_assets BIGINT,
    total_current_assets BIGINT,
    cash_equivalents BIGINT,
    inventory BIGINT,
    net_receivables BIGINT,
    property_plant_equipment BIGINT,
    intangible_assets BIGINT,
    goodwill BIGINT,
    total_liabilities BIGINT,
    total_current_liabilities BIGINT,
    long_term_debt BIGINT,
    short_term_debt BIGINT,
    shareholder_equity BIGINT,
    retained_earnings BIGINT,
    shares_outstanding BIGINT
);

CREATE INDEX IF NOT EXISTS idx_balance_sheet_symbol ON balance_sheet(symbol);


-- =========================
-- CRYPTO PRICES TABLE
-- =========================

CREATE TABLE IF NOT EXISTS crypto (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    market VARCHAR(10),
    date TIMESTAMP,
    open_price DECIMAL(10,3),
    high_price DECIMAL(10,3),
    low_price DECIMAL(10,3),
    close_price DECIMAL(10,3),
    volume DECIMAL(10,3)
);

CREATE INDEX IF NOT EXISTS idx_crypto_symbol ON crypto(symbol);