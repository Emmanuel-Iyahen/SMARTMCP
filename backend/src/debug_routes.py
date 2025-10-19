# debug_routes.py
import os
import importlib.util

def check_route_file(file_path):
    print(f"\n🔍 Checking: {file_path}")
    if not os.path.exists(file_path):
        print("   ❌ File does not exist")
        return
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for problematic patterns
    problems = []
    
    # Check for middleware configuration
    if 'add_middleware' in content:
        problems.append("Contains 'add_middleware' - should only be in main.py")
    
    if 'CORSMiddleware' in content:
        problems.append("Contains 'CORSMiddleware' - should only be in main.py")
    
    if 'GZipMiddleware' in content:
        problems.append("Contains 'GZipMiddleware' - should only be in main.py")
    
    # Check for FastAPI instance creation
    if 'FastAPI(' in content:
        problems.append("Contains 'FastAPI()' - routes should use APIRouter")
    
    if problems:
        print("   ❌ PROBLEMS FOUND:")
        for problem in problems:
            print(f"      - {problem}")
        
        # Show the problematic lines
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if any(keyword in line for keyword in ['add_middleware', 'CORSMiddleware', 'GZipMiddleware', 'FastAPI(']):
                print(f"      Line {i}: {line.strip()}")
    else:
        print("   ✅ No middleware issues found")

# Check all route files
print("=== ROUTE FILE ANALYSIS ===")
check_route_file("routes/dashboard.py")
check_route_file("routes/prompts.py")
check_route_file("routes/data_sources.py")