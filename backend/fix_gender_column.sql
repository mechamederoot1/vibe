-- =====================================================
-- CORREÇÃO URGENTE - COLUNA GENDER
-- Vibe Social Network
-- =====================================================

-- Verificar estrutura atual da coluna gender
DESCRIBE users;

-- Mostrar valores atuais (se houver dados)
SELECT DISTINCT gender FROM users WHERE gender IS NOT NULL;

-- Corrigir a coluna gender para suportar 'prefer_not_to_say'
ALTER TABLE users 
MODIFY COLUMN gender ENUM('male', 'female', 'other', 'prefer_not_to_say') 
DEFAULT NULL;

-- Verificar se a correção foi aplicada
DESCRIBE users;

-- Mostrar a nova definição da coluna
SHOW CREATE TABLE users;

-- =====================================================
-- VERIFICAÇÃO DE FUNCIONALIDADE
-- =====================================================

-- Testar inserção com todos os valores possíveis
-- (Remover após teste)
/*
INSERT INTO users (display_id, first_name, last_name, email, password_hash, gender) 
VALUES 
('test001', 'Test', 'Male', 'test_male@test.com', 'hash123', 'male'),
('test002', 'Test', 'Female', 'test_female@test.com', 'hash123', 'female'),
('test003', 'Test', 'Other', 'test_other@test.com', 'hash123', 'other'),
('test004', 'Test', 'Prefer', 'test_prefer@test.com', 'hash123', 'prefer_not_to_say');

-- Verificar se as inserções funcionaram
SELECT first_name, gender FROM users WHERE email LIKE 'test_%@test.com';

-- Limpar dados de teste
DELETE FROM users WHERE email LIKE 'test_%@test.com';
*/

SELECT 'Gender column fix completed successfully!' as status;
