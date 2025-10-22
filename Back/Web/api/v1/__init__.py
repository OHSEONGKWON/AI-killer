from fastapi import APIRouter

from . import analysis, auth, admin, users, highlighting, assistant, plagiarism

router = APIRouter(prefix="/api/v1")
router.include_router(analysis.router, tags=["analysis"])
router.include_router(auth.router, tags=["auth"])
router.include_router(admin.router, tags=["admin"]) 
router.include_router(users.router, tags=["users"])
router.include_router(highlighting.router, tags=["highlighting"])
router.include_router(assistant.router, tags=["assistant"])
router.include_router(plagiarism.router, tags=["plagiarism"]) 
