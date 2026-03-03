# Smart Soil Mobile App Guide

Successfully generated the full Flutter code for your Smart Soil application!

## 📂 Project Structure
The code is located in: `mobile_app/`

- **lib/main.dart**: Entry point, providers, and routing.
- **lib/services/**: API, Firebase, Auth, and Gemini logic.
- **lib/screens/**: Login, Dashboard, Advisor, and Chat UI.
- **lib/widgets/**: Reusable components (SensorCard, Drawer).
- **pubspec.yaml**: Dependencies list.

## 🚀 How to Run

### 1. Prerequisites
Ensure you have Flutter installed:
```bash
flutter doctor
```

### 2. Initialize Project
Since I generated the files manually, you need to fetch the dependencies:
```bash
cd mobile_app
flutter pub get
```

### 3. Configure Firebase
You need to link this app to your Firebase project:
1.  Install FlutterFire CLI: `npm install -g firebase-tools`
2.  Run configuration:
    ```bash
y    ```
3.  Select your project (`smart-soil`) and platforms (Android/iOS).
4.  This will generate `lib/firebase_options.dart`.
5.  **Uncomment** the Firebase init lines in `lib/main.dart`:
    ```dart
    // import 'firebase_options.dart'; 
    // await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
    ```

### 4. Run the App
Connect your phone or start an emulator:
```bash
flutter run
```

## ⚙️ Configuration
- **FastAPI URL**: Default is `http://10.0.2.2:8000` (Android Emulator localhost). Change in `lib/services/api_service.dart` if testing on a real device.
- **Gemini API**: Add your key in `lib/services/gemini_service.dart`.
