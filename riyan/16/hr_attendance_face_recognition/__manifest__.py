# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    'name': 'Face Recognition Attendance System',
    'version': '16.0.0.0',
    'category': 'Human Resources',
    'summary': """
    Advanced AI-powered attendance tracking with facial recognition, liveness detection, and GPS location capture
    
    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    face recognition
    attendance
    biometric
    odoo hr
    contactless
    gps tracking
    kiosk
    ai
    employee management
    check-in/out
    time tracking
    remote workforce
    odoo integration
    Face Recognition Attendance System
    HR
    hr
    attendance
    hr attendance
    auto
    AI
    ai
    attendance
    employee attendance
    hr
    hrms
    time tracking
    check-in
    check-out
    time and attendance
    work hours
    workforce management
    shift management
    employee tracking
    employee presence
    face recognition
    facial recognition
    biometric
    ai
    artificial intelligence
    machine learning
    liveness detection
    face id
    image processing
    deep learning
    computer vision
    webcam attendance
    odoo attendance
    odoo hr
    hr module
    odoo biometric
    odoo face recognition
    hr attendance
    odoo integration
    odoo apps
    odoo hrms
    odoo check-in
    attendance module
    anti-spoofing
    proxy prevention
    secure attendance
    identity verification
    attendance fraud prevention
    employee validation
    authentication
    contactless
    touchless
    hygienic attendance
    no-touch system
    covid-safe attendance
    remote attendance
    gps attendance
    gps tracking
    remote check-in
    remote work
    field staff tracking
    geofencing
    location tracking
    kiosk mode
    facial kiosk
    attendance kiosk
    webcam
    camera check-in
    tablet attendance
    mobile attendance
    education
    healthcare
    factory
    retail
    construction
    school attendance
    hospital staff
    office staff
    automation
    efficiency
    productivity
    real-time
    instant sync
    odoo real-time
    instant check-in
    AI Attendance System
    Face Recognition Attendance
    Odoo Face Attendance
    Odoo Biometric Attendance
    Facial Recognition for Odoo HR
    AI Attendance System for Odoo
    Contactless Attendance Odoo
    Face Recognition Odoo Module
    Attendance Kiosk Odoo App
    Biometric HR Odoo Integration
    Odoo Face Detection Attendance
    Biometric Attendance System
    Facial Recognition HR System
    Odoo Attendance Integration
    Contactless Attendance System
    Face-Based Attendance Software
    GPS Attendance Tracking
    Employee Attendance with Face Recognition
    Liveness Detection Attendance System
    Workforce management software
    Biometric time tracking
    Employee time and attendance
    Automated HR solutions
    Face detection attendance
    Digital attendance logging
    Remote employee monitoring
    Time theft prevention system
    Attendance fraud prevention
    face recognition attendance Odoo
    Odoo facial recognition attendance
    Odoo attendance face recognition app
    contactless attendance Odoo module
    Odoo HR attendance face recognition
    AI face recognition attendance for Odoo
    Odoo kiosk attendance via face recognition
    face recognition attendance with Odoo HR
    secure face-based attendance Odoo module
    Odoo attendance face recognition plugin
        
    """,
    'description': """
Face Recognition Attendance System
==================================

Transform your employee attendance management with cutting-edge facial recognition technology. This comprehensive module provides secure, contactless, and automated attendance tracking that integrates seamlessly with Odoo's HR Attendance system.

🎯 **Key Highlights:**
- **AI-Powered Recognition**: Advanced facial recognition with 99%+ accuracy
- **Anti-Spoofing Security**: Built-in liveness detection prevents photo/video fraud
- **GPS Integration**: Automatic location capture and address resolution
- **Contactless Operation**: Hygienic, touchless attendance marking
- **Real-time Processing**: Instant check-in/check-out with immediate feedback
- **Seamless Integration**: Works perfectly with existing Odoo HR modules


    tus
    TUS
    TechUltra Solutions Private Limited
    techUltra solutions private limited
    face recognition
    attendance
    biometric
    odoo hr
    contactless
    gps tracking
    kiosk
    ai
    employee management
    check-in/out
    time tracking
    remote workforce
    odoo integration
    Face Recognition Attendance System
    HR
    hr
    attendance
    hr attendance
    auto
    AI
    ai
    attendance
    employee attendance
    hr
    hrms
    time tracking
    check-in
    check-out
    time and attendance
    work hours
    workforce management
    shift management
    employee tracking
    employee presence
    face recognition
    facial recognition
    biometric
    ai
    artificial intelligence
    machine learning
    liveness detection
    face id
    image processing
    deep learning
    computer vision
    webcam attendance
    odoo attendance
    odoo hr
    hr module
    odoo biometric
    odoo face recognition
    hr attendance
    odoo integration
    odoo apps
    odoo hrms
    odoo check-in
    attendance module
    anti-spoofing
    proxy prevention
    secure attendance
    identity verification
    attendance fraud prevention
    employee validation
    authentication
    contactless
    touchless
    hygienic attendance
    no-touch system
    covid-safe attendance
    remote attendance
    gps attendance
    gps tracking
    remote check-in
    remote work
    field staff tracking
    geofencing
    location tracking
    kiosk mode
    facial kiosk
    attendance kiosk
    webcam
    camera check-in
    tablet attendance
    mobile attendance
    education
    healthcare
    factory
    retail
    construction
    school attendance
    hospital staff
    office staff
    automation
    efficiency
    productivity
    real-time
    instant sync
    odoo real-time
    instant check-in
    AI Attendance System
    Face Recognition Attendance
    Odoo Face Attendance
    Odoo Biometric Attendance
    Facial Recognition for Odoo HR
    AI Attendance System for Odoo
    Contactless Attendance Odoo
    Face Recognition Odoo Module
    Attendance Kiosk Odoo App
    Biometric HR Odoo Integration
    Odoo Face Detection Attendance
    Biometric Attendance System
    Facial Recognition HR System
    Odoo Attendance Integration
    Contactless Attendance System
    Face-Based Attendance Software
    GPS Attendance Tracking
    Employee Attendance with Face Recognition
    Liveness Detection Attendance System
    Workforce management software
    Biometric time tracking
    Employee time and attendance
    Automated HR solutions
    Face detection attendance
    Digital attendance logging
    Remote employee monitoring
    Time theft prevention system
    Attendance fraud prevention
    face recognition attendance Odoo
    Odoo facial recognition attendance
    Odoo attendance face recognition app
    contactless attendance Odoo module
    Odoo HR attendance face recognition
    AI face recognition attendance for Odoo
    Odoo kiosk attendance via face recognition
    face recognition attendance with Odoo HR
    secure face-based attendance Odoo module
    Odoo attendance face recognition plugin
        

""",
    'author': 'TechUltra Solutions Private Limited',
    'license': 'OPL-1',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com",
    'depends': ['base', 'hr', 'hr_attendance', 'web', 'website'],
    'external_dependencies': {
        'python': ['face_recognition', 'numpy', 'Pillow', 'requests']
    },
    'data': [
        'views/face_recognition_templates.xml',
        'views/hr_attendance_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hr_attendance_face_recognition/static/src/js/webcam.js',
        ],
        'web.assets_frontend': [
            'hr_attendance_face_recognition/static/src/js/webcam.js',
            'hr_attendance_face_recognition/static/src/js/face_page.js',
        ],
    },
    'images': [
        'static/description/main_screen.gif'
    ],
    'currency': 'USD',
    'price': 24.64,
    'application': True,
    'installable': True,
    'auto_install': False,
}
