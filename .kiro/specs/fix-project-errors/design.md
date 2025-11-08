# Design Document

## Overview

This design document outlines the approach to fix all errors in the Disease Prediction Django project and make it runnable on modern Python versions. The project uses Django 3.0.3 with outdated dependencies that are incompatible with Python 3.13.6. The solution involves updating dependencies, fixing database configuration, resolving model compatibility issues, and ensuring the machine learning model loads correctly.

## Architecture

### Current State Analysis

The project has the following structure:
- **Django Framework**: Version 3.0.3 (released in 2020, no longer supported)
- **Python Version**: 3.13.6 (released in 2024)
- **Database**: PostgreSQL with hardcoded credentials
- **ML Framework**: scikit-learn 0.21.3 (incompatible with Python 3.13)
- **Apps**: main_app, accounts, chats

### Target State

- **Django Framework**: Version 4.2 LTS (long-term support until April 2026)
- **Python Version**: 3.13.6 (maintained)
- **Database**: SQLite (default) with PostgreSQL as optional
- **ML Framework**: scikit-learn 1.7.2 (compatible with Python 3.13)
- **Apps**: All existing apps with updated models

## Components and Interfaces

### 1. Dependency Management

**Component**: requirements.txt

**Changes Required**:
- Update Django from 3.0.3 to 4.2.x (LTS version)
- Update scikit-learn from 0.21.3 to 1.7.x
- Update joblib from 0.14.1 to 1.5.x
- Replace psycopg2 with psycopg2-binary 2.9.x
- Add pillow for image handling (if not present)

**Rationale**: Django 3.0.3 reached end-of-life and has security vulnerabilities. Python 3.13 requires updated versions of all packages. Django 4.2 is the current LTS version with support until 2026.

### 2. Database Configuration

**Component**: disease_prediction/settings.py

**Current Configuration**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'predico',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost'
    }
}
```

**New Configuration**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Optional PostgreSQL configuration (commented out)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'predico',
#         'USER': 'postgres',
#         'PASSWORD': '1234',
#         'HOST': 'localhost'
#     }
# }
```

**Rationale**: SQLite requires no external setup and is perfect for development. Users can easily switch to PostgreSQL if needed. This removes the barrier of requiring PostgreSQL installation.

### 3. Model Compatibility Fixes

**Component**: main_app/models.py

**Issues Identified**:
1. ArrayField usage (PostgreSQL-specific) will fail with SQLite
2. All models appear compatible with Django 4.2

**Solution**:
- Replace ArrayField with JSONField for SQLite compatibility
- JSONField is supported by both SQLite and PostgreSQL in Django 4.2
- Update the diseaseinfo model to use JSONField instead of ArrayField

**Before**:
```python
from django.contrib.postgres.fields import ArrayField
symptomsname = ArrayField(models.CharField(max_length=200))
```

**After**:
```python
symptomsname = models.JSONField(default=list)
```

**Rationale**: JSONField is database-agnostic and works with both SQLite and PostgreSQL. It can store lists just like ArrayField but with broader compatibility.

### 4. Machine Learning Model Handling

**Component**: main_app/views.py (model loading)

**Current Implementation**:
```python
import joblib as jb
model = jb.load('trained_model')
```

**Issues**:
- Model loads at module level (fails if file missing)
- No error handling
- Model trained with scikit-learn 0.21.3 may be incompatible with 1.7.x

**Solution**:
- Add try-except block for model loading
- Provide clear error message if model is missing or incompatible
- Load model lazily or with fallback

**New Implementation**:
```python
import joblib as jb
import os

model = None
model_path = 'trained_model'

try:
    if os.path.exists(model_path):
        model = jb.load(model_path)
        print("ML model loaded successfully")
    else:
        print(f"Warning: Model file '{model_path}' not found. Disease prediction will not work.")
except Exception as e:
    print(f"Error loading model: {e}")
    print("The model may be incompatible with the current scikit-learn version.")
```

**Rationale**: Graceful error handling prevents the entire application from crashing if the model file is missing or incompatible. The application can still run for other features.

### 5. Django 4.2 Compatibility Updates

**Components**: All settings and configurations

**Changes Required**:

1. **DEFAULT_AUTO_FIELD**: Add to settings.py
```python
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

2. **CSRF_TRUSTED_ORIGINS**: Add for Django 4.0+ (if using HTTPS)
```python
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']
```

3. **Path imports**: Update BASE_DIR to use pathlib
```python
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
```

**Rationale**: Django 4.2 has new defaults and requirements. These changes ensure compatibility and prevent deprecation warnings.

## Data Models

### Affected Models

1. **diseaseinfo model** (main_app/models.py)
   - Change: ArrayField → JSONField
   - Impact: Requires new migration
   - Data preservation: Existing data structure remains compatible

2. **All other models**
   - No structural changes required
   - Compatible with Django 4.2

### Migration Strategy

1. Create new migrations after model changes
2. Migrations will be database-agnostic (work with both SQLite and PostgreSQL)
3. Fresh database setup (no existing data to migrate)

## Error Handling

### 1. Model Loading Errors

**Error Type**: Model file missing or incompatible

**Handling**:
- Wrap model loading in try-except
- Log clear error message
- Allow application to start without model
- Display user-friendly error in disease prediction view

### 2. Database Errors

**Error Type**: Database connection failures

**Handling**:
- SQLite: Automatic creation, no connection errors
- PostgreSQL: Clear error messages if credentials are wrong
- Provide instructions in error message

### 3. Migration Errors

**Error Type**: Migration conflicts or failures

**Handling**:
- Delete existing migrations (fresh start)
- Run makemigrations to create new ones
- Apply migrations with clear error reporting

### 4. Dependency Installation Errors

**Error Type**: Package installation failures

**Handling**:
- Use compatible version ranges in requirements.txt
- Provide fallback versions if latest fails
- Document known issues with specific Python versions

## Testing Strategy

### 1. Dependency Installation Test

**Test**: Install all dependencies from requirements.txt
```bash
pip install -r requirements.txt
```

**Expected Result**: All packages install without errors

### 2. Migration Test

**Test**: Create and apply migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

**Expected Result**: All migrations apply successfully, database created

### 3. Server Start Test

**Test**: Start development server
```bash
python manage.py runserver
```

**Expected Result**: Server starts without errors, accessible at http://127.0.0.1:8000/

### 4. Model Loading Test

**Test**: Check model loading in views
- Access disease prediction page
- Verify model loads or shows appropriate error

**Expected Result**: Either model loads successfully or clear error message displayed

### 5. Basic Functionality Test

**Test**: Navigate through main pages
- Home page
- Sign up pages (patient/doctor)
- Sign in pages

**Expected Result**: All pages render without template or view errors

### 6. Database Operations Test

**Test**: Create a test user account
- Sign up as patient
- Verify data saves to database
- Sign in with created account

**Expected Result**: User creation and authentication work correctly

## Implementation Phases

### Phase 1: Dependency Updates
1. Update requirements.txt with compatible versions
2. Install dependencies
3. Verify installation success

### Phase 2: Settings Configuration
1. Update settings.py for Django 4.2
2. Change database to SQLite
3. Add new required settings

### Phase 3: Model Fixes
1. Update diseaseinfo model (ArrayField → JSONField)
2. Remove PostgreSQL-specific imports
3. Create new migrations

### Phase 4: Model Loading Fix
1. Add error handling to model loading
2. Test with and without model file
3. Verify graceful degradation

### Phase 5: Database Setup
1. Delete old migrations (if any conflicts)
2. Run makemigrations
3. Run migrate
4. Verify database creation

### Phase 6: Testing and Validation
1. Start development server
2. Test all major pages
3. Verify no errors in console
4. Document any remaining issues

## Rollback Strategy

If issues occur:
1. Keep backup of original requirements.txt
2. Use git to revert changes if needed
3. Document any incompatibilities discovered
4. Provide alternative solutions

## Future Considerations

1. **Model Retraining**: The ML model may need retraining with scikit-learn 1.7.x
2. **Security**: Update SECRET_KEY and remove from version control
3. **Environment Variables**: Move sensitive settings to environment variables
4. **Production Setup**: Configure for production deployment (DEBUG=False, ALLOWED_HOSTS, etc.)
5. **Testing**: Add automated tests for critical functionality
6. **Documentation**: Update README with new setup instructions
