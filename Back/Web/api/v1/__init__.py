from fastapi import APIRouter

from . import auth, admin, users, plagiarism, grammar, similarity

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router, tags=["auth"])
router.include_router(admin.router, tags=["admin"]) 
router.include_router(users.router, tags=["users"])
router.include_router(plagiarism.router, tags=["plagiarism"])
router.include_router(grammar.router, tags=["grammar"])
router.include_router(similarity.router, prefix="/similarity", tags=["similarity"])
