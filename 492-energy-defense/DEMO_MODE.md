# 🎭 Demo Mode - Role Switching

**Status:** ✅ Implemented

---

## 🎯 **What Changed**

### **Before (Authentication Mode):**
- ❌ Required login page
- ❌ Had to log in with username/password
- ❌ Had to log out and log back in to test different roles
- ❌ Complex authentication flow

### **After (Demo Mode):**
- ✅ No login required
- ✅ Toggle between roles instantly
- ✅ Quick role switching in header
- ✅ Perfect for demos and development

---

## 🚀 **How to Use**

### 1. **Start the System**

```bash
cd /workspace/492-energy-defense
docker compose up -d
```

### 2. **Open Dashboard**

Navigate to: **http://localhost:3000**

You'll immediately see the dashboard - no login needed!

### 3. **Switch Roles**

In the top-right corner of the dashboard, you'll see three role buttons:

🛡️ **Admin** (Red) - Full system access
- View all dashboards
- Configure AI agent weights
- Access all features

📊 **Analyst** (Blue) - Analysis & feedback
- View dashboards and alerts
- Submit AI feedback
- Generate reports

👁️ **Observer** (Green) - Read-only
- View dashboards only
- Monitor trends
- No configuration access

**Click any role button to instantly switch!**

---

## 🎨 **UI Components**

### **Role Switcher**

Located in the header, shows three buttons:
- **Active role:** Highlighted with color and shadow
- **Inactive roles:** Gray, hover to preview
- **Instant switching:** No page reload required

### **Current User Info**

Next to role switcher:
- Shows current username (admin/analyst/observer)
- Updates immediately when role changes
- Clear visual indicator of active role

---

## 🔧 **Technical Changes**

### 1. **AuthContext Simplified**

**File:** `frontend/src/context/AuthContext.tsx`

**Before:**
```typescript
- Login with API
- Fetch user data
- Store tokens
- Handle logout
```

**After:**
```typescript
- Local role state
- Switch role instantly
- No API calls needed
- Demo user created on-the-fly
```

### 2. **Removed Login Page**

**Files Removed:**
- Login page route
- Authentication requirement
- Protected route wrapper

**Why:** Not needed in demo mode

### 3. **Added Role Switcher**

**File:** `frontend/src/components/RoleSwitcher.tsx`

**Features:**
- Three role buttons with icons
- Color-coded (Red/Blue/Green)
- Hover tooltips
- Instant switching

### 4. **Updated Dashboard Layout**

**File:** `frontend/src/components/DashboardLayout.tsx`

**Changes:**
- Added "Demo Mode" subtitle
- Integrated RoleSwitcher component
- Removed logout button
- Simplified header

### 5. **Updated App Router**

**File:** `frontend/src/App.tsx`

**Changes:**
- All routes now public
- Removed ProtectedRoute wrapper
- Removed login route
- Direct access to dashboard

---

## 📋 **Role Capabilities**

### 🛡️ **Admin**

**Can:**
- ✅ View all dashboards
- ✅ Configure AI agent weights
- ✅ Access AI configuration page
- ✅ Submit feedback
- ✅ View vulnerabilities
- ✅ Full system access

**Navigation:**
- Dashboard
- Vulnerabilities
- AI Config
- Feedback

---

### 📊 **Analyst**

**Can:**
- ✅ View all dashboards
- ✅ Submit AI feedback
- ✅ View vulnerabilities
- ✅ Generate reports

**Cannot:**
- ❌ Configure AI weights
- ❌ Access admin settings

**Navigation:**
- Dashboard
- Vulnerabilities
- Feedback
- ~~AI Config~~ (read-only or restricted)

---

### 👁️ **Observer**

**Can:**
- ✅ View dashboards
- ✅ Monitor trends
- ✅ See alerts

**Cannot:**
- ❌ Submit feedback
- ❌ Configure anything
- ❌ Modify data

**Navigation:**
- Dashboard
- Vulnerabilities (read-only)
- ~~AI Config~~ (hidden)
- ~~Feedback~~ (hidden)

---

## 🎓 **Use Cases**

### **1. Demos & Presentations**

Quickly switch between roles to show:
- How different users see the system
- Role-based access control
- Feature availability by role

**Example:**
```
"As an admin, I can configure AI weights..."
*click Admin button*
"As an analyst, I can only submit feedback..."
*click Analyst button*
"As an observer, I can only view data..."
*click Observer button*
```

### **2. Development & Testing**

Test features from different perspectives:
- Admin: Test configuration features
- Analyst: Test analysis tools
- Observer: Test read-only views

No need to log in/out repeatedly!

### **3. Training**

Show new users what each role can do:
- Switch roles live
- Demonstrate permissions
- Explain access levels

---

## 🔒 **Security Note**

⚠️ **This is Demo Mode!**

**Not suitable for production without modifications:**
- No actual authentication
- No password protection
- No session management
- Anyone can switch roles

**For production, you would need to:**
1. Re-enable authentication
2. Add login page back
3. Validate role changes server-side
4. Add proper authorization

**This mode is perfect for:**
- ✅ Local development
- ✅ Demos and presentations
- ✅ Testing and QA
- ✅ Training sessions

---

## 🎯 **Benefits**

### **Speed**
- ⚡ Instant role switching
- ⚡ No login delays
- ⚡ No page reloads

### **Simplicity**
- 🎯 One-click switching
- 🎯 Clear visual indicators
- 🎯 Intuitive UI

### **Flexibility**
- 🔄 Test any role instantly
- 🔄 Compare role views
- 🔄 Demo-friendly

---

## 📱 **Mobile Responsive**

Role switcher adapts to screen size:
- **Desktop:** Full labels and icons
- **Tablet:** Compact view
- **Mobile:** Stacked or dropdown

---

## 🎨 **Customization**

### **Change Default Role**

Edit `frontend/src/context/AuthContext.tsx`:

```typescript
const [currentRole, setCurrentRole] = useState<UserRole>(() => {
  const savedRole = localStorage.getItem('demo_role');
  return (savedRole as UserRole) || 'admin'; // Change 'admin' to 'analyst' or 'observer'
});
```

### **Add More Roles**

Edit `frontend/src/components/RoleSwitcher.tsx`:

```typescript
const roles = [
  // ... existing roles
  {
    value: 'superadmin',
    label: 'Super Admin',
    icon: <Crown className="w-4 h-4" />,
    color: 'bg-purple-500 hover:bg-purple-600',
    description: 'Ultimate access',
  },
];
```

### **Change Colors**

Edit the `color` property in RoleSwitcher:

```typescript
color: 'bg-red-500 hover:bg-red-600',  // Admin
color: 'bg-blue-500 hover:bg-blue-600', // Analyst
color: 'bg-green-500 hover:bg-green-600', // Observer
```

---

## 🔄 **Reverting to Auth Mode**

If you need to add authentication back:

1. **Restore AuthContext** with API calls
2. **Add LoginPage** back to routes
3. **Add ProtectedRoute** wrapper
4. **Remove RoleSwitcher** from header
5. **Add logout** button back

Files to modify:
- `frontend/src/context/AuthContext.tsx`
- `frontend/src/App.tsx`
- `frontend/src/components/DashboardLayout.tsx`
- Create `frontend/src/pages/LoginPage.tsx`

---

## ✅ **Testing**

### **Test Role Switching:**

1. Open http://localhost:3000
2. See default role (Admin)
3. Click "Analyst" button
4. Verify:
   - Username changes to "analyst"
   - Some features become restricted
   - Button highlights change
5. Click "Observer" button
6. Verify:
   - Username changes to "observer"
   - More features become restricted
   - Read-only view
7. Click "Admin" button
8. Verify:
   - Back to full access
   - All features available

### **Test Persistence:**

1. Switch to "Analyst"
2. Refresh page (F5)
3. Should still be "Analyst"
4. Role persists in localStorage

### **Test Navigation:**

1. Switch to "Observer"
2. Navigate to different pages
3. Role remains consistent
4. Restrictions apply everywhere

---

## 🎉 **Result**

**You now have a demo-friendly system where you can:**
- ✅ Skip login completely
- ✅ Toggle between roles with one click
- ✅ Showcase different perspectives instantly
- ✅ Perfect for presentations and development

**No more logging in and out!** 🚀
