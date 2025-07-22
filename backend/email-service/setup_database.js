const mysql = require('mysql2/promise');
require('dotenv').config();

async function setupDatabase() {
  const connection = await mysql.createConnection({
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME
  });

  try {
    console.log('📋 Criando tabelas necessárias para o microserviço de e-mail...');

    // Tabela de verificações de e-mail
    await connection.execute(`
      CREATE TABLE IF NOT EXISTS email_verifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        email VARCHAR(255) NOT NULL,
        verification_code VARCHAR(6) NOT NULL,
        verification_token VARCHAR(64) NOT NULL,
        expires_at DATETIME NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        verified BOOLEAN DEFAULT FALSE,
        verified_at DATETIME NULL,
        attempts INT DEFAULT 1,
        INDEX idx_user_id (user_id),
        INDEX idx_token (verification_token),
        INDEX idx_code (verification_code),
        UNIQUE KEY unique_user_active (user_id, verified) 
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    `);

    // Tabela de recuperação de senha
    await connection.execute(`
      CREATE TABLE IF NOT EXISTS password_recovery (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        email VARCHAR(255) NOT NULL,
        recovery_code VARCHAR(6) NOT NULL,
        recovery_token VARCHAR(64) NOT NULL,
        expires_at DATETIME NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        used BOOLEAN DEFAULT FALSE,
        used_at DATETIME NULL,
        INDEX idx_user_id (user_id),
        INDEX idx_token (recovery_token),
        INDEX idx_code (recovery_code)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    `);

    // Tabela de logs de recuperação de senha
    await connection.execute(`
      CREATE TABLE IF NOT EXISTS password_recovery_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT DEFAULT 0,
        email VARCHAR(255) NOT NULL,
        action_type VARCHAR(50) NOT NULL,
        recovery_id INT NULL,
        success BOOLEAN NOT NULL,
        error_message TEXT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_user_id (user_id),
        INDEX idx_email (email),
        INDEX idx_action (action_type)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    `);

    console.log('✅ Tabelas criadas com sucesso!');

    // Verificar se a coluna is_verified existe na tabela users
    const [columns] = await connection.execute(`
      SELECT COLUMN_NAME 
      FROM INFORMATION_SCHEMA.COLUMNS 
      WHERE TABLE_SCHEMA = '${process.env.DB_NAME}' 
      AND TABLE_NAME = 'users' 
      AND COLUMN_NAME = 'is_verified'
    `);

    if (columns.length === 0) {
      console.log('➕ Adicionando coluna is_verified à tabela users...');
      await connection.execute(`
        ALTER TABLE users 
        ADD COLUMN is_verified BOOLEAN DEFAULT FALSE
      `);
      console.log('✅ Coluna is_verified adicionada!');
    } else {
      console.log('✅ Coluna is_verified já existe');
    }

    console.log('🎉 Configuração do banco de dados concluída!');

  } catch (error) {
    console.error('❌ Erro ao configurar banco de dados:', error);
    throw error;
  } finally {
    await connection.end();
  }
}

if (require.main === module) {
  setupDatabase()
    .then(() => {
      console.log('✅ Setup concluído com sucesso!');
      process.exit(0);
    })
    .catch((error) => {
      console.error('❌ Erro no setup:', error);
      process.exit(1);
    });
}

module.exports = setupDatabase;
