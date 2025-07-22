const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔧 Configurando serviço de e-mail...');

// Verificar se node_modules existe
const nodeModulesPath = path.join(__dirname, 'node_modules');
if (!fs.existsSync(nodeModulesPath)) {
  console.log('📦 Instalando dependências...');
  try {
    execSync('npm install', { stdio: 'inherit', cwd: __dirname });
    console.log('✅ Dependências instaladas com sucesso');
  } catch (error) {
    console.error('❌ Erro ao instalar dependências:', error.message);
    process.exit(1);
  }
}

// Verificar se .env existe
const envPath = path.join(__dirname, '.env');
if (!fs.existsSync(envPath)) {
  console.log('📝 Criando arquivo .env...');
  
  const envContent = `# Configurações do banco de dados MySQL
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Evo@000#!
DB_NAME=vibe

# Configurações SMTP (configure com suas credenciais)
SMTP_HOST=smtp.hostinger.com
SMTP_PORT=587
SMTP_USER=suporte@meuvibe.com
SMTP_PASS=Dashwoodi@1995
SMTP_FROM=no-reply@meuvibe.com

# Configurações de verificação
VERIFICATION_CODE_EXPIRY=300000
RESEND_COOLDOWN=60000
MAX_RESEND_ATTEMPTS=5

# Porta do serviço
PORT=3001
`;

  try {
    fs.writeFileSync(envPath, envContent);
    console.log('✅ Arquivo .env criado com sucesso');
  } catch (error) {
    console.error('❌ Erro ao criar .env:', error.message);
    process.exit(1);
  }
}

console.log('🎉 Configuração concluída!');
console.log('📧 Configure suas credenciais SMTP no arquivo .env');
console.log('🚀 Execute "npm start" para iniciar o serviço');