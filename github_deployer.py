"""
================================================================================
GITHUB DEPLOYER — Auto Deploy Blog to GitHub Pages
================================================================================
Features:
    - Commit and push blog content to GitHub repo
    - Trigger GitHub Pages deployment
    - Support for custom domain
================================================================================
"""

import os
import subprocess
import logging
import shutil
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIGURATION ====================
GH_TOKEN = os.getenv("GH_TOKEN", "")
GH_REPO = os.getenv("GH_BLOG_REPO", os.getenv("GH_REPO", ""))  # e.g., username/topik-blog
GH_BRANCH = os.getenv("GH_BLOG_BRANCH", "gh-pages")
GH_USER_NAME = os.getenv("GH_USER_NAME", "TOPIK Bot")
GH_USER_EMAIL = os.getenv("GH_USER_EMAIL", "bot@topikdaily.com")


class GitHubDeployer:
    """Deploy static files to GitHub Pages"""
    
    def __init__(self, repo: str = GH_REPO, token: str = GH_TOKEN, branch: str = GH_BRANCH):
        self.repo = repo
        self.token = token
        self.branch = branch
        self.temp_dir = "temp_gh_deploy"
        
    def is_available(self) -> bool:
        return bool(self.repo and self.token)
    
    def run_command(self, cmd: str, cwd: str = None) -> tuple:
        """Run shell command"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def deploy(self, source_dir: str, commit_message: str = None) -> bool:
        """
        Deploy directory to GitHub Pages
        
        Args:
            source_dir: Directory containing files to deploy
            commit_message: Commit message
            
        Returns:
            Success status
        """
        if not self.is_available():
            logging.error("❌ GitHub not configured. Set GH_TOKEN and GH_BLOG_REPO")
            return False
        
        if not os.path.exists(source_dir):
            logging.error(f"❌ Source directory not found: {source_dir}")
            return False
        
        if commit_message is None:
            commit_message = f"Deploy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Clean temp directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        try:
            # Clone repo
            repo_url = f"https://{self.token}@github.com/{self.repo}.git"
            logging.info(f"📥 Cloning {self.repo}...")
            
            success, out, err = self.run_command(
                f'git clone --branch {self.branch} --single-branch "{repo_url}" {self.temp_dir}'
            )
            
            if not success:
                # Branch doesn't exist, create orphan
                logging.info(f"🔧 Creating new branch {self.branch}...")
                success, _, _ = self.run_command(f'git clone "{repo_url}" {self.temp_dir}')
                if success:
                    self.run_command(f"git checkout --orphan {self.branch}", self.temp_dir)
                    self.run_command("git rm -rf .", self.temp_dir)
            
            # Copy files
            logging.info("📁 Copying files...")
            for item in os.listdir(source_dir):
                src = os.path.join(source_dir, item)
                dst = os.path.join(self.temp_dir, item)
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            # Add CNAME if custom domain
            custom_domain = os.getenv("GH_CUSTOM_DOMAIN", "")
            if custom_domain:
                with open(os.path.join(self.temp_dir, "CNAME"), "w") as f:
                    f.write(custom_domain)
            
            # Add .nojekyll for GitHub Pages
            open(os.path.join(self.temp_dir, ".nojekyll"), "w").close()
            
            # Configure git
            self.run_command(f'git config user.name "{GH_USER_NAME}"', self.temp_dir)
            self.run_command(f'git config user.email "{GH_USER_EMAIL}"', self.temp_dir)
            
            # Commit and push
            logging.info("📤 Pushing to GitHub...")
            self.run_command("git add -A", self.temp_dir)
            self.run_command(f'git commit -m "{commit_message}"', self.temp_dir)
            
            success, out, err = self.run_command(
                f"git push origin {self.branch} --force", 
                self.temp_dir
            )
            
            if success:
                logging.info(f"✅ Deployed to https://{self.repo.split('/')[0]}.github.io/{self.repo.split('/')[1]}/")
                return True
            else:
                logging.error(f"❌ Push failed: {err}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Deploy error: {e}")
            return False
        finally:
            # Cleanup
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)


def deploy_blog_to_github(blog_dir: str = "blog_output") -> bool:
    """
    Main function to deploy blog to GitHub Pages
    
    Args:
        blog_dir: Directory containing blog files
        
    Returns:
        Success status
    """
    deployer = GitHubDeployer()
    return deployer.deploy(blog_dir)


# ==================== CLI ====================
if __name__ == "__main__":
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    
    parser = argparse.ArgumentParser(description="Deploy blog to GitHub Pages")
    parser.add_argument("--source", default="blog_output", help="Source directory")
    parser.add_argument("--message", default=None, help="Commit message")
    
    args = parser.parse_args()
    
    if os.path.exists(args.source):
        success = deploy_blog_to_github(args.source)
        print(f"{'✅ Deployed!' if success else '❌ Failed!'}")
    else:
        print(f"❌ Directory not found: {args.source}")
