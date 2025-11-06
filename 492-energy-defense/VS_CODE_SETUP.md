# VS Code Development Environment Setup

## The Problem

When you open `.tsx` files in VS Code, you see:
```
Cannot find module 'react' or its corresponding type declarations.ts(2307)
```

This happens because **dependencies are only in Docker containers**, not on your local machine.

## ✅ FIXED - Dependencies Installed

I've already installed all dependencies for you:

✅ **Frontend dependencies** (React, TypeScript, etc.) - Installed in `frontend/node_modules/`  
✅ **Backend dependencies** (FastAPI, SQLAlchemy, etc.) - Installed via pip  
✅ **VS Code settings** - Created in `.vscode/settings.json`  
✅ **Extension recommendations** - Created in `.vscode/extensions.json`  

## 🔄 Restart VS Code

**The TypeScript errors should now be gone after restarting VS Code:**

1. Close VS Code completely
2. Reopen: `code /workspace/492-energy-defense`
3. When prompted, **Install Recommended Extensions**

## ✅ Verify It Worked

### Check 1: Open LoginPage.tsx

```bash
code frontend/src/pages/LoginPage.tsx
```

You should see:
- ✅ No red squiggly lines under `import React from 'react'`
- ✅ Autocomplete works when typing React components
- ✅ Type hints appear on hover

### Check 2: Open a Backend File

```bash
code backend/api/main.py
```

You should see:
- ✅ No import errors
- ✅ Autocomplete for FastAPI
- ✅ Type hints for Pydantic models

## 📦 What Was Installed

### Frontend (Node.js)
```bash
cd /workspace/492-energy-defense/frontend
ls node_modules/
```

You should see 340+ packages including:
- react
- react-dom
- typescript
- vite
- tailwindcss
- axios
- And many more...

### Backend (Python)
```bash
pip3 list | grep fastapi
```

Should show:
- fastapi
- sqlalchemy
- pydantic
- And other backend dependencies

## 🎨 VS Code Extensions (Recommended)

When you restart VS Code, install these recommended extensions:

### Frontend Development
- **ESLint** - JavaScript/TypeScript linting
- **Prettier** - Code formatting
- **Tailwind CSS IntelliSense** - Tailwind class suggestions

### Backend Development
- **Python** - Python language support
- **Pylance** - Python type checking
- **Black Formatter** - Python code formatting

### General
- **TypeScript** - Enhanced TypeScript support

VS Code will prompt you to install these automatically.

## ⚙️ VS Code Settings Applied

I've configured `.vscode/settings.json` with:

```json
{
  "editor.formatOnSave": true,
  "typescript.tsdk": "frontend/node_modules/typescript/lib",
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

This enables:
- ✅ Auto-format on save
- ✅ TypeScript from local node_modules
- ✅ Prettier for TypeScript/React
- ✅ Black for Python

## 🔧 If You Still See Errors

### TypeScript Errors After Restart

1. **Select TypeScript version:**
   - Open any `.tsx` file
   - Bottom right corner → Click TypeScript version
   - Select "Use Workspace Version"

2. **Reload VS Code:**
   - Press `Cmd/Ctrl + Shift + P`
   - Type "Reload Window"
   - Press Enter

3. **Check node_modules exists:**
   ```bash
   ls /workspace/492-energy-defense/frontend/node_modules/react
   ```
   Should show files, not "No such file"

### Python Import Errors

1. **Select Python interpreter:**
   - Press `Cmd/Ctrl + Shift + P`
   - Type "Python: Select Interpreter"
   - Choose Python 3.x from the list

2. **Check pip packages:**
   ```bash
   pip3 list | grep fastapi
   ```
   Should show fastapi and related packages

## 🚀 Running the Application

**Important:** Development dependencies are for VS Code intellisense only.

**To actually run the app, use Docker:**

```bash
cd /workspace/492-energy-defense
./fix-and-restart.sh
```

Or:
```bash
docker-compose up --build
```

**Do NOT run `npm run dev` or `uvicorn` directly** - use Docker for the actual application.

## 📁 Project Structure with Dependencies

```
492-energy-defense/
├── frontend/
│   ├── node_modules/          ← 340+ packages (for VS Code)
│   ├── src/
│   │   ├── pages/
│   │   │   └── LoginPage.tsx  ← No more React errors!
│   │   └── ...
│   └── package.json
├── backend/
│   ├── api/
│   │   └── main.py            ← Autocomplete works!
│   └── requirements.txt
└── .vscode/
    ├── settings.json          ← VS Code config
    └── extensions.json        ← Recommended extensions
```

## 🎯 Development Workflow

### 1. Edit Code in VS Code
- Full TypeScript/Python intellisense
- No import errors
- Autocomplete works
- Type hints visible

### 2. Run in Docker
```bash
./fix-and-restart.sh
```

### 3. Test in Browser
- Frontend: http://localhost:3000
- API: http://localhost:8000/api/docs

### 4. View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🔄 Keeping Dependencies Updated

### When package.json Changes

```bash
cd /workspace/492-energy-defense/frontend
npm install
```

### When requirements.txt Changes

```bash
cd /workspace/492-energy-defense/backend
pip3 install -r requirements.txt --user
```

### Full Refresh

```bash
cd /workspace/492-energy-defense
./setup-dev-environment.sh
```

## 💡 Why We Need Local Dependencies

**Docker containers** run the app in production-like environment.

**Local dependencies** provide:
- VS Code intellisense and autocomplete
- Type checking and error detection
- Import resolution
- Documentation on hover
- Better development experience

Both are needed for optimal development!

## ✅ Checklist

After restarting VS Code, verify:

- [ ] No red squiggly lines in LoginPage.tsx
- [ ] `import React from 'react'` has no errors
- [ ] Autocomplete works when typing React components
- [ ] Hover shows type information
- [ ] Python imports work in backend files
- [ ] VS Code extensions installed
- [ ] Bottom right shows "TypeScript 5.x.x"

## 🎉 You're Ready!

Your VS Code development environment is now fully configured for:
- ✅ TypeScript/React development with full intellisense
- ✅ Python/FastAPI development with type hints
- ✅ Auto-formatting on save
- ✅ Linting and error detection
- ✅ Production-like testing via Docker

**Happy coding!** 🚀

---

**Need help?** Check:
- `QUICK_FIX_SUMMARY.md` - Application fixes
- `START_HERE.md` - Getting started guide
- `README.md` - Complete documentation
