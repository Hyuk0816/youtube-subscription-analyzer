#!/usr/bin/env python3
# youtube_subtitle_analyzer.py

import re
from typing import Optional, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
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
    5. 해당 추출된 자막을 기반으로 학습 자료를 아티팩트 형식으로 만듭니다.
    6. 아티팩트 형식은 다이어그램 인포그래픽 형식으로 만듭니다.

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
            - video_title (str): 영상의 제목 (가능한 경우)
            - subtitle_text (str): 추출된 자막 내용
            - subtitle_type (str): 자막 유형 (uploaded: 게시자 등록, auto: 자동 생성)
            - video_id (str): 유튜브 영상 ID
            - video_url (str): 원본 유튜브 URL
    """
    # 도우미 함수: YouTube URL에서 video_id 추출
    def extract_video_id(url: str) -> str:
        """YouTube URL에서 video_id를 추출합니다."""
        pattern = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        match = re.search(pattern, url)
        return match.group(1) if match else ""

    # 도우미 함수: 언어 코드 확장
    def expand_language_code(language: str) -> list:
        """언어 코드를 여러 가능한 변형으로 확장합니다."""
        language_variants = [language]
        
        # 언어별 확장 코드 추가
        if language == "ko":
            language_variants.extend(["ko-KR", "ko_KR", "kor"])
        elif language == "en":
            language_variants.extend(["en-US", "en-GB", "en_US", "en_GB", "eng"])
        elif language == "ja":
            language_variants.extend(["ja-JP", "ja_JP", "jpn"])
        elif language == "zh":
            language_variants.extend(["zh-CN", "zh-TW", "zh_CN", "zh_TW", "chi", "zho"])
            
        return language_variants

    try:
        # 1. YouTube URL에서 비디오 ID 추출
        video_id = extract_video_id(youtube_url)
        if not video_id:
            return {
                "video_title": "알 수 없음",
                "subtitle_text": "유효한 YouTube URL이 아닙니다.",
                "subtitle_type": "error",
                "video_id": "",
                "video_url": youtube_url
            }
        
        # 2. 확장된 언어 코드 가져오기
        language_variants = expand_language_code(language)
        
        # 3. 자막 목록 가져오기
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # 변수 초기화
        found_transcript = None
        subtitle_type = "none"
        video_title = "제목 없음"  # 이 라이브러리는 비디오 제목을 가져오지 않음
        
        # 4. 선호하는 언어의 자막 찾기 (업로드된 자막 우선)
        try:
            # 업로드된 자막 먼저 시도
            for lang in language_variants:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    if not transcript.is_generated:
                        found_transcript = transcript
                        subtitle_type = "uploaded"
                        print(f"업로드된 자막 찾음: {lang}")
                        break
                except:
                    continue
            
            # 업로드된 자막이 없으면 자동 생성 자막 시도
            if not found_transcript:
                for lang in language_variants:
                    try:
                        transcript = transcript_list.find_transcript([lang])
                        if transcript.is_generated:
                            found_transcript = transcript
                            subtitle_type = "auto"
                            print(f"자동 생성 자막 찾음: {lang}")
                            break
                    except:
                        continue
            
            # 원하는 언어의 자막을 찾지 못한 경우, 자동 번역 시도
            if not found_transcript and language != "en":
                try:
                    # 영어 자막을 가져와서 지정한 언어로 번역
                    transcript = transcript_list.find_transcript(['en'])
                    found_transcript = transcript.translate(language)
                    subtitle_type = "translated"
                    print(f"영어 자막을 {language}로 번역")
                except:
                    # 영어 자막도 없거나 번역 실패한 경우, 첫 번째 가능한 자막 사용
                    try:
                        first_transcript = list(transcript_list)[0]
                        found_transcript = first_transcript
                        subtitle_type = "auto" if first_transcript.is_generated else "uploaded"
                        print(f"대체 자막 사용: {first_transcript.language_code}")
                    except:
                        pass
            
        except Exception as e:
            print(f"자막 검색 중 오류: {str(e)}")
            
        # 5. 자막 추출
        if found_transcript:
            try:
                # 자막 데이터 가져오기
                transcript_data = found_transcript.fetch()
                
                # 자막 텍스트 결합 (시간 순서대로)
                if isinstance(transcript_data, list):
                    subtitle_lines = [entry.get('text', '') for entry in transcript_data if isinstance(entry, dict)]
                    subtitle_text = " ".join(subtitle_lines)
                else:
                    print(f"예상치 못한 자막 데이터 형식: {type(transcript_data)}")
                    # 직접 문자열 추출 시도
                    try:
                        # found_transcript의 fetch 메서드 사용
                        transcript_data = found_transcript.fetch()
                        subtitle_text = " ".join([entry.get('text', '') for entry in transcript_data])
                    except Exception as e:
                        print(f"직접 자막 추출 시도 중 오류: {str(e)}")
                        subtitle_text = f"자막 형식을 처리할 수 없습니다: {str(e)}"
                        subtitle_type = "error"
            except Exception as e:
                print(f"자막 데이터 처리 중 오류: {str(e)}")
                # 직접적인 방법으로 다시 시도
                try:
                    print("직접 자막 추출 시도 중...")
                    # 새로운 Transcript 객체 생성 및 fetch 사용
                    transcript = transcript_list.find_transcript([language])
                    transcript_data = transcript.fetch()
                    subtitle_text = " ".join([entry.get('text', '') for entry in transcript_data])
                    print(f"직접 추출 성공, 길이: {len(subtitle_text)} 자")
                except Exception as e2:
                    print(f"직접 추출 실패: {str(e2)}")
                    subtitle_text = f"자막 추출 중 오류 발생: {str(e)}, 직접 시도: {str(e2)}"
                    subtitle_type = "error"
        else:
            subtitle_text = f"이 영상에는 지정한 언어({language})의 자막이 없습니다."
            subtitle_type = "none"
            
        # 6. 결과 반환
        return {
            "video_title": video_title,
            "subtitle_text": subtitle_text,
            "subtitle_type": subtitle_type,
            "video_id": video_id,
            "video_url": youtube_url
        }
        
    except TranscriptsDisabled:
        return {
            "video_title": "알 수 없음",
            "subtitle_text": "이 영상은 자막이 비활성화되어 있습니다.",
            "subtitle_type": "error",
            "video_id": video_id,
            "video_url": youtube_url
        }
    except NoTranscriptFound:
        return {
            "video_title": "알 수 없음",
            "subtitle_text": f"이 영상에는 지정한 언어({language})의 자막이 없습니다.",
            "subtitle_type": "none",
            "video_id": video_id,
            "video_url": youtube_url
        }
    except Exception as e:
        return {
            "video_title": "알 수 없음",
            "subtitle_text": f"자막 추출 중 오류 발생: {str(e)}",
            "subtitle_type": "error",
            "video_id": video_id if video_id else "알 수 없음",
            "video_url": youtube_url
        }


if __name__ == "__main__":
    print("🚀 YouTube Subtitle Analyzer MCP Server 실행 중...")
    # FastMCP 서버 실행
    mcp.run()
