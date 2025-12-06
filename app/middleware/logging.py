
import time
import logging
from fastapi import Request

# 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next):
    """
    요청/응답 요약 로그(메서드, 경로, 상태코드, 지연시간)
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    logger.info(
        f"request method={request.method} "
        f"path={request.url.path} "
        f"status_code={response.status_code} "
        f"process_time={process_time:.2f}ms"
    )
    
    return response
