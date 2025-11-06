# Manual VS Code Verification Guide

## 1. Check TypeScript Version

### Step-by-Step:

1. **Open any .tsx file:**
   ```bash
   code /workspace/492-energy-defense/frontend/src/pages/LoginPage.tsx
   ```

2. **Look at bottom right corner of VS Code:**
   - You should see: `TypeScript 5.x.x` or `{} TypeScript`
   
3. **Click on the TypeScript version text**
   - A menu will appear at the top
   - Select: **"Use Workspace Version"**
   - It should show TypeScript 5.9.3

### If you don't see TypeScript version:
- Make sure you're in a `.ts` or `.tsx` file
- The file must be open and active

## 2. Manually Install Extensions

### Open Extensions Panel:
- Press `Cmd/Ctrl + Shift + X`
- Or click the Extensions icon in left sidebar (4 squares icon)

### Install These Extensions One by One:

#### For TypeScript/React:

1. **ESLint**
   - Search: `dbaeumer.vscode-eslint`
   - Click "Install"

2. **Prettier - Code formatter**
   - Search: `esbenp.prettier-vscode`
   - Click "Install"

3. **Tailwind CSS IntelliSense**
   - Search: `bradlc.vscode-tailwindcss`
   - Click "Install"

#### For Python:

4. **Python**
   - Search: `ms-python.python`
   - Click "Install"

5. **Pylance**
   - Search: `ms-python.vscode-pylance`
   - Click "Install"

6. **Black Formatter**
   - Search: `ms-python.black-formatter`
   - Click "Install"

## 3. Verify Node Modules Exist

### Check in Terminal:

```bash
# Check if node_modules exists
ls -la /workspace/492-energy-defense/frontend/node_modules/

# Should show lots of directories

# Check specific packages
ls /workspace/492-energy-defense/frontend/node_modules/react
ls /workspace/492-energy-defense/frontend/node_modules/typescript
```

### Expected output:
Both commands should show files/directories, NOT "No such file or directory"

## 4. Check for Import Errors

### Open LoginPage.tsx:

```bash
code /workspace/492-energy-defense/frontend/src/pages/LoginPage.tsx
```

### Look for these lines at the top:

```typescript
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
```

### What to check:

**BAD (Still has errors):**
- Red squiggly lines under imports
- Error message: "Cannot find module 'react'"
- Hover shows error

**GOOD (Fixed):**
- No red lines
- Imports are green/blue (syntax highlighted)
- Hover shows type information
- No error messages

## 5. Force TypeScript to Reload

If you still see errors:

### Method 1: Restart TS Server
1. Press `Cmd/Ctrl + Shift + P` (Command Palette)
2. Type: `TypeScript: Restart TS Server`
3. Press Enter
4. Wait 5 seconds

### Method 2: Reload Window
1. Press `Cmd/Ctrl + Shift + P`
2. Type: `Developer: Reload Window`
3. Press Enter

### Method 3: Close and Reopen File
1. Close the .tsx file
2. Wait 2 seconds
3. Reopen it

## 6. Check VS Code Settings

### Open Settings:
1. Press `Cmd/Ctrl + Shift + P`
2. Type: `Preferences: Open User Settings (JSON)`
3. Press Enter

### Check workspace settings exist:
```bash
cat /workspace/492-energy-defense/.vscode/settings.json
```

Should show content like:
```json
{
  "typescript.tsdk": "frontend/node_modules/typescript/lib",
  ...
}
```

## 7. Verify Python Packages

### Check Python interpreter:
1. Press `Cmd/Ctrl + Shift + P`
2. Type: `Python: Select Interpreter`
3. Choose Python 3.x from the list

### Check packages installed:
```bash
pip3 list | grep fastapi
pip3 list | grep sqlalchemy
pip3 list | grep pydantic
```

Should show versions for each.

## 8. Test Autocomplete

### In LoginPage.tsx:

1. Go to an empty line
2. Type: `const [state, setSt`
3. Press `Ctrl + Space` (force autocomplete)

**Should show:**
- Autocomplete suggestions
- `setState` option
- Type hints

### In a .py file:

```bash
code /workspace/492-energy-defense/backend/api/main.py
```

1. Go to an empty line
2. Type: `from fastapi import `
3. Should show autocomplete with FastAPI imports

## 9. Check for Workspace Errors

### Open Problems Panel:
1. Press `Cmd/Ctrl + Shift + M`
2. Or View → Problems

### What to check:
- How many errors are listed?
- Are they all TypeScript/import errors?
- Or are there actual code errors?

**If you see many "Cannot find module" errors:**
- Node modules might not be installed correctly
- See Section 10 below

## 10. Reinstall Dependencies (If Needed)

### If node_modules is missing or incomplete:

```bash
cd /workspace/492-energy-defense/frontend

# Remove and reinstall
rm -rf node_modules package-lock.json
npm install

# Should take 1-2 minutes
# Should say "added 340 packages"
```

### Verify it worked:
```bash
ls node_modules/react
ls node_modules/typescript
```

Both should show files.

## 11. Quick Diagnostic Command

Run this all-in-one check:

```bash
cd /workspace/492-energy-defense

echo "=== Checking Frontend ==="
echo "Node modules exists:"
ls frontend/node_modules/ &>/dev/null && echo "✓ YES" || echo "✗ NO"

echo ""
echo "React installed:"
ls frontend/node_modules/react &>/dev/null && echo "✓ YES" || echo "✗ NO"

echo ""
echo "TypeScript installed:"
ls frontend/node_modules/typescript &>/dev/null && echo "✓ YES" || echo "✗ NO"

echo ""
echo "=== Checking VS Code Config ==="
echo "Settings file exists:"
ls .vscode/settings.json &>/dev/null && echo "✓ YES" || echo "✗ NO"

echo ""
echo "Extensions file exists:"
ls .vscode/extensions.json &>/dev/null && echo "✓ YES" || echo "✗ NO"

echo ""
echo "=== Checking Backend ==="
echo "FastAPI installed:"
pip3 list | grep -q fastapi && echo "✓ YES" || echo "✗ NO"

echo ""
echo "SQLAlchemy installed:"
pip3 list | grep -q sqlalchemy && echo "✓ YES" || echo "✗ NO"
```

### Expected output:
All should show `✓ YES`

## 12. Nuclear Option - Complete Reset

If nothing works, do a complete reinstall:

```bash
cd /workspace/492-energy-defense

# Remove everything
rm -rf frontend/node_modules frontend/package-lock.json
rm -rf .vscode

# Reinstall
cd frontend
npm install
cd ..

# Recreate VS Code config
cat > .vscode/settings.json << 'EOF'
{
  "typescript.tsdk": "frontend/node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true
}
EOF

# Restart VS Code completely (quit and reopen)
```

## 13. Expected Final State

### When everything is working:

**✓ In LoginPage.tsx:**
- No red squiggly lines on imports
- Autocomplete works when typing
- Hover shows type information
- Bottom right shows TypeScript version

**✓ In Terminal:**
```bash
ls frontend/node_modules/ | wc -l
# Shows: 300+

npm list react typescript
# Shows versions without errors
```

**✓ Extensions installed:**
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)

**✓ VS Code settings:**
```bash
cat .vscode/settings.json
# Shows proper TypeScript config
```

## Common Issues and Solutions

### Issue: "Cannot find module 'react'" persists

**Solution:**
1. Verify node_modules exists: `ls frontend/node_modules/react`
2. Select workspace TypeScript (bottom right corner)
3. Restart TS server: `Cmd/Ctrl+Shift+P` → "TypeScript: Restart TS Server"
4. If still fails: reinstall with `npm install` in frontend folder

### Issue: TypeScript version not showing

**Solution:**
1. Make sure you're in a `.ts` or `.tsx` file
2. Click anywhere in the file to make it active
3. Look at bottom right corner
4. If missing, install TypeScript extension

### Issue: No autocomplete

**Solution:**
1. Install ESLint and Prettier extensions
2. Restart VS Code
3. Open file and press `Ctrl+Space` to trigger autocomplete
4. Check that TypeScript language service is running

### Issue: Extensions not installing

**Solution:**
1. Check internet connection
2. Try installing from VS Code marketplace website
3. Reload VS Code
4. Check VS Code extensions folder: `~/.vscode/extensions/`

## Still Not Working?

### Get detailed diagnostics:

```bash
# Check VS Code version
code --version

# Check Node version
node --version

# Check npm version
npm --version

# List installed VS Code extensions
code --list-extensions

# Check TypeScript installation
npx tsc --version
```

Share these outputs if you need more help!

---

## Quick Checklist

Run through this checklist:

- [ ] Ran `cd frontend && npm install` (completed successfully)
- [ ] File `frontend/node_modules/react` exists
- [ ] File `frontend/node_modules/typescript/lib/typescript.js` exists
- [ ] File `.vscode/settings.json` exists
- [ ] Opened LoginPage.tsx in VS Code
- [ ] Bottom right shows TypeScript version
- [ ] Clicked TypeScript version → Selected "Use Workspace Version"
- [ ] Pressed `Cmd/Ctrl+Shift+P` → "TypeScript: Restart TS Server"
- [ ] Waited 5 seconds
- [ ] No red squiggly lines under `import React from 'react'`
- [ ] Installed extensions: ESLint, Prettier, Python
- [ ] Restarted VS Code completely

If all checked ✓ and still have errors → try Nuclear Option in Section 12
