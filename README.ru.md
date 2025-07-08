Когда-нибудь заполню

Настройка тригера для вычисления вектора поиска в БД

# Создание ф-ции подсчета вектора
```
CREATE OR REPLACE FUNCTION update_title_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('russian', COALESCE(NEW.name_ru, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.name_en, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

# Создание тригера обновления
```
CREATE TRIGGER title_search_vector_update
    BEFORE INSERT OR UPDATE ON titles
    FOR EACH ROW
    EXECUTE FUNCTION update_title_search_vector();
```

# Создание индексов

```
CREATE INDEX idx_title_search_vector ON titles USING GIN(search_vector);
```

## Устанавливаем EXTENSION
```
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```
## И добавляем Индексы
```
CREATE INDEX idx_title_name_ru_trigram ON titles USING GIN(name_ru gin_trgm_ops);
CREATE INDEX idx_title_name_en_trigram ON titles USING GIN(name_en gin_trgm_ops);
```

# Обновляем записи
```
SELECT COUNT(*) FROM titles;

DO $$
DECLARE
    batch_size INTEGER := 10000;
    total_rows INTEGER;
    processed INTEGER := 0;
BEGIN
    SELECT COUNT(*) INTO total_rows FROM titles;
    
    WHILE processed < total_rows LOOP
        UPDATE titles 
        SET search_vector = 
            setweight(to_tsvector('russian', COALESCE(name_ru, '')), 'A') ||
            setweight(to_tsvector('english', COALESCE(name_en, '')), 'B')
        WHERE id IN (
            SELECT id FROM titles 
            WHERE search_vector IS NULL 
            OR search_vector = ''
            LIMIT batch_size
        );
        
        processed := processed + batch_size;
        RAISE NOTICE 'Processed: % / %', processed, total_rows;
        
        PERFORM pg_sleep(0.1);
    END LOOP;
END $$;
```