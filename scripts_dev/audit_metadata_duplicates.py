"""
Audit metadata_registry.json for potential duplicate semantic fields.

Identifies cases where different field names might represent the same concept
but have different UUIDs (which would be wrong).
"""
import json
from pathlib import Path
from collections import defaultdict

# Load registry
repo_root = Path(__file__).resolve().parents[1]
registry_path = repo_root / "smart_media_manager" / "metadata_registry.json"
with open(registry_path) as f:
    registry = json.load(f)

metadata_fields = registry["metadata_fields"]

# Collect all tool field names and which UUID they map to
tool_field_to_uuid = defaultdict(list)

for category, fields in metadata_fields.items():
    for field_name, field_info in fields.items():
        uuid = field_info["uuid"]
        canonical = field_info["canonical"]

        for tool, field_names in field_info["tool_mappings"].items():
            for tool_field in field_names:
                tool_field_to_uuid[(tool, tool_field.lower())].append({
                    "uuid": uuid,
                    "canonical": canonical,
                    "category": category,
                    "tool_field_original": tool_field
                })

# Find duplicates - same tool field name mapped to multiple UUIDs
print("=" * 80)
print("AUDIT: Checking for duplicate semantic fields")
print("=" * 80)
print()

duplicates_found = False

for (tool, field_name), mappings in sorted(tool_field_to_uuid.items()):
    if len(mappings) > 1:
        duplicates_found = True
        print(f"⚠️  DUPLICATE: {tool}:{field_name}")
        print(f"   Mapped to {len(mappings)} different UUIDs:")
        for m in mappings:
            print(f"     - {m['canonical']} ({m['category']}) → {m['uuid']}")
            print(f"       Original field: {m['tool_field_original']}")
        print()

if not duplicates_found:
    print("✓ No duplicates found!")
    print("  Each tool-specific field name maps to exactly one UUID")
    print()

# Now check for potential semantic duplicates that might have been missed
# Look for very similar canonical names
print("=" * 80)
print("AUDIT: Checking for similar canonical field names")
print("=" * 80)
print()

all_fields = []
for category, fields in metadata_fields.items():
    for field_name, field_info in fields.items():
        all_fields.append({
            "canonical": field_info["canonical"],
            "uuid": field_info["uuid"],
            "category": category,
            "description": field_info.get("description", "")
        })

# Look for similar names
similar_found = False
checked = set()

for i, field1 in enumerate(all_fields):
    for field2 in all_fields[i+1:]:
        pair_key = tuple(sorted([field1["canonical"], field2["canonical"]]))
        if pair_key in checked:
            continue
        checked.add(pair_key)

        # Check if names are very similar (might be duplicates)
        name1_words = set(field1["canonical"].replace("_", " ").split())
        name2_words = set(field2["canonical"].replace("_", " ").split())

        # If they share most words, flag for review
        if name1_words & name2_words:  # Have common words
            overlap = len(name1_words & name2_words)
            total_unique = len(name1_words | name2_words)
            similarity = overlap / total_unique

            if similarity > 0.5 and field1["uuid"] != field2["uuid"]:
                similar_found = True
                print(f"⚠️  SIMILAR: {field1['canonical']} vs {field2['canonical']}")
                print(f"   Similarity: {similarity:.1%}")
                print(f"   {field1['canonical']}: {field1['description'][:60]}...")
                print(f"   {field2['canonical']}: {field2['description'][:60]}...")
                print(f"   Categories: {field1['category']} vs {field2['category']}")
                print()

if not similar_found:
    print("✓ No suspiciously similar field names found")
    print()

# Summary statistics
print("=" * 80)
print("REGISTRY STATISTICS")
print("=" * 80)
print(f"Total categories: {len(metadata_fields)}")
print(f"Total fields: {sum(len(fields) for fields in metadata_fields.values())}")
print(f"Total UUIDs: {len(set(f['uuid'] for cat in metadata_fields.values() for f in cat.values()))}")
print()

# Check UUID uniqueness
all_uuids = [f['uuid'] for cat in metadata_fields.values() for f in cat.values()]
if len(all_uuids) == len(set(all_uuids)):
    print("✓ All UUIDs are unique")
else:
    print("⚠️  WARNING: Some UUIDs are duplicated!")
    from collections import Counter
    uuid_counts = Counter(all_uuids)
    for uuid, count in uuid_counts.items():
        if count > 1:
            print(f"   {uuid} appears {count} times")
