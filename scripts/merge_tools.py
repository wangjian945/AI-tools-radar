"""
Merge new tools into existing database and regenerate the website.
"""
import json
from datetime import datetime

# Load existing tools
with open("data/processed_2026-03-28.json", "r", encoding="utf-8") as f:
    existing_data = json.load(f)

# Load new tools
with open("data/new_tools_2026_04_13.json", "r", encoding="utf-8") as f:
    new_data = json.load(f)

print(f"[OK] Loaded {len(existing_data['tools'])} existing tools")
print(f"[OK] Loaded {len(new_data['tools'])} new tools")

# Convert new tools to match existing format
def convert_tool_format(tool):
    """Convert new tool format to match existing database"""
    # Convert how_to_use list to string format
    how_to_use_str = ". ".join(tool["howToUse"]) + "."
    
    # Convert pricing_details to dict format
    pricing_details_dict = {tool["pricing"]: tool["pricingDetails"]}
    
    return {
        "name": tool["name"],
        "category": tool["category"],
        "one_liner": tool["tagline"],
        "key_features": tool["features"],
        "use_case": tool["useCase"],
        "how_to_use": how_to_use_str,
        "pricing": tool["pricing"],
        "pricing_details": pricing_details_dict,
        "quality_score": 9,  # Default score for new tools
        "is_research_relevant": tool["isResearchRelevant"],
        "url": tool["url"],
        "source": "Discovery_2026-04-13",
        "stars": 0,
        "collected_date": tool["dateAdded"],
        "featured": True,
        "logo": f"https://www.google.com/s2/favicons?domain={tool['url'].replace('https://', '').split('/')[0]}&sz=256",
        "logos": [
            f"https://www.google.com/s2/favicons?domain={tool['url'].replace('https://', '').split('/')[0]}&sz=256"
        ]
    }

# Convert and add new tools
converted_tools = [convert_tool_format(tool) for tool in new_data["tools"]]

# Check for duplicates
existing_names = {tool["name"].lower() for tool in existing_data["tools"]}
new_tools_to_add = []
duplicates = []

for tool in converted_tools:
    if tool["name"].lower() not in existing_names:
        new_tools_to_add.append(tool)
    else:
        duplicates.append(tool["name"])

print(f"\n[OK] {len(new_tools_to_add)} new tools to add")
if duplicates:
    print(f"    Skipped {len(duplicates)} duplicates: {', '.join(duplicates)}")

# Merge tools
all_tools = existing_data["tools"] + new_tools_to_add

# Create updated database
today = datetime.now().strftime("%Y-%m-%d")
updated_data = {
    "date": today,
    "processed_at": datetime.now().isoformat(),
    "total_collected": len(all_tools),
    "total_processed": len(all_tools),
    "total_qualified": sum(1 for t in all_tools if t.get("is_research_relevant", True)),
    "tools": all_tools
}

# Save merged database
output_file = f"data/processed_{today}.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(updated_data, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Saved merged database: {output_file}")
print(f"    Total tools: {len(all_tools)}")
print(f"    Qualified: {updated_data['total_qualified']}")
print(f"    Added: {len(new_tools_to_add)}")
