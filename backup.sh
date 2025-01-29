# backup.sh
#!/bin/bash

# 定义数据库凭证
DB_NAME="your_database_name"
DB_USER="your_database_user"
DB_PASSWORD="your_database_password"
BACKUP_DIR="./backups"

# 如果备份目录不存在，则创建
mkdir -p "$BACKUP_DIR"

# 执行备份
pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/backup_$(date +%F).sql"

# 可选：删除7天以上的备份
find "$BACKUP_DIR" -type f -name "*.sql" -mtime +7 -exec rm {} \;