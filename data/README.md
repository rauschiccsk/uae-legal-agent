# Adresárová štruktúra dát

## data/raw_documents/
Surové PDF dokumenty zo zákonov Spojených arabských emirátov. Sem sa ukladajú originálne súbory pred spracovaním.

## data/processed/
Spracované a očistené texty z PDF dokumentov. Obsahuje extrahovaný text pripravený na vytvorenie embeddings.

## data/embeddings/
ChromaDB vektorová databáza s embeddings z právnych dokumentov. Používa sa pre semantické vyhľadávanie.