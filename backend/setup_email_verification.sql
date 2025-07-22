-- Script para configurar tabela de verificação de e-mail
-- Execute este script no banco de dados MySQL

USE vibe;

-- Criar tabela para verificação de e-mail
CREATE TABLE IF NOT EXISTS email_verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    verification_code VARCHAR(6) NOT NULL,
    verification_token VARCHAR(64) NOT NULL,
    expires_at DATETIME NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    verified_at DATETIME NULL,
    attempts INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices para performance
    INDEX idx_user_id (user_id),
    INDEX idx_verification_code (verification_code),
    INDEX idx_verification_token (verification_token),
    INDEX idx_expires_at (expires_at),
    INDEX idx_verified (verified),
    
    -- Chave estrangeira para usuários
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Constraint para garantir apenas uma verificação ativa por usuário
    UNIQUE KEY unique_user_verification (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Criar tabela para log de envios de e-mail (para auditoria)
CREATE TABLE IF NOT EXISTS email_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    email_type ENUM('verification', 'password_reset', 'notification') DEFAULT 'verification',
    status ENUM('sent', 'failed', 'bounced') DEFAULT 'sent',
    error_message TEXT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices
    INDEX idx_user_id (user_id),
    INDEX idx_email_type (email_type),
    INDEX idx_status (status),
    INDEX idx_sent_at (sent_at),
    
    -- Chave estrangeira
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Adicionar colunas à tabela users se não existirem
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS email_verified_at DATETIME NULL AFTER is_verified,
ADD COLUMN IF NOT EXISTS email_verification_required BOOLEAN DEFAULT TRUE AFTER email_verified_at;

-- Atualizar usuários existentes como não verificados (se necessário)
-- UPDATE users SET is_verified = FALSE, email_verification_required = TRUE WHERE is_verified IS NULL;

-- Criar procedure para limpeza automática de códigos expirados
DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS CleanExpiredVerifications()
BEGIN
    DELETE FROM email_verifications 
    WHERE verified = FALSE AND expires_at < NOW();
    
    SELECT ROW_COUNT() as deleted_count;
END$$
DELIMITER ;

-- Criar event para limpeza automática (executa a cada hora)
-- SET GLOBAL event_scheduler = ON;
-- CREATE EVENT IF NOT EXISTS cleanup_expired_verifications
-- ON SCHEDULE EVERY 1 HOUR
-- DO CALL CleanExpiredVerifications();

-- Inserir dados de configuração (opcional)
CREATE TABLE IF NOT EXISTS system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Inserir configurações padrão para verificação de e-mail
INSERT IGNORE INTO system_config (config_key, config_value, description) VALUES
('email_verification_enabled', 'true', 'Habilitar verificação de e-mail para novos usuários'),
('verification_code_expiry', '300000', 'Tempo de expiração do código em milissegundos (5 minutos)'),
('max_resend_attempts', '5', 'Máximo de tentativas de reenvio por hora'),
('resend_cooldown', '60000', 'Tempo de espera entre reenvios em milissegundos (1 minuto)'),
('email_template_name', 'Vibe', 'Nome exibido nos e-mails'),
('email_template_from', 'no-reply@meuvibe.com', 'E-mail de origem para verificação');

-- Exibir resultado
SELECT 'Tabelas criadas com sucesso!' as status;
SELECT 'Execute as configurações do microserviço de e-mail' as next_step;

-- Verificar estrutura criada
SHOW TABLES LIKE '%email%';
DESCRIBE email_verifications;
