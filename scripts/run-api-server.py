"""
Script to run the RAG-LLM Framework API server.
"""
import os
import sys
import uvicorn
import importlib.util
from pathlib import Path

def setup_python_path():
    """Set up the Python path to include the necessary directories."""
    project_root = Path(__file__).parent.parent.absolute()
    
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "src"))
    
    os.environ["PYTHONPATH"] = f"{project_root}:{project_root}/src:{os.environ.get('PYTHONPATH', '')}"
    
    print(f"Python path set to: {sys.path[:3]}")

def check_dependencies():
    """Check if the required dependencies are installed."""
    dependencies = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("langchain", "LangChain"),
        ("git", "GitPython"),
        ("github", "PyGithub")
    ]
    
    missing = []
    for module_name, package_name in dependencies:
        try:
            importlib.import_module(module_name)
            print(f"✅ {package_name} is installed")
        except ImportError:
            missing.append(package_name)
            print(f"❌ {package_name} is not installed")
    
    if missing:
        print("\nMissing dependencies. Install them with:")
        for package in missing:
            print(f"pip install {package.lower()}")
        return False
    
    return True

def run_api_server():
    """Run the FastAPI server."""
    backend_dir = Path(__file__).parent.parent / "src" / "backend"
    os.chdir(backend_dir)
    
    print(f"Starting API server from directory: {backend_dir}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

def main():
    """Main function."""
    print("=== Starting RAG-LLM Framework API Server ===")
    
    setup_python_path()
    
    if not check_dependencies():
        sys.exit(1)
    
    run_api_server()

if __name__ == "__main__":
    main()
