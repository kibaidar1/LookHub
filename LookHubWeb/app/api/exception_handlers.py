from fastapi import FastAPI, Request, HTTPException
from starlette import status

from app.application.exceptions import EntityNotFoundError, UnknownError, InvalidFileError


def init_exception_handlers(app: FastAPI):
    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found(request: Request, exc: EntityNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.args)

    @app.exception_handler(InvalidFileError)
    async def invalid_file(request: Request, exc: InvalidFileError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.args)

    @app.exception_handler(UnknownError)
    async def unknown_error(request: Request, exc: UnknownError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.args)
