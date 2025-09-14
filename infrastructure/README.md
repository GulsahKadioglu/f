# Infrastructure Scripts

This directory contains scripts related to the management and maintenance of the project's infrastructure.

## `backup_restore.sh`

This script is a utility for backing up and restoring the PostgreSQL database used by the application.

### Prerequisites

- The script assumes that `pg_dump` and `psql` command-line tools are installed and available in the shell's `PATH`.
- It also requires that the necessary environment variables for database connection (`POSTGRES_USER`, `POSTGRES_DB`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`) are set or exported in the shell environment where the script is run.

### Usage

The script accepts two arguments: an operation (`backup` or `restore`) and a filename.

#### To Create a Backup:

This command will dump the contents of the database to a specified SQL file.

```bash
bash backup_restore.sh backup my_database_backup.sql
```

#### To Restore from a Backup:

This command will restore the database from the specified SQL file. **Warning:** This will overwrite the existing data in the database.

```bash
bash backup_restore.sh restore my_database_backup.sql
```

---

**Disclaimer:** This script is a basic utility. Before using it in a production environment, ensure you have tested it thoroughly and adapted it to your specific infrastructure and security requirements.
