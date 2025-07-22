-- =====================================================
-- SCRIPT DE CONFIGURAÇÃO - RECUPERAÇÃO DE SENHA
-- Vibe Social Network
-- =====================================================

-- Criar tabela para tokens de recuperação de senha
CREATE TABLE IF NOT EXISTS password_recovery (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    recovery_token VARCHAR(64) NOT NULL UNIQUE,
    recovery_code VARCHAR(6) NOT NULL,
    expires_at DATETIME NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    used_at DATETIME NULL,
    attempts INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices para performance
    INDEX idx_user_id (user_id),
    INDEX idx_email (email),
    INDEX idx_recovery_token (recovery_token),
    INDEX idx_recovery_code (recovery_code),
    INDEX idx_expires_at (expires_at),
    INDEX idx_used (used),
    INDEX idx_created_at (created_at),
    
    -- Chave estrangeira
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabela de logs para auditoria de recuperação de senha
CREATE TABLE IF NOT EXISTS password_recovery_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    action_type ENUM('request', 'code_attempt', 'token_attempt', 'success', 'expired', 'failed') NOT NULL,
    recovery_id INT NULL,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    success BOOLEAN DEFAULT FALSE,
    error_message TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_user_id (user_id),
    INDEX idx_email (email),
    INDEX idx_action_type (action_type),
    INDEX idx_recovery_id (recovery_id),
    INDEX idx_success (success),
    INDEX idx_created_at (created_at),
    
    -- Chave estrangeira
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recovery_id) REFERENCES password_recovery(id) ON DELETE SET NULL
);

-- Limpar tokens expirados (procedure para limpeza automática)
DELIMITER //
CREATE PROCEDURE CleanExpiredPasswordRecoveryTokens()
BEGIN
    DELETE FROM password_recovery 
    WHERE expires_at < NOW() 
    AND used = FALSE;
    
    -- Log da limpeza
    INSERT INTO password_recovery_logs (user_id, email, action_type, success, error_message)
    SELECT 0, 'system', 'cleanup', TRUE, CONCAT('Removed ', ROW_COUNT(), ' expired tokens')
    WHERE ROW_COUNT() > 0;
END //
DELIMITER ;

-- Event para executar limpeza automaticamente a cada hora
CREATE EVENT IF NOT EXISTS CleanPasswordRecoveryTokens
ON SCHEDULE EVERY 1 HOUR
DO
    CALL CleanExpiredPasswordRecoveryTokens();

-- Verificar se o event scheduler está habilitado
SET GLOBAL event_scheduler = ON;

-- =====================================================
-- CONFIGURAÇÕES DE SEGURANÇA
-- =====================================================

-- Limite máximo de tentativas por hora por usuário: 3
-- Tempo de expiração do token: 15 minutos
-- Código de 6 dígitos numéricos
-- Token hexadecimal de 64 caracteres

-- =====================================================
-- VERIFICAÇÃO DA INSTALAÇÃO
-- =====================================================

-- Verificar tabelas criadas
SELECT 
    'password_recovery' as table_name,
    COUNT(*) as record_count
FROM password_recovery
UNION ALL
SELECT 
    'password_recovery_logs' as table_name,
    COUNT(*) as record_count
FROM password_recovery_logs;

-- Verificar procedures
SHOW PROCEDURE STATUS WHERE Name = 'CleanExpiredPasswordRecoveryTokens';

-- Verificar events
SHOW EVENTS WHERE Name = 'CleanPasswordRecoveryTokens';

-- =====================================================
-- QUERIES ÚTEIS PARA MONITORAMENTO
-- =====================================================

-- Ver tokens ativos
-- SELECT * FROM password_recovery WHERE used = FALSE AND expires_at > NOW();

-- Ver tentativas recentes
-- SELECT * FROM password_recovery_logs ORDER BY created_at DESC LIMIT 20;

-- Ver estatísticas de uso
-- SELECT 
--     action_type,
--     COUNT(*) as total,
--     SUM(success) as successful,
--     ROUND((SUM(success) / COUNT(*)) * 100, 2) as success_rate
-- FROM password_recovery_logs 
-- WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
-- GROUP BY action_type;

-- =====================================================
-- INSTALAÇÃO CONCLUÍDA
-- =====================================================

SELECT 'Password Recovery System - Database Setup Complete!' as status;
