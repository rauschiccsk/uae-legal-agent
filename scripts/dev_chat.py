"""
AI Development Agent - Claude API + Git Integration
Automatically generates code, saves files, and commits to Git

Usage:
    python dev_agent.py --project uae-legal-agent --prompt "Create vector_store.py"
    python dev_agent.py --project uae-legal-agent --prompt "Fix bug in claude_client.py" --auto-commit
"""
import os
import re
import sys
import json
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import subprocess

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class GitManager:
    """Git operations manager"""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

    def git_command(self, *args) -> Tuple[bool, str]:
        """Execute git command"""
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_path)] + list(args),
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def add(self, file_path: str) -> bool:
        """Git add file"""
        success, output = self.git_command("add", file_path)
        return success

    def commit(self, message: str) -> Tuple[bool, str]:
        """Git commit"""
        success, output = self.git_command("commit", "-m", message)
        return success, output

    def push(self, remote: str = "origin", branch: str = "main") -> Tuple[bool, str]:
        """Git push"""
        success, output = self.git_command("push", remote, branch)
        return success, output

    def status(self) -> str:
        """Git status"""
        success, output = self.git_command("status", "--short")
        return output if success else ""

    def diff(self, file_path: str) -> str:
        """Git diff for file"""
        success, output = self.git_command("diff", file_path)
        return output if success else ""


class CodeBlockParser:
    """Parse code blocks and artifacts from Claude responses"""

    @staticmethod
    def extract_code_blocks(text: str) -> List[Dict]:
        """Extract all code blocks from markdown text"""
        # Pattern: ```language\ncode\n```
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)

        code_blocks = []
        for language, code in matches:
            code_blocks.append({
                "language": language or "text",
                "code": code.strip(),
                "lines": len(code.strip().split('\n'))
            })

        return code_blocks

    @staticmethod
    def suggest_filename(code: str, language: str, context: str = "") -> str:
        """Suggest filename based on code content and context"""
        # Try to extract from context (e.g., "Create src/core/file.py")
        path_pattern = r'(?:Create|create|make|add)\s+([a-zA-Z0-9_/\\.-]+\.(py|md|txt|json|yaml|yml))'
        match = re.search(path_pattern, context)
        if match:
            return match.group(1)

        # Try to extract class name from Python code
        if language == "python":
            class_match = re.search(r'class\s+(\w+)', code)
            if class_match:
                class_name = class_match.group(1)
                # Convert CamelCase to snake_case
                filename = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
                return f"{filename}.py"

        # Default
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "markdown": "md",
            "json": "json",
            "yaml": "yaml"
        }.get(language, "txt")

        return f"generated_{timestamp}.{ext}"

    @staticmethod
    def generate_commit_message(files: List[str], prompt: str) -> str:
        """Generate semantic commit message"""
        # Determine type
        if any("test" in f for f in files):
            commit_type = "test"
        elif any("doc" in f or f.endswith(".md") for f in files):
            commit_type = "docs"
        elif any("config" in f or f.endswith((".yaml", ".json", ".txt")) for f in files):
            commit_type = "chore"
        elif "fix" in prompt.lower() or "bug" in prompt.lower():
            commit_type = "fix"
        else:
            commit_type = "feat"

        # Generate description
        if len(files) == 1:
            file_name = Path(files[0]).name
            desc = f"Add {file_name}" if "add" in prompt.lower() or "create" in prompt.lower() else f"Update {file_name}"
        else:
            desc = f"Add {len(files)} files"

        # Truncate prompt if too long
        prompt_clean = prompt[:50] + "..." if len(prompt) > 50 else prompt

        return f"{commit_type}: {desc}\n\nGenerated via AI agent: {prompt_clean}"


class DevAgent:
    """AI Development Agent with Claude API"""

    def __init__(self, project: str, repo_path: str, session: str = "default"):
        self.project = project
        self.repo_path = Path(repo_path)
        self.session = session

        # Initialize Git
        self.git = GitManager(repo_path)

        # Initialize Claude
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found!")

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"
        self.max_tokens = 8000

        # Initialize conversation DB
        self.db_path = self.repo_path / "dev_agent_history.db"
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                session TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tokens INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                action_type TEXT NOT NULL,
                file_path TEXT,
                commit_hash TEXT,
                success BOOLEAN,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        """)

        conn.commit()
        conn.close()

    def load_conversation_history(self) -> List[Dict]:
        """Load conversation history for session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            """SELECT role, content FROM conversations 
               WHERE project = ? AND session = ? 
               ORDER BY created_at""",
            (self.project, self.session)
        )
        history = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
        conn.close()
        return history

    def save_message(self, role: str, content: str, tokens: int = 0, cost: float = 0):
        """Save message to database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT INTO conversations (project, session, role, content, tokens, cost_usd)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (self.project, self.session, role, content, tokens, cost)
        )
        conn.commit()
        conn.close()

    def log_action(self, action_type: str, file_path: str = None,
                   commit_hash: str = None, success: bool = True, error: str = None):
        """Log file/git action"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT INTO actions (action_type, file_path, commit_hash, success, error_message)
               VALUES (?, ?, ?, ?, ?)""",
            (action_type, file_path, commit_hash, success, error)
        )
        conn.commit()
        conn.close()

    def process_prompt(self, prompt: str, auto_commit: bool = False) -> Dict:
        """Process user prompt with Claude API"""
        print(f"\n{'='*70}")
        print("🤖 AI DEVELOPMENT AGENT")
        print(f"{'='*70}")
        print(f"Project:      {self.project}")
        print(f"Session:      {self.session}")
        print(f"Prompt:       {prompt}")
        print(f"Auto-commit:  {auto_commit}")
        print(f"{'='*70}\n")

        # Load history
        history = self.load_conversation_history()
        print(f"📚 Loaded {len(history)} previous messages")

        # Add user prompt
        history.append({"role": "user", "content": prompt})

        # Call Claude API
        print(f"🔄 Calling Claude API...")
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=history
        )

        # Extract response
        assistant_message = response.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = (input_tokens / 1_000_000) * 3 + (output_tokens / 1_000_000) * 15

        print(f"✅ Response received")
        print(f"📊 Tokens: {input_tokens} in + {output_tokens} out = {input_tokens + output_tokens}")
        print(f"💰 Cost: ${cost:.6f}\n")

        # Save to DB
        self.save_message("user", prompt, input_tokens, 0)
        self.save_message("assistant", assistant_message, output_tokens, cost)

        # Parse code blocks
        code_blocks = CodeBlockParser.extract_code_blocks(assistant_message)

        if not code_blocks:
            print("ℹ️  No code blocks found in response")
            return {
                "success": True,
                "response": assistant_message,
                "code_blocks": [],
                "files_created": [],
                "tokens": input_tokens + output_tokens,
                "cost": cost
            }

        print(f"📝 Found {len(code_blocks)} code block(s)")

        # Process code blocks
        files_created = []
        for i, block in enumerate(code_blocks, 1):
            print(f"\n{'─'*70}")
            print(f"Code Block {i}/{len(code_blocks)}")
            print(f"{'─'*70}")
            print(f"Language: {block['language']}")
            print(f"Lines:    {block['lines']}")

            # Suggest filename
            suggested_path = CodeBlockParser.suggest_filename(
                block['code'],
                block['language'],
                prompt
            )

            print(f"Suggested: {suggested_path}")

            # Save file
            file_path = self.repo_path / suggested_path
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(block['code'])

            print(f"✅ Saved: {file_path}")
            files_created.append(str(suggested_path))
            self.log_action("file_created", str(suggested_path))

        # Git operations
        if auto_commit and files_created:
            print(f"\n{'='*70}")
            print("🔧 GIT OPERATIONS")
            print(f"{'='*70}")

            # Add files
            for file_path in files_created:
                success = self.git.add(file_path)
                if success:
                    print(f"✅ git add {file_path}")
                else:
                    print(f"❌ Failed to add {file_path}")

            # Commit
            commit_msg = CodeBlockParser.generate_commit_message(files_created, prompt)
            success, output = self.git.commit(commit_msg)

            if success:
                # Extract commit hash
                commit_hash = output.split()[1] if output else "unknown"
                print(f"✅ git commit {commit_hash}")
                print(f"   {commit_msg.split(chr(10))[0]}")
                self.log_action("git_commit", commit_hash=commit_hash)

                # Push
                success, output = self.git.push()
                if success:
                    print(f"✅ git push origin main")
                    self.log_action("git_push", commit_hash=commit_hash)
                else:
                    print(f"❌ git push failed: {output}")
                    self.log_action("git_push", commit_hash=commit_hash, success=False, error=output)
            else:
                print(f"❌ git commit failed: {output}")
                self.log_action("git_commit", success=False, error=output)

        return {
            "success": True,
            "response": assistant_message,
            "code_blocks": code_blocks,
            "files_created": files_created,
            "tokens": input_tokens + output_tokens,
            "cost": cost
        }


def main():
    parser = argparse.ArgumentParser(description="AI Development Agent")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--repo-path", default=".", help="Repository path")
    parser.add_argument("--session", default="default", help="Session name")
    parser.add_argument("--prompt", required=True, help="Development prompt")
    parser.add_argument("--auto-commit", action="store_true", help="Auto commit and push")
    parser.add_argument("--json-output", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        agent = DevAgent(args.project, args.repo_path, args.session)
        result = agent.process_prompt(args.prompt, args.auto_commit)

        if args.json_output:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'='*70}")
            print("✅ AGENT COMPLETED")
            print(f"{'='*70}")
            print(f"Files created: {len(result['files_created'])}")
            for f in result['files_created']:
                print(f"  • {f}")
            print(f"\n💰 Total cost: ${result['cost']:.6f}")
            print(f"📊 Total tokens: {result['tokens']:,}")

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())