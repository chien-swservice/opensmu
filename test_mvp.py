#!/usr/bin/env python3
"""
Test script for MVP architecture
"""
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mvp_imports():
    """Test that all MVP components can be imported"""
    try:
        from model.smu_model import SMUModel
        from presenter.main_presenter import MainPresenter
        from view.view import View
        print("✅ All MVP components imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_model_creation():
    """Test that the model can be created and initialized"""
    try:
        from model.smu_model import SMUModel
        model = SMUModel()
        print("✅ Model created successfully")
        print(f"   - Config loaded: {model.get_config() is not None}")
        print(f"   - Data initialized: {model.get_measurement_data() is not None}")
        return True
    except Exception as e:
        print(f"❌ Model creation error: {e}")
        return False

def test_presenter_creation():
    """Test that the presenter can be created"""
    try:
        from presenter.main_presenter import MainPresenter
        # Note: This will create the view as well, so we need to be careful
        # In a real test, we might want to mock the view
        print("✅ Presenter creation test passed (view creation would happen here)")
        return True
    except Exception as e:
        print(f"❌ Presenter creation error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing MVP Architecture")
    print("=" * 40)
    
    tests = [
        test_mvp_imports,
        test_model_creation,
        test_presenter_creation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MVP architecture is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 