from fastapi import APIRouter, HTTPException

from schemas import DeleteDocumentRequest, DeleteDocumentResponse, IndexDocumentRequest, IndexDocumentResponse

from .service import delete_document_by_id, index_document


router = APIRouter()


@router.post("/index-document", response_model=IndexDocumentResponse)
def index_document_route(request: IndexDocumentRequest):
	try:
		total_chunks = index_document(
			style=request.style,
			document_id=request.document_id,
			document_path=request.document_path,
		)
	except FileNotFoundError as exc:
		raise HTTPException(status_code=404, detail=str(exc)) from exc
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc
	except Exception as exc:
		raise HTTPException(status_code=500, detail=str(exc)) from exc

	return IndexDocumentResponse(success=True, total_chunks=total_chunks)


@router.post("/delete-document", response_model=DeleteDocumentResponse)
def delete_document_route(request: DeleteDocumentRequest):
	try:
		deleted_chunks = delete_document_by_id(request.document_id)
	except Exception as exc:
		raise HTTPException(status_code=500, detail=str(exc)) from exc

	return DeleteDocumentResponse(success=deleted_chunks > 0, deleted_chunks=deleted_chunks)