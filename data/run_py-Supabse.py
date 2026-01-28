"""
Partners Migration Script
- Runs the 027_partners.sql migration
- Adds KaroStartup as the first partner

Usage: python scripts/run_partners_migration.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Try to import psycopg2, install if not available
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("Installing psycopg2-binary...")
    os.system(f"{sys.executable} -m pip install psycopg2-binary python-dotenv")
    import psycopg2
    from psycopg2.extras import RealDictCursor

# Load environment variables
env_path = Path(__file__).parent.parent / '.env.local'
if not env_path.exists():
    env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables")
    print("Please set DATABASE_URL in .env.local or .env file")
    sys.exit(1)

# Fix URL encoding for passwords with special characters like @
# Pattern: postgresql://user:password@host:port/database
import re
from urllib.parse import quote

# Extract and re-encode the password if it contains special characters
match = re.match(r'postgresql://([^:]+):(.+)@([^@]+)$', DATABASE_URL)
if match:
    user = match.group(1)
    password = match.group(2)
    rest = match.group(3)
    # URL-encode the password (handles @ and other special chars)
    encoded_password = quote(password, safe='')
    DATABASE_URL = f"postgresql://{user}:{encoded_password}@{rest}"
    print(f"Database host: {rest.split(':')[0]}")


def run_migration():
    """Run the partners migration SQL"""
    migration_path = Path(__file__).parent.parent / 'supabase' / 'migrations' / '027_partners.sql'

    if not migration_path.exists():
        print(f"ERROR: Migration file not found at {migration_path}")
        sys.exit(1)

    print(f"Reading migration from: {migration_path}")

    with open(migration_path, 'r', encoding='utf-8') as f:
        migration_sql = f.read()

    conn = None
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        print("Running partners migration...")
        cursor.execute(migration_sql)
        conn.commit()

        print("Migration completed successfully!")
        return True

    except psycopg2.errors.DuplicateTable:
        print("Partners table already exists - skipping migration")
        if conn:
            conn.rollback()
        return True
    except psycopg2.errors.DuplicateObject as e:
        print(f"Some objects already exist (this is OK): {e}")
        if conn:
            conn.rollback()
        return True
    except Exception as e:
        print(f"Migration error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def add_karostartup_partner():
    """Add KaroStartup as a partner"""

    partner_data = {
        'name': 'KaroStartup',
        'slug': 'karostartup',
        'logo_url': 'https://www.thekarostartup.com/_next/image?url=%2Fassets%2Fimages%2Flogo.png&w=640&q=75',
        'website_url': 'https://www.thekarostartup.com',
        'description': '''KaroStartup is a digital platform dedicated to providing startup-related content and resources for entrepreneurs. Founded in 2019 by an IIT-Delhi alumni team, they began by establishing a community on Instagram, LinkedIn, and Facebook, connecting people from tier 2 and tier 3 cities with small startups and businesses.

The platform offers a marketplace and networking platform for college students, providing mentorship and education to new entrepreneurs. Their services include hosting virtual events, publishing content and ads, and enabling access to business skills and mentorship sessions.

KaroStartup has raised $1.33M in funding and operates as a blockchain-based ed-tech startup that provides training, guidance, and placement services for students.''',
        'short_description': 'Your ultimate destination for startup stories, news, and insights. Empowering entrepreneurs to build the future.',
        'partnership_type': 'strategic',
        'services_provided': [
            'Startup News & Updates',
            'Success Stories & Case Studies',
            'Founder Interviews',
            'Industry Trends & Tech Updates',
            'Mentorship & Education',
            'Networking Platform'
        ],
        'is_featured': True,
        'display_order': 1,
        'is_active': True
    }

    conn = None
    try:
        print("\nConnecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Check if partner already exists
        cursor.execute("SELECT id FROM partners WHERE slug = %s", (partner_data['slug'],))
        existing = cursor.fetchone()

        if existing:
            print(f"Partner '{partner_data['name']}' already exists with ID: {existing['id']}")
            print("Updating existing partner...")

            cursor.execute("""
                UPDATE partners SET
                    name = %s,
                    logo_url = %s,
                    website_url = %s,
                    description = %s,
                    short_description = %s,
                    partnership_type = %s,
                    services_provided = %s,
                    is_featured = %s,
                    display_order = %s,
                    is_active = %s,
                    updated_at = NOW()
                WHERE slug = %s
                RETURNING id, name
            """, (
                partner_data['name'],
                partner_data['logo_url'],
                partner_data['website_url'],
                partner_data['description'],
                partner_data['short_description'],
                partner_data['partnership_type'],
                partner_data['services_provided'],
                partner_data['is_featured'],
                partner_data['display_order'],
                partner_data['is_active'],
                partner_data['slug']
            ))

            result = cursor.fetchone()
            conn.commit()
            print(f"Updated partner: {result['name']} (ID: {result['id']})")

        else:
            print(f"Adding new partner: {partner_data['name']}...")

            cursor.execute("""
                INSERT INTO partners (
                    name, slug, logo_url, website_url, description,
                    short_description, partnership_type, services_provided,
                    is_featured, display_order, is_active
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id, name, slug
            """, (
                partner_data['name'],
                partner_data['slug'],
                partner_data['logo_url'],
                partner_data['website_url'],
                partner_data['description'],
                partner_data['short_description'],
                partner_data['partnership_type'],
                partner_data['services_provided'],
                partner_data['is_featured'],
                partner_data['display_order'],
                partner_data['is_active']
            ))

            result = cursor.fetchone()
            conn.commit()
            print(f"\nSuccessfully added partner!")
            print(f"  ID: {result['id']}")
            print(f"  Name: {result['name']}")
            print(f"  Slug: {result['slug']}")

        # Verify the partner was added
        cursor.execute("SELECT * FROM partners WHERE slug = %s", (partner_data['slug'],))
        partner = cursor.fetchone()

        print(f"\n--- Partner Details ---")
        print(f"Name: {partner['name']}")
        print(f"Website: {partner['website_url']}")
        print(f"Type: {partner['partnership_type']}")
        print(f"Featured: {partner['is_featured']}")
        print(f"Active: {partner['is_active']}")
        print(f"Services: {', '.join(partner['services_provided'] or [])}")

        return True

    except Exception as e:
        print(f"Error adding partner: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def main():
    print("=" * 50)
    print("Partners Migration & Setup Script")
    print("=" * 50)

    # Step 1: Run migration
    print("\n[Step 1] Running Partners Table Migration...")
    if not run_migration():
        print("Migration failed, but continuing to try adding partner...")

    # Step 2: Add KaroStartup partner
    print("\n[Step 2] Adding KaroStartup as Partner...")
    if add_karostartup_partner():
        print("\n" + "=" * 50)
        print("SUCCESS! KaroStartup has been added as a partner.")
        print("View at: /partners or /admin/content/partners")
        print("=" * 50)
    else:
        print("\nFailed to add partner. Please check the error above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
