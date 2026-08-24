"""
Fully Automated Natural Language Interface
User says "refresh my data" → System automatically executes
No confirmation needed, just pure automation
"""
import subprocess
import sys
from anthropic import Anthropic
from datetime import datetime

# Command mappings
COMMANDS = {
    "refresh data": {
        "steps": [
            ("📥 Downloading from Kaggle", "python analytics/01_download_dataset.py"),
            ("📚 Loading into DuckDB", "python analytics/02_load_duckdb.py"),
            ("📝 Updating Metadata", "python analytics/03_generate_metadata_draft.py"),
        ],
        "description": "Refreshing your data from Kaggle and updating the database"
    },
    "download": {
        "steps": [("📥 Downloading from Kaggle", "python analytics/01_download_dataset.py")],
        "description": "Downloading latest data from Kaggle"
    },
    "load data": {
        "steps": [("📚 Loading into DuckDB", "python analytics/02_load_duckdb.py")],
        "description": "Loading data into DuckDB"
    },
    "update metadata": {
        "steps": [("📝 Updating Metadata", "python analytics/03_generate_metadata_draft.py")],
        "description": "Updating metadata schema"
    },
    "start dashboard": {
        "steps": [("🎯 Starting Dashboard", "streamlit run app.py")],
        "description": "Launching dashboard at localhost:8501"
    },
    "test dashboard": {
        "steps": [("🧪 Testing Dashboard", "streamlit run app.py")],
        "description": "Testing dashboard locally"
    },
    "deploy": {
        "steps": [("🚀 Deploying to Cloud", "git add . && git commit -m 'Auto-refresh' && git push origin main")],
        "description": "Pushing to GitHub and auto-deploying to Streamlit Cloud"
    },
    "verify": {
        "steps": [("✅ Verifying Data", "python -c \"import duckdb; con = duckdb.connect('data/processed/superstore.duckdb'); print('✅ Rows:', con.sql('SELECT COUNT(*) FROM orders').fetchall()[0][0])\"")],
        "description": "Verifying data integrity"
    },
}

def parse_command(user_input: str) -> tuple:
    """Parse user input and return (command_config, matched_command)"""
    user_lower = user_input.lower().strip()

    # Direct command match
    for cmd_name, cmd_config in COMMANDS.items():
        if cmd_name in user_lower:
            return cmd_config, cmd_name

    # Keyword matching for flexibility
    keywords = {
        "refresh": ("refresh data", COMMANDS["refresh data"]),
        "download": ("download", COMMANDS["download"]),
        "load": ("load data", COMMANDS["load data"]),
        "metadata": ("update metadata", COMMANDS["update metadata"]),
        "dashboard": ("start dashboard", COMMANDS["start dashboard"]),
        "start": ("start dashboard", COMMANDS["start dashboard"]),
        "run": ("start dashboard", COMMANDS["start dashboard"]),
        "deploy": ("deploy", COMMANDS["deploy"]),
        "push": ("deploy", COMMANDS["deploy"]),
        "test": ("test dashboard", COMMANDS["test dashboard"]),
        "verify": ("verify", COMMANDS["verify"]),
        "check": ("verify", COMMANDS["verify"]),
    }

    for keyword, (cmd_name, cmd_config) in keywords.items():
        if keyword in user_lower:
            return cmd_config, cmd_name

    return None, None

def execute_step(step_name: str, cmd: str) -> bool:
    """Execute a single step"""
    print(f"\n{step_name}")
    print(f"$ {cmd}\n")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False

        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def execute_command(cmd_config: dict, cmd_name: str) -> bool:
    """Execute all steps in a command automatically"""
    print("\n" + "=" * 60)
    print(f"🤖 {cmd_config['description'].upper()}")
    print("=" * 60)

    all_success = True
    for step_name, cmd in cmd_config['steps']:
        success = execute_step(step_name, cmd)
        if not success:
            all_success = False
            print(f"⚠️  Failed at: {step_name}")
            # Continue with other steps even if one fails
            continue

    print("\n" + "=" * 60)
    if all_success:
        print("✅ ALL STEPS COMPLETED SUCCESSFULLY!")
    else:
        print("⚠️  SOME STEPS FAILED - Check output above")
    print("=" * 60 + "\n")

    return all_success

def log_execution(user_input: str, cmd_name: str, success: bool):
    """Log execution to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "✅ SUCCESS" if success else "❌ FAILED"

    with open("execution_log.txt", "a") as f:
        f.write(f"[{timestamp}] {status} | User: {user_input} | Command: {cmd_name}\n")

def main():
    """Main interactive loop - fully automated"""
    print("\n" + "=" * 60)
    print("🤖 AGENTIC ANALYTICS POC - AUTO EXECUTOR")
    print("=" * 60)
    print("\nJust tell me what you want to do:")
    print("\n  Commands:")
    print("  • 'refresh my data'     - Download & load latest data")
    print("  • 'start dashboard'     - Launch dashboard locally")
    print("  • 'deploy'              - Push to cloud")
    print("  • 'verify'              - Check data integrity")
    print("  • 'help'                - Show all commands")
    print("  • 'exit'                - Quit\n")

    while True:
        try:
            user_input = input("📝 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("\n👋 Goodbye!")
                break

            if user_input.lower() == "help":
                print("\n📚 Available Commands:")
                for cmd_name in COMMANDS.keys():
                    print(f"  • {cmd_name}")
                print()
                continue

            # Parse command
            cmd_config, cmd_name = parse_command(user_input)

            if not cmd_config:
                print("\n❓ I didn't understand. Try one of these:")
                for cmd_name in list(COMMANDS.keys())[:5]:
                    print(f"  • {cmd_name}")
                print()
                continue

            # AUTO-EXECUTE (no confirmation needed!)
            success = execute_command(cmd_config, cmd_name)

            # Log execution
            log_execution(user_input, cmd_name, success)

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()
