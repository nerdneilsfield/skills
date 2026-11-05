# Backup and restore runbook

Operator runbook for the `ledger` Postgres cluster. Applies to `ledger-prod` only.

## Prerequisites

- `pg_dump` 15 or newer available on the bastion host.
- `S3_BACKUP_BUCKET` exported in your shell.
- Read access to `/etc/ledger/backup.conf`.

## 1. Take a manual backup

Confirm the current backup directory:

    cat /etc/ledger/backup.conf

Run the dump:

    pg_dump -Fc -d ledger -f /var/backups/ledger/manual-$(date +%F).dump

Upload it:

    aws s3 cp /var/backups/ledger/manual-$(date +%F).dump "s3://$S3_BACKUP_BUCKET/"

## 2. Restore from a backup

Stop the application tier first. Restores overwrite the live database; anything written
after the dump is lost.

    pg_restore -C -d postgres /var/backups/ledger/manual-2024-05-01.dump

Start the application tier again.

## 3. Retention

The nightly job deletes dumps older than **7 days** from `/var/backups/ledger/`, and
keeps the first dump of each month in `s3://$S3_BACKUP_BUCKET/monthly/`.

## 4. Troubleshooting

If `pg_restore` fails with `role "app_rw" does not exist`, create the role first, then
rerun the restore.

## Summary

- Backups are written to `/var/backups/ledger/` and uploaded to S3.
- Retention is **14 days** for local dumps.
- Restore is performed with `pg_restore`.