async def m001_add_satspot(db):
    """
    Creates a hash check table.
    """
    await db.execute(
        f"""
        CREATE TABLE satspot.satspot (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            wallet TEXT NOT NULL,
            "user" TEXT NOT NULL,
            haircut INTEGER NOT NULL DEFAULT 5 CHECK(haircut <= 50),
            closing_date TIMESTAMP NOT NULL,
            buy_in INTEGER NOT NULL,
            players TEXT NOT NULL,
            completed BOOLEAN,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
        """
    )
