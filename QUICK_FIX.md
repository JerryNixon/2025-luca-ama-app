# 🚨 **IMMEDIATE ACTION REQUIRED - Database Connection Fix**

## **Problem Identified**
Your ODBC driver doesn't support `ActiveDirectoryDefault` authentication method, causing the backend to fail.

## **🔧 SOLUTION: Use SQLite for Development**

### **Step 1: Verify Current Configuration**
Your `.env` file is now set to use SQLite by default:
```
USE_SQLITE=True
```

### **Step 2: Start the Backend (Fixed)**
1. **Open terminal** in VS Code
2. **Navigate to backend directory**:
   ```powershell
   cd backend
   ```

3. **Run migrations** (with SQLite):
   ```powershell
   python manage.py migrate
   ```

4. **Create a superuser**:
   ```powershell
   python manage.py createsuperuser
   ```
   - Email: `admin@test.com`
   - Name: `Admin User`
   - Password: `admin123`

5. **Start the server**:
   ```powershell
   python manage.py runserver 127.0.0.1:8000
   ```

### **Step 3: Test the Backend**
1. **Open browser** to: http://127.0.0.1:8000/admin/
2. **Login** with admin credentials
3. **Verify** you can see the database tables

### **Step 4: Start the Frontend**
1. **Open NEW terminal**
2. **Navigate to frontend**:
   ```powershell
   cd frontend
   ```
3. **Install dependencies**:
   ```powershell
   npm install
   ```
4. **Start frontend**:
   ```powershell
   npm run dev
   ```

### **Step 5: Test Full Application**
1. **Open browser** to: http://localhost:3000
2. **Login** with admin credentials
3. **Test creating events and questions**

## **🔄 Switching to Fabric SQL Later**

When you want to use Fabric SQL (production):

1. **Update `.env`**:
   ```
   USE_SQLITE=False
   AUTH_METHOD=ActiveDirectoryInteractive
   ```

2. **Test connection**:
   ```powershell
   python test_db_connection.py
   ```

3. **Run migrations**:
   ```powershell
   python manage.py migrate
   ```

## **🎯 Expected Results**

After following these steps, you should see:
- ✅ Backend starts without database errors
- ✅ Django admin accessible
- ✅ Frontend connects to backend
- ✅ Full application workflow works

## **📞 If Still Having Issues**

Run the database test script:
```powershell
python test_db_connection.py
```

This will test both SQLite and Fabric SQL connections and provide specific error details.

---

**🚀 START HERE: Run the commands in Step 2 to get your backend working!**
