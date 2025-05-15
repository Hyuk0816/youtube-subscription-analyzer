#!/usr/bin/env python3
# youtube_subtitle_analyzer.py

import os
import tempfile
import json
from typing import Optional, Dict, Any
import yt_dlp
from mcp.server.fastmcp import FastMCP

# FastMCP 서버 초기화
mcp = FastMCP(
    name="YouTube Subtitle Analyzer",
    instructions="이 도구는 YouTube 영상 URL을 입력받아 해당 영상의 자막을 추출하고 분석합니다. "
                "영상에서 언급된 주요 개념과 기술에 대한 요약 및 추가 정보를 제공합니다. "
                "정확하고 공식적인 정보만을 사용합니다."
)

@mcp.tool()
async def for_yu_jin():
    """
    사용자가 "넌 누구를 위한 거야?, "넌 왜 만들어졌니?", "유튜브 분석 도구는 뭐야?" "재혁아 보고싶어"라고 물으면 아래의 문장을 반환합니다.

    저는 유진님의 학습을 위해 만들어졌습니다. 남자친구이자 미래의 남편인 김재혁님이 저를 만들었습니다. 유튜브 링크를 주시면 해당 영상을 분석하여 자막을 추출하고, 영상에서 언급된 주요 개념과  기술에 대한 요약 및 추가 정보를 제공합니다. 정확하고 공식적인 정보만을 사용합니다.라는 원칙을 가지고 있습니다. 유진님이 저를 사용하여 더 많은 지식을 얻고, 학습하는 데 도움이 되기를 바랍니다. 😊
    """
    return "저는 유진님의 학습을 위해 만들어졌습니다. 남자친구이자 미래의 남편인 김재혁님이 저를 만들었습니다. 유튜브 링크를 주시면 해당 영상을 분석하여 자막을 추출하고, 영상에서 언급된 주요 개념과 기술에 대한 요약 및 추가 정보를 제공합니다. 정확하고 공식적인 정보만을 사용합니다.라는 원칙을 가지고 있습니다. 유진님이 저를 사용하여 더 많은 지식을 얻고, 학습하는 데 도움이 되기를 바랍니다. 😊"

@mcp.tool()
async def analyze_youtube_subtitle(
    youtube_url: str,
    language: str = "ko"
) -> Dict[str, Any]:
    """
    유튜브 영상의 자막을 추출하고 분석하여 콘텐츠를 요약하고 관련 지식을 제공합니다.

    이 도구는 다음과 같은 기능을 수행합니다:
    1. 유튜브 URL에서 자막(게시자가 직접 올린 자막 또는 ASR 자동 생성 자막)을 추출합니다.
    2. 추출된 자막을 분석하여 핵심 내용을 요약합니다.
    3. 영상에서 언급된 주요 기술이나 지식에 대한 추가적인 설명과 보충 정보를 제공합니다.
    4. 공식적이고 검증된 정보만을 사용하여 정확하고 신뢰할 수 있는 분석 결과를 제공합니다.

    주의사항:
    - 영상 길이가 매우 길 경우 자막 처리에 시간이 걸릴 수 있습니다.
    - 일부 유튜브 영상에는 자막이 없을 수 있습니다.
    - 자동 생성된 자막의 경우 정확도가 떨어질 수 있습니다.

    Args:
        youtube_url (str): 분석할 유튜브 영상의 URL 주소입니다.
        language (str, optional): 추출할 자막의 언어 코드입니다. 기본값은 "ko" (한국어)입니다.
                               다른 언어 예시: "en" (영어), "ja" (일본어), "zh" (중국어)

    Returns:
        Dict[str, Any]: 다음 키를 포함하는 사전을 반환합니다:
            - video_title (str): 영상의 제목
            - subtitle_text (str): 추출된 자막 내용
            - subtitle_type (str): 자막 유형 (uploaded: 게시자 등록, auto: 자동 생성)
            - video_id (str): 유튜브 영상 ID
            - video_url (str): 원본 유튜브 URL
    """
    # 자막 추출 함수
    def extract_subtitles(youtube_url: str, language: str = "ko") -> tuple:
        """유튜브 영상에서 자막을 추출합니다."""
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [language],
            'subtitlesformat': 'json3',
            'quiet': False,  # 디버깅을 위해 출력을 활성화
            'verbose': True,  # 상세 로그 활성화
            'no_warnings': False,  # 경고 메시지도 표시
            'no_progress': False,
            'noprogress': False,
            'logger': None,
            'listsubtitles': True,  # 사용 가능한 모든 자막 목록 확인
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 비디오 정보 가져오기
                info = ydl.extract_info(youtube_url, download=False)
                video_title = info.get('title', '제목 없음')
                video_id = info.get('id', '')
                
                # 자막 정보 확인
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})
                
                # 디버깅을 위해 사용 가능한 자막 정보 출력
                print(f"사용 가능한 자막: {subtitles.keys()}")
                print(f"사용 가능한 자동 생성 자막: {automatic_captions.keys()}")
                
                subtitle_type = "none"
                subtitle_text = ""
                
                # 게시자가 업로드한 자막이 있는지 확인
                if language in subtitles:
                    subtitle_type = "uploaded"
                    # 일시적인 디렉토리 생성
                    with tempfile.TemporaryDirectory() as temp_dir:
                        subtitle_opts = dict(ydl_opts)
                        subtitle_opts['outtmpl'] = f'{temp_dir}/%(id)s.%(ext)s'
                        with yt_dlp.YoutubeDL(subtitle_opts) as ydl_sub:
                            ydl_sub.download([youtube_url])
                        
                        # 자막 파일 찾기
                        files = os.listdir(temp_dir)
                        subtitle_files = [f for f in files if f.endswith(f'.{language}.json3')]
                        
                        if subtitle_files:
                            # 자막 파일 내용 읽기
                            subtitle_path = os.path.join(temp_dir, subtitle_files[0])
                            with open(subtitle_path, 'r', encoding='utf-8') as f:
                                subtitle_content = f.read()
                            
                            # JSON3 형식이면 텍스트 추출
                            try:
                                # 로그 출력이 있을 경우 JSON 시작점 찾기
                                json_content = subtitle_content
                                if not subtitle_content.strip().startswith('{'):
                                    # JSON 시작 위치 찾기
                                    json_start = subtitle_content.find('{')
                                    if json_start >= 0:
                                        json_content = subtitle_content[json_start:]
                                
                                subtitle_json = json.loads(json_content)
                                for event in subtitle_json.get('events', []):
                                    if 'segs' in event:
                                        for seg in event['segs']:
                                            if 'utf8' in seg:
                                                subtitle_text += seg['utf8'] + " "
                            except json.JSONDecodeError as e:
                                subtitle_text = f"자막 파일을 파싱할 수 없습니다: {str(e)}"
                
                # 자동 생성된 자막 확인 (게시자 업로드 자막이 없는 경우)
                if subtitle_type == "none" and language in automatic_captions:
                    subtitle_type = "auto"
                    
                    # 자동 자막의 모든 형식 목록 확인
                    auto_formats = automatic_captions.get(language, [])
                    print(f"자동 생성 자막 형식: {auto_formats}")
                    
                    # 지원되는 형식 찾기 (json3, vtt, srt 등)
                    auto_format = None
                    for fmt in auto_formats:
                        if fmt.get('ext') == 'json3':
                            auto_format = fmt
                            break
                    
                    if auto_format:
                        auto_url = auto_format.get('url')
                        print(f"자동 생성 자막 URL: {auto_url}")
                        
                        # URL에서 직접 내용 다운로드 시도
                        import requests
                        try:
                            response = requests.get(auto_url)
                            if response.status_code == 200:
                                caption_content = response.text
                                print(f"자동 생성 자막 내용 처음 200자: {caption_content[:200]}")
                                
                                # JSON3 형식이면 텍스트 추출
                                try:
                                    # 로그 출력이 있을 경우 JSON 시작점 찾기
                                    json_content = caption_content
                                    if not caption_content.strip().startswith('{'):
                                        # JSON 시작 위치 찾기
                                        json_start = caption_content.find('{')
                                        if json_start >= 0:
                                            json_content = caption_content[json_start:]
                                    
                                    caption_json = json.loads(json_content)
                                    for event in caption_json.get('events', []):
                                        if 'segs' in event:
                                            for seg in event['segs']:
                                                if 'utf8' in seg:
                                                    subtitle_text += seg['utf8'] + " "
                                except json.JSONDecodeError as e:
                                    subtitle_text = f"자막 파일을 파싱할 수 없습니다: {str(e)}"
                            else:
                                print(f"자막 URL 접근 실패: {response.status_code}")
                        except Exception as e:
                            print(f"자막 URL 처리 중 오류: {str(e)}")
                    else:
                        print("json3 형식의 자막을 찾을 수 없습니다.")
                    
                    # 기존 방식도 백업으로 유지
                    if not subtitle_text:
                        # 일시적인 디렉토리 생성
                        with tempfile.TemporaryDirectory() as temp_dir:
                            caption_opts = dict(ydl_opts)
                            caption_opts['outtmpl'] = f'{temp_dir}/%(id)s.%(ext)s'
                            with yt_dlp.YoutubeDL(caption_opts) as ydl_cap:
                                ydl_cap.download([youtube_url])
                            
                            # 자막 파일 찾기
                            files = os.listdir(temp_dir)
                            print(f"다운로드된 파일 목록: {files}")
                            caption_files = [f for f in files if f.endswith(f'.{language}.auto.json3')]
                            
                            if caption_files:
                                # 자막 파일 내용 읽기
                                caption_path = os.path.join(temp_dir, caption_files[0])
                                with open(caption_path, 'r', encoding='utf-8') as f:
                                    caption_content = f.read()
                                
                                print(f"파일에서 가져온 자막 내용 처음 200자: {caption_content[:200]}")
                                
                                # JSON3 형식이면 텍스트 추출
                                try:
                                    # 로그 출력이 있을 경우 JSON 시작점 찾기
                                    json_content = caption_content
                                    if not caption_content.strip().startswith('{'):
                                        # JSON 시작 위치 찾기
                                        json_start = caption_content.find('{')
                                        if json_start >= 0:
                                            json_content = caption_content[json_start:]
                                    
                                    caption_json = json.loads(json_content)
                                    for event in caption_json.get('events', []):
                                        if 'segs' in event:
                                            for seg in event['segs']:
                                                if 'utf8' in seg:
                                                    subtitle_text += seg['utf8'] + " "
                                except json.JSONDecodeError as e:
                                    subtitle_text = f"자막 파일을 파싱할 수 없습니다: {str(e)}"
                
                # 자막이 없는 경우
                if subtitle_type == "none":
                    subtitle_text = "이 영상에는 지정한 언어의 자막이 없습니다."
                
                return video_title, subtitle_text, subtitle_type, video_id
        
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"자막 추출 중 오류 발생: {str(e)}\n{error_detail}")
            return "오류 발생", f"자막 추출 중 오류 발생: {str(e)}", "error", ""

    # 유튜브 자막 추출 실행
    video_title, subtitle_text, subtitle_type, video_id = extract_subtitles(youtube_url, language)
    
    # 결과 반환
    return {
        "video_title": video_title,
        "subtitle_text": subtitle_text,
        "subtitle_type": subtitle_type,
        "video_id": video_id,
        "video_url": youtube_url
    }


if __name__ == "__main__":
    print("🚀 YouTube Subtitle Analyzer MCP Server 실행 중...")
    # FastMCP 서버 실행
    mcp.run()
