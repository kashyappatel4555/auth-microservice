# **Auth Service** 🔐  

This project provides an authentication service using **Django** and **Django REST Framework (DRF)**. It includes features such as:  

✅ **User Registration**  
✅ **Email & OTP Verification**  
✅ **OTP-Based Login**  
✅ **Password Reset**  
✅ **Account Updates**  

---

## **🛠 Prerequisites**  

Ensure you have the following installed before proceeding:  

- **Python** (>= 3.8)  
- **Django** (>= 5.1.6)  
- **Django REST Framework**  
- **Twilio** (for sending OTPs via SMS)  
- **SMTP Server** (for sending emails)  

---

## **📥 Installation**  

### **1️⃣ Clone the Repository**  
```bash
git clone https://github.com/yourusername/auth_service.git
cd auth_service
```
### **2️⃣ Create a Virtual Environment**  
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```
### **3️⃣ Install Dependencies**  
After activating the virtual environment, install all required dependencies using:  

```bash
pip install -r requirements.txt
```
### **4️⃣ Set Up Environment Variables**  
Create a `.env` file in the project's root directory and add the following environment variables and add your credentials, for TWILIO credentials you have create an account on TWILIO:

```env
# Email settings
EMAIL_HOST=smtp.yourmailserver.com (i.e. smtp.gmail.com)
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password

# Twilio settings
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
```
### **5️⃣ Run Migrations**  
Run the following command to create and apply database migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```
### **6️⃣ Run the Development Server**  
Start the Django development server by running:

```bash
python manage.py runserver
```
## 📝 API Endpoints

Below are the available API endpoints for authentication services:

### **🔹 Register a New User**
**Endpoint:**  
`POST /api/auth/register/`  

**Request Body:**
```json
{
    "username": "newuser",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "email": "john.doe@example.com",
    "password": "securepassword"
}
```
### **🔹 Verify Email OTP**  
**Endpoint:**  
`POST /api/auth/verify-email/`  

**Request Body:**  
```json
{
    "email": "john.doe@example.com",
    "otp": "123456"
}
```
### **🔹 Request OTP for Login**  
**Endpoint:**  
`POST /api/auth/login/request-otp/`  

**Request Body:**  
```json
{
    "phone_number": "+1234567890"
}
```
### **🔹 Request Password Reset**  
**Endpoint:**  
`POST /api/auth/reset-password-request/`  

**Request Body:**  
```json
{
    "email": "john.doe@example.com"
}
```
### **🔹 Reset Password**  
**Endpoint:**  
`POST /api/auth/reset-password/<token>/`  

**Request Body:**  
```json
{
    "email": "john.doe@example.com",
    "new_password": "newsecurepassword",
    "confirm_password": "newsecurepassword"
}
```
### **🔹 Update Account Information**  
**Endpoint:**  
`PATCH /api/auth/update-account/`  

**Request Body:**  
```json
{
    "username": "updateduser",
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@example.com",
    "phone_number": "+0987654321",
    "password": "newsecurepassword"
}
```
### 🔸 Note  
When making a request to `PATCH /api/auth/update-account/`, ensure you include the Authorization header with a Bearer token:  

```bash
Authorization: Bearer <access_token>
```
### **🔹 Testing APIs from the UI**  
To test all APIs from the UI side, you can directly go to:  

```bash
http://127.0.0.1:8000/api/auth/
```
