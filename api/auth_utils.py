import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, status, Header
import os

# Initialize Firebase Admin SDK
def init_firebase():
    if not firebase_admin._apps:
        # Check if we have credentials in environment or a service account file
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback to default credentials (e.g., set via GOOGLE_APPLICATION_CREDENTIALS)
            try:
                firebase_admin.initialize_app()
            except Exception as e:
                print(f"Firebase Admin init failed: {e}. Ensure service account is configured.")

async def get_current_user(authorization: str = Header(None)):
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
        # if not email.endswith("@giet.edu"):
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access restricted: GIET email required"
        #     )
            
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication: {str(e)}"
        )
