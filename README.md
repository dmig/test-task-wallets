# test-task-wallets
## setup & run
1. execute `docker-compose up` in project folder
2. open http://127.0.0.1:8000/

## how it works
- there are 2 entities: wallets and transactions
- wallets can be listed/created/renamed/deleted (unless some transactions created)
- transactions can be listed, created and updated (comment only)
- on each transfer transaction created, there is 1 or 2 followup commission transactions
- commission can be charged to _sender_, _receiver_ or _both_
  - _sender_ - charges extra 1.5% of the _amount_
  - _receiver_ - deducts 1.5% from the _amount_
  - _both_ - charges _sender_ extra and deducts 0.75% from the _amount_

## limitations
- SQLite as a database (to reduce overall size and number of dependencies)
- `floats` used to store amounts (SQLite stores `NUMERIC` as `float` anyway) would likely cause some decimal precision issues (in the real world using MySQL/PostgreSQL and `Decilmal` type **or** completely integer-based calulations would resolve this)
