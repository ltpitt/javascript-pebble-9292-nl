#!/usr/bin/env python3
"""Find stops near Spaarnhovenstraat in GTFS database"""
import sqlite3

conn = sqlite3.connect('data/gtfs.db')
conn.row_factory = sqlite3.Row

# Search for stops with "Spaarn" in the name
print("=== Searching for stops with 'Spaarn' in name ===")
cursor = conn.execute("""
    SELECT stop_id, stop_code, stop_name, stop_lat, stop_lon
    FROM stops
    WHERE LOWER(stop_name) LIKE '%spaarn%'
    LIMIT 20
""")

results = cursor.fetchall()
if results:
    for row in results:
        print(f"stop_code: {row['stop_code']}, name: {row['stop_name']}")
        print(f"  → stop_id: {row['stop_id']}, coords: ({row['stop_lat']}, {row['stop_lon']})")
else:
    print("No stops found with 'Spaarn' in name")

# Also search OV API stop area codes
print("\n=== Searching for 'hlm' stop area codes (Haarlem) ===")
print("Common patterns: hlmbyz (Byzantiumstraat), hlmnsl (Nassaulaan)")
print("Need to search OV API or check their documentation for Spaarnhovenstraat code")

conn.close()
