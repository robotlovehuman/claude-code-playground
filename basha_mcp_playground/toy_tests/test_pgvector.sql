-- Phase 0: Toy pgvector test
-- Testing: Basic vector functionality with 3D vectors
-- Goal: Verify pgvector works with simple, understandable data

-- Create test database
-- Run: createdb toy_vector_test
-- Then: psql -d toy_vector_test

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create super simple table with 3D vectors
CREATE TABLE toy_vectors (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    embedding vector(3)  -- Just 3 dimensions for easy understanding!
);

-- Insert toy data representing simple concepts
-- Think of dimensions as: [cuteness, size, water-affinity]
INSERT INTO toy_vectors (name, description, embedding) VALUES 
    ('cat', 'Furry pet, medium size, dislikes water', '[0.9, 0.5, 0.1]'),
    ('dog', 'Loyal pet, varies in size, some like water', '[0.8, 0.6, 0.5]'),
    ('fish', 'Aquatic pet, small, loves water', '[0.3, 0.2, 1.0]'),
    ('hamster', 'Tiny pet, very small, avoids water', '[0.7, 0.1, 0.1]'),
    ('dolphin', 'Smart mammal, large, lives in water', '[0.6, 0.9, 1.0]');

-- Test 1: Basic retrieval
SELECT name, embedding FROM toy_vectors;

-- Test 2: Find similar to a cat (high cuteness, medium size, low water)
SELECT 
    name,
    embedding,
    embedding <-> '[0.9, 0.5, 0.1]' AS l2_distance,
    ROUND((embedding <-> '[0.9, 0.5, 0.1]')::numeric, 3) AS distance_rounded
FROM toy_vectors 
ORDER BY l2_distance
LIMIT 3;

-- Test 3: Find water-loving animals (high water-affinity)
SELECT 
    name,
    description,
    embedding,
    embedding <-> '[0, 0, 1]' AS distance_to_water_lover
FROM toy_vectors 
ORDER BY distance_to_water_lover
LIMIT 3;

-- Test 4: Test different distance metrics
SELECT 
    name,
    embedding <-> '[0.5, 0.5, 0.5]' AS l2_distance,
    embedding <#> '[0.5, 0.5, 0.5]' AS inner_product,
    embedding <=> '[0.5, 0.5, 0.5]' AS cosine_distance
FROM toy_vectors
ORDER BY l2_distance;

-- Test 5: Aggregate functions
SELECT 
    AVG(embedding) AS average_vector,
    COUNT(*) as total_animals
FROM toy_vectors;

-- Expected results to verify:
-- 1. Cat should be most similar to itself (distance 0)
-- 2. Dog should be second most similar to cat
-- 3. Fish and dolphin should be most water-loving
-- 4. All distance metrics should work
-- 5. Can compute average vectors