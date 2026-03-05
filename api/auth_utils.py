import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, status, Header
import os

# Initialize Firebase Admin SDK
def init_firebase():
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        if project_id:
            os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
            os.environ["FIREBASE_PROJECT_ID"] = project_id
            
        print(f"DEBUG: Initializing Firebase with Project ID: {project_id}")
        
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'projectId': project_id
            } if project_id else {})
        elif project_id:
            # Initialize with just project ID (for public key verification)
            try:
                firebase_admin.initialize_app(options={
                    'projectId': project_id
                })
            except Exception as e:
                print(f"Firebase Init Error (options): {e}")
        else:
            try:
                firebase_admin.initialize_app()
            except Exception as e:
                print(f"Firebase Admin init failed: {e}. Ensure project ID is configured.")

# --- Authentication & Demo Mode ---

DEV_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
print(f"DEBUG: auth_utils.py -> DEV_MODE is {DEV_MODE}")

async def get_current_user(authorization: str = Header(None)):
    print(f"DEBUG: get_current_user called. DEV_MODE={DEV_MODE}, Auth={authorization}")
    if DEV_MODE:
        return {
            "uid": "dev-user-123",
            "email": "demo-analyst@giet.edu",
            "name": "Demo Analyst",
            "picture": "https://www.gstatic.com/images/branding/product/2x/avatar_anonymous_color_120dp.png"
        }
        
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token"
        )

    id_token = authorization.split("Bearer ")[1]

    try:
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(id_token)
        
        # Optional: Domain Restriction
        email = decoded_token.get("email", "")
        # Allowlist for testing
        ALLOWLIST = ["rajprasad8260@gmail.com"]
        
        if not email.endswith("@giet.edu") and email not in ALLOWLIST:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access restricted: GIET email required or not in allowlist"
            )
            
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication: {str(e)}"
        )
