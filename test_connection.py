import sys
sys.path.insert(0, '.')

try:
    print("🔄 Testing Firebase connection...")
    print("")
    
    from config import Config
    Config.validate()
    print("✅ Configuration validated")
    
    from firebase_service import FirebaseService
    firebase = FirebaseService()
    print("✅ Firebase Admin SDK initialized")
    
    db = firebase.db
    print(f"✅ Firestore connected: {db.project}")
    
    # Test write/read
    test_ref = db.collection('_test').document('connection_test')
    test_ref.set({'status': 'working', 'timestamp': 'test'})
    print("✅ Test write successful")
    
    doc = test_ref.get()
    if doc.exists:
        print("✅ Test read successful")
        test_ref.delete()
        print("✅ Test cleanup successful")
    
    print("")
    print("═══════════════════════════════════════════════")
    print("🎉 ALL TESTS PASSED - FIREBASE IS READY!")
    print("═══════════════════════════════════════════════")
    print("")
    print("Next steps:")
    print("  1. Run: ./start.sh")
    print("  2. Open: http://localhost:5000")
    print("  3. Follow GET_STARTED.md")
    
except Exception as e:
    print("")
    print("❌ CONNECTION FAILED")
    print(f"Error: {e}")
    print("")
    print("Troubleshooting:")
    print("  1. Check that Firestore is enabled:")
    print("     https://console.firebase.google.com/project/whatsapp-automation-a8d2d/firestore")
    print("  2. Verify your .env file has correct credentials")
    print("  3. Check service account has proper roles:")
    print("     - Cloud Datastore User")
    print("     - Firebase Admin SDK Administrator Service Agent")
    sys.exit(1)

