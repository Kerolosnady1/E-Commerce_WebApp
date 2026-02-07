"""
Script to update profile avatar icons in E-Commerce_UI HTML files
"""
import re
import os

files_to_update = [
    'E-Commerce_UI/05-Account_Management_System_Code.html',
    'E-Commerce_UI/08-Tax_Management_System_Code.html',
    'E-Commerce_UI/09-Print_Templates_System_Code.html',
    'E-Commerce_UI/11-Security_&_Permissions_System_Code.html',
    'E-Commerce_UI/12-Language_&_Time_System_Code.html',
    'E-Commerce_UI/13-Users_&_Permissions_System_Code.html',
]

# Pattern to find the avatar div with Google URL
pattern = r'<div class="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10[^"]*" data-alt="[^"]*" style=\'background-image: url\("https://lh3\.googleusercontent\.com/[^"]+"\);\'></div>'

# Replacement template
replacement = '''{% if request.user.profile.avatar %}
            <div class="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10{classes}" style='background-image: url("{{{{ request.user.profile.avatar.url }}}}");' title="{{{{ request.user.get_full_name|default:request.user.username }}}}"></div>
            {% else %}
            <div class="flex items-center justify-center rounded-full size-10{classes} bg-primary/10 text-primary font-bold">
                {{{{ request.user.first_name|default:request.user.username|slice:":1"|upper }}}}
            </div>
            {% endif %}'''

def update_file(filename):
    """Update a single HTML file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all matches
        matches = list(re.finditer(pattern, content))
        
        if not matches:
            print(f"❌ No matches found in {filename}")
            return False
        
        print(f"✅ Found {len(matches)} match(es) in {filename}")
        
        # Process each match from end to start to preserve positions
        for match in reversed(matches):
            matched_text = match.group(0)
            
            # Extract the classes from the original div (everything after "size-10")
            class_match = re.search(r'size-10([^"]*)"', matched_text)
            extra_classes = class_match.group(1) if class_match else ''
            
            # Generate replacement text with extracted classes
            replacement_text = replacement.replace('{classes}', extra_classes)
            
            # Replace in content
            content = content[:match.start()] + replacement_text + content[match.end():]
        
        # Write back
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Successfully updated {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {filename}: {e}")
        return False

def main():
    """Update all files"""
    print("🚀 Starting profile icon updates...\n")
    
    updated_count = 0
    for filename in files_to_update:
        if os.path.exists(filename):
            if update_file(filename):
                updated_count += 1
        else:
            print(f"❌ File not found: {filename}")
        print()
    
    print(f"✅ Complete! Updated {updated_count}/{len(files_to_update)} files")

if __name__ == '__main__':
    main()
