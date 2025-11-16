#!/usr/bin/env python3
"""
Migrate existing posts from JSON files to database
"""
import json
import sqlite3
import glob
import os
from datetime import datetime

def migrate_posts_to_database():
    """Migrate posts from JSON files to the database"""
    db_path = 'data/metrics.db'

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Count existing posts in database
    cursor.execute('SELECT COUNT(*) FROM generated_content')
    existing_count = cursor.fetchone()[0]
    print(f"Existing posts in database: {existing_count}")

    posts_migrated = 0

    # Migrate from all JSON files in outputs directory
    json_files = glob.glob('outputs/*.json')

    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

                if isinstance(data, list):
                    for post in data:
                        if post.get('content') and post.get('content').strip():
                            # Determine platform from filename or post data
                            platform = 'linkedin'  # default
                            filename = os.path.basename(json_file).lower()
                            if 'twitter' in filename:
                                platform = 'twitter'
                            elif 'instagram' in filename:
                                platform = 'instagram'
                            elif 'linkedin' in filename:
                                platform = 'linkedin'

                            if post.get('platform'):
                                platform = post['platform']

                            # Generate post_id if not exists
                            post_id = post.get('id') or f"{platform}_{posts_migrated + existing_count + 1}"

                            # Insert or replace in database
                            cursor.execute('''
                                INSERT OR REPLACE INTO generated_content
                                (platform, content, topic, post_id, generated_at, posted)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (
                                platform,
                                post.get('content', ''),
                                post.get('topic', 'No topic'),
                                post_id,
                                post.get('created_at', post.get('generated_at', datetime.now().isoformat())),
                                post.get('status') == 'published' or post.get('posted', False)
                            ))

                            posts_migrated += 1

        except Exception as e:
            print(f"Error processing {json_file}: {e}")
            continue

    # Commit changes
    conn.commit()

    # Get final count
    cursor.execute('SELECT COUNT(*) FROM generated_content')
    final_count = cursor.fetchone()[0]

    print(f"Posts migrated: {posts_migrated}")
    print(f"Total posts in database: {final_count}")

    conn.close()
    print("Migration completed!")

if __name__ == '__main__':
    migrate_posts_to_database()