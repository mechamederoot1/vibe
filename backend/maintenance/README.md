# Scripts de Manutenção

Esta pasta contém scripts de manutenção e correção do banco de dados.

## Estrutura

- **scripts/**: Scripts principais de inicialização
  - `init_database.py`: Inicialização do banco de dados

- **Fixes de Banco de Dados**:
  - `add_display_id.py`: Adicionar IDs de exibição aos usuários
  - `auto_fix_reactions.py`: Correção automática da tabela de reações
  - `complete_fix.py`: Correção completa do banco
  - `emergency_db_fix.py`: Correções de emergência
  - `fix_album_photos.py`: Correção da estrutura de fotos do álbum
  - `fix_profile_columns.py`: Correção de colunas do perfil
  - `fix_reactions_sql.sql`: Script SQL para correção de reações

## Como Usar

Execute os scripts de correção apenas quando necessário e sempre faça backup do banco antes.

```bash
# Exemplo de uso
cd backend/maintenance
python nome_do_script.py
```

⚠️ **Importante**: Sempre teste em ambiente de desenvolvimento antes de aplicar em produção.
