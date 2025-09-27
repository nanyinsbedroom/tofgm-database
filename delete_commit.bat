@echo off
setlocal enabledelayedexpansion

REM Set variables
set "BRANCH_NAME=latest_branch"
set "COMMIT_MESSAGE=Update"
set "REMOTE_NAME=origin"
set "DEFAULT_BRANCH=main"

REM Check if we're in a git repository
git status >nul 2>&1
if errorlevel 1 (
    echo ERROR: Not a git repository or git command not found.
    echo Please run this script from within a git repository.
    pause
    exit /b 1
)

echo Current repository status:
git remote -v
echo.
git branch
echo.

echo WARNING: This script will permanently delete all commit history!
echo Current files will be kept, but all history will be lost.
echo.
set /p "CONFIRM=Are you sure you want to continue? (y/N): "

if /i not "!CONFIRM!"=="y" (
    echo Operation cancelled.
    pause
    exit /b 0
)

echo.
echo Starting cleanup process...
echo.

REM Step 1: Create orphan branch
echo Step 1/6: Creating orphan branch...
git checkout --orphan %BRANCH_NAME%
if errorlevel 1 (
    echo ERROR: Failed to create orphan branch.
    pause
    exit /b 1
)

REM Step 2: Add all files
echo Step 2/6: Adding all files to staging...
git add -A
if errorlevel 1 (
    echo ERROR: Failed to add files to staging.
    pause
    exit /b 1
)

REM Step 3: Commit changes
echo Step 3/6: Committing changes...
git commit -am "%COMMIT_MESSAGE%"
if errorlevel 1 (
    echo ERROR: Failed to commit changes.
    pause
    exit /b 1
)

REM Step 4: Delete main branch
echo Step 4/6: Deleting main branch...
git branch -D %DEFAULT_BRANCH%
if errorlevel 1 (
    echo WARNING: Failed to delete main branch (may not exist yet)
)

REM Step 5: Rename current branch to main
echo Step 5/6: Renaming branch to main...
git branch -m %DEFAULT_BRANCH%
if errorlevel 1 (
    echo ERROR: Failed to rename branch.
    pause
    exit /b 1
)

REM Step 6: Force push to remote
echo Step 6/6: Force pushing to remote repository...
git push -f %REMOTE_NAME% %DEFAULT_BRANCH%
if errorlevel 1 (
    echo ERROR: Failed to push to remote repository.
    echo You may need to manually run: git push -f origin main
    pause
    exit /b 1
)

echo.
echo ===============================================
echo SUCCESS: Repository history has been cleaned up!
echo ===============================================
echo.
echo Your repository now has only one commit with all current files.
echo Old commit history has been permanently removed.

pause