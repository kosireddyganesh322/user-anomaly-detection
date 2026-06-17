from fastapi import APIRouter

router = APIRouter()

@router.post("/run")
def run_predictions():
    # TODO: trigger Isolation Forest prediction pipeline
    return {"status": "queued"}

@router.get("/results")
def get_results():
    # TODO: return latest prediction results
    return {"results": []}
