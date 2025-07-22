const express = require('express');
const nodemailer = require('nodemailer');
const cors = require('cors');
const crypto = require('crypto');
const mysql = require('mysql2/promise');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Configuração do transportador de e-mail
const transporter = nodemailer.createTransporter({
  host: process.env.SMTP_HOST,
  port: process.env.SMTP_PORT,
  secure: false, // true para 465, false para outros ports
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
  tls: {
    rejectUnauthorized: false
  }
});

// Configuração do banco de dados
const dbConfig = {
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
};

// Pool de conexões do banco
const pool = mysql.createPool(dbConfig);

// Função para gerar código de verificação
function generateVerificationCode() {
  return Math.floor(100000 + Math.random() * 900000).toString();
}

// Função para gerar token de verificação
function generateVerificationToken() {
  return crypto.randomBytes(32).toString('hex');
}

// Template de e-mail de verificação
function getEmailTemplate(firstName, code, token, baseUrl = 'http://localhost:5173') {
  const verificationUrl = `${baseUrl}/verify-email?token=${token}`;
  
  return `
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Confirme seu e-mail - Vibe</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          line-height: 1.6;
          color: #333;
          max-width: 600px;
          margin: 0 auto;
          padding: 20px;
          background-color: #f7f7f7;
        }
        .container {
          background: white;
          padding: 40px;
          border-radius: 10px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
          text-align: center;
          margin-bottom: 30px;
        }
        .logo {
          font-size: 32px;
          font-weight: bold;
          color: #6366f1;
          margin-bottom: 10px;
        }
        .title {
          font-size: 24px;
          margin-bottom: 20px;
          color: #1f2937;
        }
        .code-container {
          background: #f8fafc;
          border: 2px dashed #e2e8f0;
          border-radius: 8px;
          padding: 20px;
          text-align: center;
          margin: 20px 0;
        }
        .verification-code {
          font-size: 32px;
          font-weight: bold;
          color: #6366f1;
          letter-spacing: 4px;
          margin: 10px 0;
        }
        .button {
          display: inline-block;
          background: #6366f1;
          color: white;
          padding: 15px 30px;
          text-decoration: none;
          border-radius: 8px;
          font-weight: 500;
          margin: 20px 0;
          text-align: center;
        }
        .button:hover {
          background: #4f46e5;
        }
        .footer {
          margin-top: 30px;
          padding-top: 20px;
          border-top: 1px solid #e2e8f0;
          font-size: 14px;
          color: #6b7280;
          text-align: center;
        }
        .warning {
          background: #fef3c7;
          border: 1px solid #f59e0b;
          border-radius: 6px;
          padding: 15px;
          margin: 20px 0;
          color: #92400e;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <div class="logo">Vibe</div>
          <h1 class="title">Confirme seu e-mail</h1>
        </div>
        
        <p>Olá <strong>${firstName}</strong>,</p>
        
        <p>Bem-vindo ao Vibe! Para concluir seu cadastro, você precisa confirmar seu endereço de e-mail.</p>
        
        <div class="code-container">
          <p><strong>Seu código de verificação:</strong></p>
          <div class="verification-code">${code}</div>
          <p style="font-size: 14px; color: #6b7280;">Este código expira em 5 minutos</p>
        </div>
        
        <p style="text-align: center;">
          <strong>Ou clique no botão abaixo para confirmar automaticamente:</strong>
        </p>
        
        <div style="text-align: center;">
          <a href="${verificationUrl}" class="button">
            ✓ Confirmar E-mail
          </a>
        </div>
        
        <div class="warning">
          <strong>⚠️ Importante:</strong> Se você não solicitou este cadastro, pode ignorar este e-mail com segurança.
        </div>
        
        <div class="footer">
          <p>Este e-mail foi enviado para confirmar seu cadastro no Vibe.</p>
          <p>Se você não conseguir clicar no botão, copie e cole o código acima na página de verificação.</p>
          <p>&copy; 2024 Vibe. Todos os direitos reservados.</p>
        </div>
      </div>
    </body>
    </html>
  `;
}

// Rota de teste para verificar se o serviço está funcionando
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    service: 'Vibe Email Service',
    timestamp: new Date().toISOString()
  });
});

// Rota para enviar e-mail de verificação
app.post('/send-verification', async (req, res) => {
  try {
    const { email, firstName, userId } = req.body;

    if (!email || !firstName || !userId) {
      return res.status(400).json({
        success: false,
        message: 'E-mail, nome e ID do usuário são obrigatórios'
      });
    }

    // Verificar se o e-mail é válido
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({
        success: false,
        message: 'E-mail inválido'
      });
    }

    // Verificar limite de tentativas (anti-spam)
    const [existingAttempts] = await pool.execute(
      `SELECT COUNT(*) as count FROM email_verifications 
       WHERE user_id = ? AND created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)`,
      [userId]
    );

    if (existingAttempts[0].count >= process.env.MAX_RESEND_ATTEMPTS) {
      return res.status(429).json({
        success: false,
        message: 'Muitas tentativas. Tente novamente em 1 hora.',
        retryAfter: 3600000
      });
    }

    // Verificar cooldown entre envios
    const [lastAttempt] = await pool.execute(
      `SELECT created_at FROM email_verifications 
       WHERE user_id = ? ORDER BY created_at DESC LIMIT 1`,
      [userId]
    );

    if (lastAttempt.length > 0) {
      const timeSinceLastAttempt = Date.now() - new Date(lastAttempt[0].created_at).getTime();
      const cooldownMs = parseInt(process.env.RESEND_COOLDOWN);
      
      if (timeSinceLastAttempt < cooldownMs) {
        const remainingTime = Math.ceil((cooldownMs - timeSinceLastAttempt) / 1000);
        return res.status(429).json({
          success: false,
          message: `Aguarde ${remainingTime} segundos antes de solicitar um novo código`,
          retryAfter: remainingTime * 1000
        });
      }
    }

    // Gerar código e token de verificação
    const verificationCode = generateVerificationCode();
    const verificationToken = generateVerificationToken();
    const expiresAt = new Date(Date.now() + parseInt(process.env.VERIFICATION_CODE_EXPIRY));

    // Salvar no banco de dados
    await pool.execute(
      `INSERT INTO email_verifications (user_id, email, verification_code, verification_token, expires_at, created_at, attempts)
       VALUES (?, ?, ?, ?, ?, NOW(), 1)
       ON DUPLICATE KEY UPDATE 
       verification_code = VALUES(verification_code),
       verification_token = VALUES(verification_token),
       expires_at = VALUES(expires_at),
       created_at = NOW(),
       attempts = attempts + 1,
       verified = FALSE`,
      [userId, email, verificationCode, verificationToken, expiresAt]
    );

    // Enviar e-mail
    const mailOptions = {
      from: {
        name: 'Vibe',
        address: process.env.SMTP_FROM
      },
      to: email,
      subject: 'Confirme seu e-mail - Vibe',
      html: getEmailTemplate(firstName, verificationCode, verificationToken)
    };

    await transporter.sendMail(mailOptions);

    console.log(`✅ E-mail de verificação enviado para: ${email}`);

    res.json({
      success: true,
      message: 'E-mail de verificação enviado com sucesso',
      expiresIn: parseInt(process.env.VERIFICATION_CODE_EXPIRY),
      cooldownMs: parseInt(process.env.RESEND_COOLDOWN)
    });

  } catch (error) {
    console.error('❌ Erro ao enviar e-mail:', error);
    res.status(500).json({
      success: false,
      message: 'Erro interno do servidor ao enviar e-mail'
    });
  }
});

// Rota para verificar código
app.post('/verify-code', async (req, res) => {
  try {
    const { userId, code } = req.body;

    if (!userId || !code) {
      return res.status(400).json({
        success: false,
        message: 'ID do usuário e código são obrigatórios'
      });
    }

    // Buscar registro de verificação
    const [results] = await pool.execute(
      `SELECT * FROM email_verifications 
       WHERE user_id = ? AND verification_code = ? AND verified = FALSE AND expires_at > NOW()
       ORDER BY created_at DESC LIMIT 1`,
      [userId, code]
    );

    if (results.length === 0) {
      return res.status(400).json({
        success: false,
        message: 'Código inválido ou expirado'
      });
    }

    // Marcar como verificado
    await pool.execute(
      'UPDATE email_verifications SET verified = TRUE, verified_at = NOW() WHERE id = ?',
      [results[0].id]
    );

    // Atualizar usuário como verificado
    await pool.execute(
      'UPDATE users SET is_verified = TRUE WHERE id = ?',
      [userId]
    );

    console.log(`✅ E-mail verificado para usuário ID: ${userId}`);

    res.json({
      success: true,
      message: 'E-mail verificado com sucesso!'
    });

  } catch (error) {
    console.error('❌ Erro ao verificar código:', error);
    res.status(500).json({
      success: false,
      message: 'Erro interno do servidor'
    });
  }
});

// Rota para verificar token (link do e-mail)
app.post('/verify-token', async (req, res) => {
  try {
    const { token } = req.body;

    if (!token) {
      return res.status(400).json({
        success: false,
        message: 'Token é obrigatório'
      });
    }

    // Buscar registro de verificação
    const [results] = await pool.execute(
      `SELECT * FROM email_verifications 
       WHERE verification_token = ? AND verified = FALSE AND expires_at > NOW()
       ORDER BY created_at DESC LIMIT 1`,
      [token]
    );

    if (results.length === 0) {
      return res.status(400).json({
        success: false,
        message: 'Token inválido ou expirado'
      });
    }

    // Marcar como verificado
    await pool.execute(
      'UPDATE email_verifications SET verified = TRUE, verified_at = NOW() WHERE id = ?',
      [results[0].id]
    );

    // Atualizar usuário como verificado
    await pool.execute(
      'UPDATE users SET is_verified = TRUE WHERE id = ?',
      [results[0].user_id]
    );

    console.log(`✅ E-mail verificado via token para usuário ID: ${results[0].user_id}`);

    res.json({
      success: true,
      message: 'E-mail verificado com sucesso!',
      userId: results[0].user_id
    });

  } catch (error) {
    console.error('❌ Erro ao verificar token:', error);
    res.status(500).json({
      success: false,
      message: 'Erro interno do servidor'
    });
  }
});

// Rota para verificar status de verificação
app.get('/verification-status/:userId', async (req, res) => {
  try {
    const { userId } = req.params;

    const [results] = await pool.execute(
      'SELECT is_verified FROM users WHERE id = ?',
      [userId]
    );

    if (results.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Usuário não encontrado'
      });
    }

    res.json({
      success: true,
      verified: !!results[0].is_verified
    });

  } catch (error) {
    console.error('❌ Erro ao verificar status:', error);
    res.status(500).json({
      success: false,
      message: 'Erro interno do servidor'
    });
  }
});

// Rota para teste de envio de e-mail
app.post('/test-email', async (req, res) => {
  try {
    const testEmail = {
      from: {
        name: 'Vibe',
        address: process.env.SMTP_FROM
      },
      to: process.env.SMTP_USER, // Enviar para o próprio e-mail de suporte
      subject: 'Teste do Microserviço de E-mail - Vibe',
      html: `
        <h2>Teste de E-mail</h2>
        <p>Este é um e-mail de teste do microserviço de e-mail do Vibe.</p>
        <p>Configurações SMTP funcionando corretamente!</p>
        <p>Data/Hora: ${new Date().toLocaleString('pt-BR')}</p>
      `
    };

    await transporter.sendMail(testEmail);
    
    res.json({
      success: true,
      message: 'E-mail de teste enviado com sucesso!'
    });

  } catch (error) {
    console.error('❌ Erro no teste de e-mail:', error);
    res.status(500).json({
      success: false,
      message: 'Erro ao enviar e-mail de teste',
      error: error.message
    });
  }
});

// Inicializar servidor
app.listen(PORT, () => {
  console.log(`🚀 Microserviço de E-mail rodando na porta ${PORT}`);
  console.log(`📧 SMTP: ${process.env.SMTP_HOST}:${process.env.SMTP_PORT}`);
  console.log(`📮 From: ${process.env.SMTP_FROM}`);
});

module.exports = app;
