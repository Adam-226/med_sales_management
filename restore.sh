# restore.sh
#!/bin/bash

# 定义数据库凭证
DB_NAME="your_database_name"
DB_USER="your_database_user"
DB_PASSWORD="your_database_password"
BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup-file.sql>"
  exit 1
fi

# 恢复备份
psql -U "$DB_USER" -d "$DB_NAME" -f "$BACKUP_FILE"