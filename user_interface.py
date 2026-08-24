"""
Natural Language User Interface for Agentic Analytics POC
Users type simple English commands, Claude handles the technical execution
"""
import subprocess
import sys
from anthropic import Anthropic

# Command mappings
COMMANDS = {
    "refresh data": "python analytics/01_download_dataset.py && python analytics/02_load_duckdb.py && python analytics/03_generate_metadata_draft.py",
    "download": "python analytics/01_download_dataset.py",
    "load data": "python analytics/02_load_duckdb.py",
    "update metadata": "python analytics/03_generate_metadata_draft.py",
    "start dashboard": "streamlit run app.py",
    "test": "streamlit run app.py",
    "deploy": "git add . && git commit -m 'Data refresh' && git push origin main",
    "push to github": "git add . && git commit -m 'Updates' && git push origin main",
    "verify": "python -c \"import duckdb; con = duckdb.connect('data/processed/superstore.duckdb'); print('✅ Rows:', con.sql('SELECT COUNT(*) FROM orders').fetchall()[0][0])\"",
}

def get_claude_response(user_input: str, client: Anthropic) -> str:
    """Get Claude's guidance on what the user wants to do"""
    system_prompt = """You are a helpful assistant for the Agentic Analytics POC.

User just typed a natural language command. Understand what they want and respond with:
1. What you understand they want to do
2. What command will be executed
3. What to expect

Be friendly and non-technical. Examples:
- User: "refresh my data" → "I'll download the latest data from Kaggle, load it into the database, and update the metadata."
- User: "start the dashboard" → "I'll launch your dashboard at localhost:8501"
- User: "deploy to cloud" → "I'll push your changes to GitHub and Streamlit Cloud will auto-deploy."
"""

    messages = [{"role": "user", "content": user_input}]
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=system_prompt,
        messages=messages
    )
    return next((b.text for b in response.content if hasattr(b, "text")), "")

def parse_command(user_input: str) -> str:
    """Parse user input to find matching command"""
    user_lower = user_input.lower()

    # Direct command match
    for cmd, shell_cmd in COMMANDS.items():
        if cmd in user_lower:
            return shell_cmd

    # Keyword matching
    keywords = {
        "refresh": COMMANDS["refresh data"],
        "download": COMMANDS["download"],
        "load": COMMANDS["load data"],
        "metadata": COMMANDS["update metadata"],
        "dashboard": COMMANDS["start dashboard"],
        "start": COMMANDS["start dashboard"],
        "run": COMMANDS["start dashboard"],
        "deploy": COMMANDS["deploy"],
        "push": COMMANDS["push to github"],
        "test": COMMANDS["test"],
        "verify": COMMANDS["verify"],
    }

    for keyword, cmd in keywords.items():
        if keyword in user_lower:
            return cmd

    return None

def execute_command(cmd: str, description: str) -> bool:
    """Execute shell command and show output"""
    print(f"\n🔄 {description}...\n")
    print(f"$ {cmd}\n")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=False)
        if result.returncode == 0:
            print(f"\n✅ Done!\n")
            return True
        else:
            print(f"\n❌ Command failed\n")
            return False
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return False

def main():
    """Main interactive loop"""
    client = Anthropic()

    print("=" * 60)
    print("🤖 Agentic Analytics POC - User Interface")
    print("=" * 60)
    print("\nHi! I'm your assistant. Just tell me what you want to do:")
    print("  • 'refresh my data'")
    print("  • 'start the dashboard'")
    print("  • 'deploy to cloud'")
    print("  • 'verify the data'")
    print("  • Type 'help' for more commands")
    print("  • Type 'exit' to quit\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("\n👋 Goodbye!")
                break

            if user_input.lower() == "help":
                print("\n📚 Available Commands:")
                for cmd in COMMANDS.keys():
                    print(f"  • {cmd}")
                print()
                continue

            # Get Claude's understanding
            claude_response = get_claude_response(user_input, client)
            print(f"\n🤖 Claude: {claude_response}\n")

            # Parse and execute command
            cmd = parse_command(user_input)

            if not cmd:
                print("❓ I'm not sure what you want. Try:")
                for command in COMMANDS.keys():
                    print(f"  • {command}")
                print()
                continue

            # Confirm before executing
            confirm = input("Ready to execute? (yes/no): ").strip().lower()
            if confirm != "yes" and confirm != "y":
                print("Cancelled.\n")
                continue

            # Execute
            success = execute_command(cmd, claude_response.split("\n")[0])

            if not success:
                retry = input("Try again? (yes/no): ").strip().lower()
                if retry == "yes" or retry == "y":
                    execute_command(cmd, claude_response.split("\n")[0])

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()
