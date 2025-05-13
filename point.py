# Streamlit 기반 분리수거 챗봇 + 실시간 배터리 감지 포인트 적립
import streamlit as st
import pandas as pd
import re
import webbrowser
from difflib import get_close_matches
import folium
from streamlit_folium import folium_static
from charset_normalizer import from_path
import requests
import cv2
from ultralytics import YOLO

# 포인트 시스템 초기화
if 'points' not in st.session_state:
    st.session_state.points = 0

# 포인트 추가 함수
def add_points(pts):
    st.session_state.points += pts

# 주소를 좌표로 변환하는 함수 (Kakao API 사용)
# 주소를 좌표로 변환하는 함수 (Kakao API 사용) - 오류 수정
def geocode_address(address):
    try:
        # 주소가 문자열이 아닐 경우 문자열로 변환
        if not isinstance(address, str):
            address = str(address)
            
        if not address or len(address.strip()) < 2:
            return 37.566, 126.978  # 기본값 (서울시청)
            
        url = f"https://dapi.kakao.com/v2/local/search/address.json?query={address}"
        headers = {"Authorization": "KakaoAK cc4d9a2b17f6e35cace2da0660061ec8"}  # API 키 앞에 KakaoAK 추가
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("documents") and len(data["documents"]) > 0:
                x = float(data["documents"][0]["x"])  # 경도
                y = float(data["documents"][0]["y"])  # 위도
                return y, x
            else:
                # 주소 검색 실패 시 키워드 검색 시도
                keyword_url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={address}"
                keyword_response = requests.get(keyword_url, headers=headers)
                if keyword_response.status_code == 200:
                    keyword_data = keyword_response.json()
                    if keyword_data.get("documents") and len(keyword_data["documents"]) > 0:
                        x = float(keyword_data["documents"][0]["x"])
                        y = float(keyword_data["documents"][0]["y"])
                        return y, x
    except Exception as e:
        print(f"지오코딩 오류: {e}")
    
    # 기본 좌표 반환 (서울시청)
    return 37.566, 126.978

def validate_coordinates(lat, lon):
    return 33.0 <= lat <= 43.0 and 124.0 <= lon <= 132.0

def auto_read_csv(path):
    detection = from_path(path).best()
    return pd.read_csv(path, encoding=detection.encoding)

battery_df = auto_read_csv("battery_bins.csv")
waste_df = auto_read_csv("waste_fees.csv")
battery_df.columns = battery_df.columns.str.strip()
waste_df.columns = waste_df.columns.str.strip()

all_items = waste_df["품목"].dropna().unique().tolist()

def extract_keywords(text):
    region_match = re.search(r"([가-힣]+구)", text)
    matched_item = None
    for item in all_items:
        if item in text:
            matched_item = item
            break
    if not matched_item:
        words = re.findall(r"[가-힣0-9]+", text)
        guess = get_close_matches(words[-1], all_items, n=1, cutoff=0.7)
        matched_item = guess[0] if guess else None
    return region_match.group(1) if region_match else None, matched_item

# 가장 가까운 수거함 찾는 함수 - 개선 버전
# 가장 가까운 수거함 찾는 함수 - 버그 수정
# 가장 가까운 수거함 찾는 함수 - 버그 수정
def find_nearest_bin(address, bin_type=""):
    try:
        # 주소 유효성 검사
        if not address:
            return False, "주소를 입력해주세요.", None
            
        # 주소에서 좌표 변환
        user_lat, user_lon = geocode_address(address)
        user_coords_valid = validate_coordinates(user_lat, user_lon)
        
        if not user_coords_valid:
            return False, f"'{address}'의 좌표를 찾을 수 없습니다.", None
        
        # 주소 키워드 추출 (구/동 정보)
        address_keywords = re.findall(r'([가-힣]+)(구|동|시|군|읍|면|로)', address)
        
        # 데이터프레임에서 검색
        clean_addr = re.sub(r'\s+', '', address)  # 공백 제거
        regions = battery_df['지역'].fillna('').apply(lambda x: re.sub(r'\s+', '', str(x)))  # 문자열 변환 추가
        
        # 1. 정확한 매칭 시도
        exact_matches = battery_df[regions.str.contains(clean_addr, case=False, na=False)]
        
        # 2. 정확한 매칭이 없으면 유사 매칭 시도
        if exact_matches.empty:
            try:
                regions_list = regions.tolist()
                if regions_list:  # 빈 리스트 체크 추가
                    best_matches = get_close_matches(clean_addr, regions_list, n=1, cutoff=0.4)
                    if best_matches and len(best_matches) > 0:  # 결과 확인
                        best_match = best_matches[0]
                        exact_matches = battery_df[regions == best_match]
            except Exception as e:
                print(f"유사 매칭 오류: {e}")
        
        # 3. 유사 매칭도 없으면 키워드 기반 매칭 시도
        if exact_matches.empty and address_keywords:
            for base, suffix in address_keywords:
                keyword = base + suffix
                keyword_matches = battery_df[battery_df['지역'].str.contains(keyword, case=False, na=False)]
                if not keyword_matches.empty:
                    exact_matches = keyword_matches
                    break
        
        # 4. 키워드도 실패하면 동/구/로 만 추출하여 재시도
        if exact_matches.empty:
            # 동/구/로 등의 행정구역 추출
            location_match = re.search(r'([가-힣]+(?:동|구|로|시|군|읍|면))', address)
            if location_match:
                location = location_match.group(1)
                location_matches = battery_df[battery_df['지역'].str.contains(location, case=False, na=False)]
                if not location_matches.empty:
                    exact_matches = location_matches
        
        # 매칭 결과가 있으면 처리
        if not exact_matches.empty:
            # 가장 가까운 위치 찾기 (좌표 기반)
            nearest_idx = None
            min_distance = float('inf')
            
            for idx, row in exact_matches.iterrows():
                try:
                    # 좌표값 처리 개선
                    try:
                        bin_lat = float(row.get('위도', 0))
                        bin_lon = float(row.get('경도', 0))
                    except (ValueError, TypeError):
                        bin_lat, bin_lon = 0, 0
                    
                    # 좌표가 없거나 유효하지 않은 경우 주소로 변환
                    if not validate_coordinates(bin_lat, bin_lon):
                        bin_address = row.get('지번주소', '') or row.get('도로명주소', '') or row.get('지역', '')
                        if bin_address:
                            bin_lat, bin_lon = geocode_address(bin_address)
                    
                    # 거리 계산 (단순 좌표 차이)
                    if validate_coordinates(bin_lat, bin_lon):
                        distance = ((bin_lat - user_lat) ** 2 + (bin_lon - user_lon) ** 2) ** 0.5
                        if distance < min_distance:
                            min_distance = distance
                            nearest_idx = idx
                except Exception as e:
                    print(f"좌표 계산 오류 (행 {idx}): {e}")
                    continue
            
            # 가장 가까운 수거함 정보 추출
            if nearest_idx is not None:
                nearest_bin = exact_matches.loc[nearest_idx]
                location_name = nearest_bin.get('위치명', '수거함')
                bin_region = nearest_bin.get('지역', '')
                bin_address = nearest_bin.get('지번주소', '') or nearest_bin.get('도로명주소', '') or bin_region
                
                # 좌표 확인
                bin_lat, bin_lon = None, None
                try:
                    bin_lat = float(nearest_bin.get('위도', 0))
                    bin_lon = float(nearest_bin.get('경도', 0))
                    
                    if not validate_coordinates(bin_lat, bin_lon):
                        bin_lat, bin_lon = geocode_address(bin_address)
                except (ValueError, TypeError):
                    bin_lat, bin_lon = geocode_address(bin_address)
                
                # 지도 생성
                m = folium.Map(location=[bin_lat, bin_lon], zoom_start=15)
                folium.Marker(
                    [bin_lat, bin_lon], 
                    tooltip=location_name,
                    popup=f"{location_name}<br>{bin_address}",
                    icon=folium.Icon(color='red', icon='trash', prefix='fa')
                ).add_to(m)
                
                # 사용자 위치가 수거함과 충분히 떨어져 있으면 사용자 위치도 표시
                if abs(user_lat - bin_lat) > 0.001 or abs(user_lon - bin_lon) > 0.001:
                    folium.Marker(
                        [user_lat, user_lon],
                        tooltip=f"입력 주소: {address}",
                        popup=f"입력하신 주소: {address}",
                        icon=folium.Icon(color='blue', icon='home', prefix='fa')
                    ).add_to(m)
                    folium.PolyLine(
                        locations=[[bin_lat, bin_lon], [user_lat, user_lon]],
                        color='gray', weight=2, opacity=0.7, dash_array='5'
                    ).add_to(m)
                    
                    # 지도 영역 조정
                    bounds = [[min(bin_lat, user_lat), min(bin_lon, user_lon)], 
                             [max(bin_lat, user_lat), max(bin_lon, user_lon)]]
                    m.fit_bounds(bounds)
                
                # 결과 반환
                bin_type_str = f"{bin_type} " if bin_type else ""
                response = f"📍 가장 가까운 {bin_type_str}수거함:\n- 위치: {location_name}\n- 지역: {bin_region}\n- 주소: {bin_address}\n- 좌표: ({bin_lat:.6f}, {bin_lon:.6f})"
                return True, response, m
        
        # 매칭 결과가 없으면
        m = folium.Map(location=[user_lat, user_lon], zoom_start=15)
        folium.Marker(
            [user_lat, user_lon],
            tooltip=f"입력 주소: {address}",
            popup=f"입력하신 주소: {address}",
            icon=folium.Icon(color='blue', icon='home', prefix='fa')
        ).add_to(m)
        
        return False, f"❌ '{address}' 근처에서 수거함을 찾을 수 없습니다. 다른 주소를 입력해보세요.", m
        
    except Exception as e:
        import traceback
        print(f"수거함 검색 오류: {e}")
        traceback.print_exc()  # 스택 트레이스 출력
        return False, f"❌ 검색 중 오류가 발생했습니다: {str(e)}", None
def generate_response(user_input):
    try:
        # 건전지/형광등 수거함 검색 패턴 - 개선된 버전
        bin_search_patterns = [
            r"([가-힣0-9\-\s]+)(?:에서|근처|주변|가까운)?\s*(폐건전지|폐형광등|건전지|형광등)?\s*수거함",
            r"(폐건전지|폐형광등|건전지|형광등)?\s*수거함\s*(?:위치|어디|찾기|검색)?\s*([가-힣0-9\-\s]+)"
        ]
        
        # 수거함 검색 패턴 확인
        for pattern in bin_search_patterns:
            bin_match = re.search(pattern, user_input)
            if bin_match:
                groups = bin_match.groups()
                bin_type = None
                address = None
                
                # 패턴에 따라 그룹 할당 방식이 다름
                if bin_match.re.pattern == bin_search_patterns[0]:  # 첫 번째 패턴: 주소 먼저
                    address = groups[0].strip() if groups[0] else None
                    bin_type = groups[1] if groups[1] else "수거함"
                else:  # 두 번째 패턴: 수거함 종류 먼저
                    bin_type = groups[0] if groups[0] else "수거함"
                    address = groups[1].strip() if groups[1] else None
                
                # 주소가 있으면 처리
                if address:
                    success, response_text, map_obj = find_nearest_bin(address, bin_type)
                    return response_text, map_obj
        
        # 감지 없이 포인트 적립되지 않도록 변경
        if any(keyword in user_input for keyword in ['건전지', 'battery', 'item']):
            return (
                "🔍 건전지 관련 질문입니다. 실시간 감지 기능을 이용해 포인트를 적립해보세요!"
                f"\n현재 포인트: {st.session_state.points}점"
            ), None

        recyclable_keywords = ["플라스틱", "캔", "페트병", "종이", "비닐", "금속", "철", "페트", "종이컵", "일회용종이컵", "유리병"]
        for word in recyclable_keywords:
            if word in user_input:
                return f"♻️ '{word}'은(는) 재활용이 가능합니다.", None

        e_waste_keywords = ["텔레비젼", "다리미", "전자기기", "전자제품", "라디오", "드라이기", "청소기", "냉장고", "전자렌지", "김치냉장고", "컴퓨터", "PC", "키보드", "공기청정기", "제습기", "가습기", "전화기"]
        for ew in e_waste_keywords:
            if ew in user_input:
                return f"📆 '{ew}'은(는) 폐가전 무료 방문 수거 서비스를 이용해 주세요:\n👉 https://15990903.or.kr/portal/main/main.do", None

        if "수수료" in user_input:
            clean_text = user_input.replace("수수료", "")
            try:
                region, item = extract_keywords(clean_text)
                if not region or not item:
                    return "⚠️ 지역명과 품목을 포함해 주세요.", None
                result = waste_df[(waste_df['지역'] == region) & (waste_df['품목'] == item)]
                if not result.empty:
                    specs = result[['규격', '수수료', '홈페이지']].drop_duplicates()
                    lines = [f"- {row['규격']}: {row['수수료']}원\n  🔗 홈페이지: {row['홈페이지']}" for _, row in specs.iterrows()]
                    return f"💰 {region} '{item}' 수수료 정보:\n" + "\n".join(lines), None
                else:
                    return f"❌ {region} 지역의 '{item}' 수수료 정보를 찾을 수 없습니다.", None
            except Exception as e:
                print(f"수수료 검색 오류: {e}")
                return "⚠️ 수수료 검색 중 오류가 발생했습니다. 지역명과 품목을 다시 확인해주세요.", None

        # 기존 수거함 패턴 처리 (이전 버전과 호환성 유지)
        bin_match = re.search(r"([가-힣0-9\-\s]+)\s+(폐건전지|폐형광등|건전지|형광등)", user_input)
        if bin_match:
            query_addr = bin_match.group(1).strip()
            bin_type = bin_match.group(2)
            success, response_text, map_obj = find_nearest_bin(query_addr, bin_type)
            return response_text, map_obj

        return "🤖 예: '구로구 냉장고 수수료', '봉천동 폐건전지 수거함'처럼 질문해보세요!", None
        
    except Exception as e:
        import traceback
        print(f"응답 생성 오류: {e}")
        traceback.print_exc()  # 스택 트레이스 출력
        return f"⚠️ 죄송합니다. 오류가 발생했습니다: {str(e)}", None
# Streamlit UI 렌더링
# 이전 코드는 동일

# Streamlit UI 렌더링 부분에서 수정
st.set_page_config(page_title="분리수거 챗봇", layout="centered")
st.title("♻️ 분리수거 챗봇 RecycleMe")

st.markdown(f"### 🔋 현재 포인트: {st.session_state.points}점")

if 'realtime_detect' not in st.session_state:
    st.session_state.realtime_detect = False

stop_requested = False
detecting = False

if st.button("📸 실시간 감지로 포인트 적립"):
    st.session_state.realtime_detect = True

if st.session_state.realtime_detect:
    model = YOLO("best.pt")
    cap = cv2.VideoCapture(0)
    total_detected = 0
    detection_log = []  # 감지 이력 저장용 리스트

    FRAME_WINDOW = st.image([])

    if not cap.isOpened():
        st.error("웹캠을 열 수 없습니다.")
    else:
        st.warning("🔴 실시간 감지 중입니다. 창은 아래에 표시됩니다. 감지되면 자동 종료됩니다.")
        import time
        start_time = time.time()
        detecting = True
        stop_requested = False
        
        while detecting and not stop_requested:
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame)
            result = results[0]
            detections = result.boxes
            battery_count = 0

            for box in detections:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model.names[cls_id]
                if class_name == 'item' and conf >= 0.7:
                    battery_count += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    detection_log.append({
                        "label": class_name,
                        "confidence": round(conf, 2),
                        "box": [x1, y1, x2, y2]
                    })
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{class_name} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            if battery_count > 0 and time.time() - start_time >= 2:
                st.session_state.points += battery_count * 10
                total_detected += battery_count
                st.success(f"✅ 건전지 {battery_count}개 감지 → {battery_count * 10}점 적립!")
                detecting = False

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                stop_requested = True
                detecting = False
        
        cap.release()
        if total_detected > 0:
            st.success(f"🎯 감지 종료! 총 {total_detected}개 감지 → {total_detected * 10}점 적립 완료!")
        st.session_state.realtime_detect = False
        st.info(f"🟢 웹캠 종료됨 (총 감지: {total_detected}개)")
        if detection_log:
            st.markdown("#### 📋 감지 이력")
            for i, log in enumerate(detection_log, 1):
                st.markdown(f"{i}. **{log['label']}** | 신뢰도: {log['confidence']} | 좌표: {log['box']}")

# 감지 중일 때만 종료 버튼 표시
if st.session_state.realtime_detect and detecting:
    if st.button("❌ 감지 종료"):
        stop_requested = True

# 질문 입력 부분
try:
    user_input = st.text_input("질문을 입력하세요")
    if user_input:
        response_text, map_obj = generate_response(user_input)
        st.text_area("응답:", value=response_text, height=200)
        if map_obj:
            folium_static(map_obj)
except Exception as e:
    st.error(f"오류가 발생했습니다: {str(e)}")