import os
import glob
import re

dashboard_path = 'frontend/src/app/(dashboard)'
files = glob.glob(f"{dashboard_path}/**/*.tsx", recursive=True)

for file_path in files:
    with open(file_path, 'r') as f:
        content = f.read()

    # Replace text-white with text-foreground, unless it's in a Button component or followed by something?
    # Actually, let's just replace `text-white` with `text-foreground`.
    # And manually fix buttons if there are any.
    
    # We can also do text-[#A0A0A0] -> text-muted-foreground
    content = content.replace('text-white', 'text-foreground')
    content = content.replace('text-[#A0A0A0]', 'text-muted-foreground')
    content = content.replace('bg-[#2A2A2A]', 'bg-muted')
    content = content.replace('bg-[#1E1E1E]', 'bg-card')
    content = content.replace('border-[rgba(255,255,255,0.1)]', 'border-border')
    
    with open(file_path, 'w') as f:
        f.write(content)
