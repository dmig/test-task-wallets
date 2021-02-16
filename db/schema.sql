CREATE TABLE IF NOT EXISTS wallets (
    id INTEGER PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    balance DECIMAL(10, 5) NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    from_id INT NOT NULL REFERENCES wallets (id),
    to_id INT NOT NULL REFERENCES wallets (id),
    amount DECIMAL(10, 5) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    comment VARCHAR(64)
);
