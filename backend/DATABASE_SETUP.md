# 🗄️ Setup do Banco de Dados da Rede Social

## 📋 Visão Geral

Este diretório contém scripts para configurar completamente o banco de dados da rede social com suporte a mídia de alta qualidade.

## 🚀 Como Usar

### Opção 1: Setup Completo (Recomendado)

```bash
cd backend
python setup_complete_database.py
```

### Opção 2: Scripts Individuais

```bash
# 1. Criar estrutura básica
python create_database_structure.py

# 2. Configurar sistema de mídia
python setup_media_quality.py
```

## 📊 Estrutura do Banco

### 👥 **Tabelas de Usuários**

- `users` - Dados dos usuários
- `friendships` - Sistema de amizades
- `follows` - Sistema de seguidores
- `blocks` - Usuários bloqueados

### 📱 **Tabelas de Conteúdo**

- `posts` - Publicações e depoimentos
- `comments` - Comentários e respostas
- `reactions` - Curtidas e reações
- `stories` - Stories temporários
- `story_views` - Visualizações dos stories

### 📸 **Sistema de Mídia**

- `media_files` - Arquivos originais
- `media_variants` - Diferentes qualidades
- `media_quality_settings` - Configurações
- `media_metadata` - Metadados EXIF e análise

### 🖼️ **Álbuns e Organização**

- `albums` - Álbuns de fotos
- `album_photos` - Fotos dos álbuns

### 💬 **Sistema de Chat**

- `chats` - Conversas privadas e grupos
- `chat_messages` - Mensagens
- `chat_participants` - Participantes

### 🔔 **Notificações**

- `notifications` - Sistema de notificações

## 🎨 Sistema de Qualidade de Mídia

### 📏 **Variações Automáticas**

Cada imagem é processada em 5 qualidades:

| Tipo        | Dimensões   | Qualidade | Uso                   |
| ----------- | ----------- | --------- | --------------------- |
| `thumbnail` | 64-400px    | 70%       | Previews rápidas      |
| `small`     | 128-800px   | 80%       | Listagens             |
| `medium`    | 256-1200px  | 85%       | Visualização normal   |
| `large`     | 512-1600px  | 90%       | Visualização ampliada |
| `original`  | 1024-1920px | 95%       | Download/edição       |

### 📱 **Tipos de Mídia Suportados**

#### 👤 Avatar de Perfil

- **Thumbnail**: 64x64px
- **Original**: 1024x1024px
- **Formato**: JPEG otimizado

#### 🖼️ Foto de Capa

- **Thumbnail**: 400x150px
- **Original**: 1920x720px
- **Formato**: JPEG de alta qualidade

#### 📝 Imagens de Posts

- **Thumbnail**: 300x300px
- **Original**: 1920x1920px
- **Formato**: JPEG com qualidade adaptativa

#### 📱 Stories

- **Dimensões**: 9:16 (vertical)
- **Thumbnail**: 200x356px
- **Original**: 1080x1920px
- **Formato**: JPEG otimizado para mobile

#### 💬 Imagens de Chat/Comentários

- **Thumbnail**: 150-200px
- **Original**: 1200px
- **Formato**: JPEG comprimido

## ⚡ Recursos Avançados

### 🎯 **Metadados Inteligentes**

- Dados EXIF preservados
- Paleta de cores extraída
- Cor dominante identificada
- Detecção de faces (preparado)
- Análise de conteúdo (preparado)

### 🚀 **Otimizações de Performance**

- Índices compostos estratégicos
- Views pré-calculadas
- Consultas otimizadas
- Cache de metadados

### 🔍 **Views Úteis**

- `media_with_variants` - Mídia com todas as variações
- `posts_with_media` - Posts com URLs de mídia prontas

## 📋 **Configuração de Ambiente**

### Variáveis Necessárias (.env)

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=redesocial
```

### Pré-requisitos

- MySQL 8.0+
- Python 3.8+
- SQLAlchemy
- PyMySQL

## 🔧 **Customização**

### Alterar Qualidades

Edite `media_quality_settings` na tabela:

```sql
UPDATE media_quality_settings
SET max_width = 2048, max_height = 2048, quality_percentage = 90
WHERE media_type = 'post_image' AND variant_type = 'original';
```

### Adicionar Novos Tipos

```sql
INSERT INTO media_quality_settings
(media_type, variant_type, max_width, max_height, quality_percentage, format)
VALUES ('custom_type', 'medium', 800, 600, 85, 'jpeg');
```

## 🐛 **Troubleshooting**

### Erro de Conexão

```
❌ Erro ao conectar com banco de dados
```

**Solução**: Verifique credenciais no `.env`

### Tabelas já Existem

```
⚠️ Table already exists
```

**Solução**: Script limpa automaticamente. Use `--force` se necessário.

### Espaço em Disco

```
💾 Disk space warning
```

**Solução**: Mídia em múltiplas qualidades usa mais espaço. Monitore storage.

## 📊 **Estimativa de Espaço**

Para 1000 usuários ativos:

- **Avatares**: ~500MB (5 variações cada)
- **Capas**: ~2GB
- **Posts**: ~10GB (assumindo 50% com imagem)
- **Stories**: ~5GB (temporários)
- **Chat**: ~3GB

**Total estimado**: ~20GB para 1000 usuários

## 🔒 **Segurança**

### Validações Implementadas

- ✅ Tipos de arquivo verificados
- ✅ Tamanho máximo limitado
- ✅ Metadados sanitizados
- ✅ Paths seguros
- ✅ Proteção contra upload malicioso

### Recomendações

- Configure firewall no banco
- Use HTTPS para uploads
- Monitore uploads suspeitos
- Backup regular dos dados

## 🎉 **Pronto para Usar!**

Após executar os scripts, sua rede social terá:

- ✅ Estrutura completa de dados
- ✅ Sistema de mídia profissional
- ✅ Múltiplas qualidades automáticas
- ✅ Performance otimizada
- ✅ Escalabilidade preparada

Execute `python main.py` e comece a testar!
