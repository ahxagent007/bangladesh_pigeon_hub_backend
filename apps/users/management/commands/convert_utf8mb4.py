from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = (
        "Diagnose and convert the database + all tables to utf8mb4 so Bengali "
        "text can be stored. Dry run by default; pass --apply to execute."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply', action='store_true',
            help='Actually run the ALTER statements (default is a dry run).')

    def handle(self, *args, **options):
        apply_changes = options['apply']
        with connection.cursor() as c:
            c.execute("SELECT DATABASE(), @@character_set_database, @@collation_database")
            db, db_charset, db_collation = c.fetchone()
            self.stdout.write(f"Database: {db}  charset={db_charset}  collation={db_collation}")

            # Round-trip test through the live connection
            c.execute("SELECT 'বাংলা'")
            ok = c.fetchone()[0] == 'বাংলা'
            self.stdout.write(f"Connection Bangla round-trip: {'OK' if ok else 'BROKEN (check OPTIONS charset)'}")

            c.execute("""
                SELECT table_name, table_collation FROM information_schema.tables
                WHERE table_schema = DATABASE()
                  AND table_type = 'BASE TABLE'
                  AND table_collation NOT LIKE 'utf8mb4%'
            """)
            tables = c.fetchall()

            c.execute("""
                SELECT table_name, column_name, character_set_name
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                  AND character_set_name IS NOT NULL
                  AND character_set_name != 'utf8mb4'
            """)
            columns = c.fetchall()

            self.stdout.write(f"\nTables not utf8mb4: {len(tables)}")
            for name, coll in tables:
                self.stdout.write(f"  {name}  ({coll})")
            self.stdout.write(f"Text columns not utf8mb4: {len(columns)}")
            for tname, cname, cs in columns:
                self.stdout.write(f"  {tname}.{cname}  ({cs})")

            if db_charset != 'utf8mb4' or tables:
                self.stdout.write('')
                statements = []
                if db_charset != 'utf8mb4':
                    statements.append(
                        f"ALTER DATABASE `{db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                # Tables with non-utf8mb4 columns may still report a utf8mb4
                # default collation, so convert the union of both lists.
                to_convert = {name for name, _ in tables} | {t for t, _, _ in columns}
                statements += [
                    f"ALTER TABLE `{t}` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                    for t in sorted(to_convert)]

                if apply_changes:
                    for sql in statements:
                        self.stdout.write(f"RUNNING: {sql}")
                        c.execute(sql)
                    self.stdout.write(self.style.SUCCESS(
                        f"\nDone — converted {len(statements)} object(s) to utf8mb4."))
                else:
                    self.stdout.write("DRY RUN — would execute:")
                    for sql in statements:
                        self.stdout.write(f"  {sql};")
                    self.stdout.write("\nRe-run with --apply to execute. BACK UP THE DATABASE FIRST.")
            else:
                self.stdout.write(self.style.SUCCESS(
                    "\nEverything is already utf8mb4 — nothing to convert."))

            self.stdout.write(self.style.WARNING(
                "\nNote: text already saved as '???' was destroyed at insert time "
                "and cannot be recovered — those records must be re-entered."))
