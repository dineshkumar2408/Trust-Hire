# Trust-Hire

A modern, responsive web application for hiring and recruitment management with secure authentication and an intuitive dashboard.

## 🚀 Features

### 🔐 Authentication System
- Secure login with session management
- Password hashing using Werkzeug
- CORS support for frontend-backend communication
- Session-based authentication with proper logout

### 📊 Dashboard
- Real-time statistics display
- Interactive hiring metrics
- Recent activity feed
- Responsive design for all devices

### 🎨 Modern UI/UX
- Beautiful gradient backgrounds
- Smooth animations and transitions
- Mobile-first responsive design
- Clean, professional interface
- Font Awesome icons

## 🛠️ Technology Stack

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-Origin Resource Sharing
- **Werkzeug** - Password hashing and security

### Frontend
- **HTML5** - Modern semantic markup
- **CSS3** - Advanced styling with gradients and animations
- **JavaScript (ES6+)** - Modern JavaScript features
- **Font Awesome** - Icon library

## 📋 Demo Credentials

The application comes with pre-configured demo accounts:

- **Admin User:**
  - Email: `admin@trusthire.com`
  - Password: `admin123`

- **Regular User:**
  - Email: `user@trusthire.com`
  - Password: `user123`

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip3 (Python package installer)

### Installation & Running

1. **Clone or extract the project:**
   ```bash
   # If you have the zip file, it's already extracted
   cd trust-hire
   ```

2. **Run the application:**
   ```bash
   ./start.sh
   ```

   Or manually:
   ```bash
   # Install dependencies
   cd backend
   pip3 install -r requirements.txt
   
   # Start the backend server
   python3 app.py
   ```

3. **Access the application:**
   - Open `frontend/index.html` in your web browser
   - Or serve it through a local server for best experience

## 📁 Project Structure

```
trust-hire/
├── backend/
│   ├── app.py              # Flask application with API endpoints
│   └── requirements.txt    # Python dependencies
├── frontend/
│   └── index.html         # Complete frontend application
├── start.sh               # Quick start script
└── README.md             # Project documentation
```

## 🔌 API Endpoints

The backend provides the following REST API endpoints:

- `POST /api/login` - User authentication
- `POST /api/logout` - User logout
- `GET /api/profile` - Get user profile information
- `GET /api/dashboard-stats` - Get dashboard statistics

## 🎯 Dashboard Features

### Statistics Cards
- **Total Applications** - Number of job applications received
- **Pending Reviews** - Applications awaiting review
- **Scheduled Interviews** - Upcoming interview sessions
- **Hired Candidates** - Successfully hired candidates

### Activity Feed
- Real-time updates on hiring activities
- Categorized by activity type (application, interview, hire, review)
- Color-coded icons for easy identification
- Timestamps for each activity

## 🔒 Security Features

- Password hashing using industry-standard algorithms
- Session-based authentication
- CORS protection
- Input validation and sanitization
- Secure logout functionality

## 📱 Responsive Design

The application is fully responsive and works seamlessly on:
- Desktop computers
- Tablets
- Mobile phones
- Various screen sizes and orientations

## 🎨 Design Highlights

- **Modern gradient backgrounds** for visual appeal
- **Smooth hover effects** and transitions
- **Loading states** for better user feedback
- **Error handling** with user-friendly messages
- **Consistent color scheme** throughout the application

## 🚧 Development Notes

### Backend Architecture
- Uses in-memory storage for demo purposes
- Session management with Flask sessions
- RESTful API design principles
- Error handling with proper HTTP status codes

### Frontend Architecture
- Single-page application (SPA) design
- Client-side routing between login and dashboard
- Async/await for API calls
- Modern CSS features (Grid, Flexbox, Custom Properties)

## 🔧 Customization

### Adding New Users
Edit the `users_db` dictionary in `backend/app.py`:

```python
users_db = {
    "new@example.com": {
        "password": generate_password_hash("password123"),
        "name": "New User",
        "role": "user",
        "created_at": datetime.now().isoformat()
    }
}
```

### Modifying Dashboard Stats
Update the `get_dashboard_stats()` function in `backend/app.py` to connect to your actual data source.

### Styling Changes
Modify the CSS in `frontend/index.html` to customize the appearance.

## 🚀 Production Deployment

For production deployment, consider:

1. **Database Integration:** Replace in-memory storage with a proper database (PostgreSQL, MySQL, etc.)
2. **Environment Variables:** Use environment variables for sensitive configuration
3. **HTTPS:** Enable SSL/TLS encryption
4. **Authentication:** Implement JWT tokens or OAuth
5. **Logging:** Add comprehensive logging
6. **Testing:** Add unit and integration tests

## 📄 License

This project is available for educational and demonstration purposes.

## 🤝 Contributing

This is a demo project, but feel free to fork and enhance it for your own use cases!

---

**Built with ❤️ for modern hiring solutions**