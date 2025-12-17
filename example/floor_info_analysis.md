# floor_info.json 구조 분석

## 현재 floor_info.json의 문제점

### 1. **저장 형식 불일치**
- **현재 파일**: 배열 형태 `[{...}, {...}]`
- **백엔드 구조**: 각 층은 개별 JSON 파일로 저장
  - 경로: `content/facilities/buildings/{building_id}/floors/floor_{number}.json`
  - 형식: 단일 객체 `{...}`

### 2. **필수 필드 누락**
- **누락된 필드**: `buildingId` (필수)
- 현재 모델에서 `buildingId`는 필수 필드입니다.

### 3. **이미지 경로 형식 불일치**
- **현재 파일**: `"floorImage": "images/floors/image-8.svg"`
- **백엔드 구조**: `"floorImage": "facilities/buildings/{building_id}/floors/floor_plan_{timestamp}.{ext}"`

### 4. **iconTypes 구조 차이**
- **현재 파일**: `iconTypes`에 `currentLocation` 포함
- **백엔드 구조**: `currentLocation`은 별도 필드로 분리됨
  - `iconTypes`: 화장실, 식당 등의 아이콘 타입만 포함
  - `currentLocation`: 별도 객체로 관리

## 올바른 구조 예시

```json
{
  "floor": 1,
  "floorName": "1층",
  "buildingId": "건물UUID",
  "floorImage": "facilities/buildings/{building_id}/floors/floor_plan_20241216_123456.svg",
  "imageSize": {
    "width": 931,
    "height": 330
  },
  "createdAt": "2025-12-11T00:00:00.000Z",
  "updatedAt": "2025-12-11T00:00:00.000Z",
  "iconTypes": {
    "toiletMan": {
      "icon": "facilities/icons/toilet_man.svg",
      "label": "남자화장실"
    },
    "toiletWoman": {
      "icon": "facilities/icons/toilet_woman.svg",
      "label": "여자화장실"
    },
    "restaurant": {
      "icon": "facilities/icons/dish-02.svg",
      "label": "식당"
    }
  },
  "elements": [
    {
      "id": "element1f001",
      "type": "text",
      "text": "토지정보과",
      "x1": 153,
      "y1": 40,
      "x2": 244,
      "y2": 65,
      "style": {
        "fontSize": 12,
        "fontFamily": "Pretendard",
        "fontWeight": "normal",
        "color": "#333333"
      }
    }
  ],
  "currentLocation": {
    "enabled": true,
    "x1": 512,
    "y1": 220,
    "x2": 567,
    "y2": 82,
    "icon": "facilities/icons/current_location.svg",
    "showLabel": true,
    "labelText": "현위치",
    "labelStyle": {
      "fontSize": 11,
      "fontFamily": "Pretendard",
      "fontWeight": "bold",
      "color": "#000000",
      "backgroundColor": "#FFEB3B",
      "borderRadius": 12
    }
  }
}
```

## 수정 필요 사항

1. **배열 → 단일 객체**: 각 층을 개별 JSON 파일로 분리
2. **buildingId 추가**: 각 층 데이터에 건물 ID 필수 추가
3. **이미지 경로 수정**: 새로운 경로 구조에 맞게 변경
4. **iconTypes 정리**: `currentLocation`을 `iconTypes`에서 제거하고 별도 필드로 유지
5. **아이콘 경로 수정**: `images/` → `facilities/icons/` 또는 적절한 경로로 변경

