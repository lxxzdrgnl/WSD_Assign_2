"""
Rate Limiter Configuration
API 요청 횟수 제한 설정 (slowapi)
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Limiter 인스턴스 생성
# key_func는 클라이언트의 IP 주소를 사용하여 요청을 식별합니다.
limiter = Limiter(key_func=get_remote_address)
