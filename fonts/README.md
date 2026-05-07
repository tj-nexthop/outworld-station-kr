# Fonts

이 패치는 한국어 표시를 위해 두 개의 폰트를 사용합니다. 본 레포에는 폰트 바이너리를 포함하지 않으며, 빌드 시 아래 경로에서 직접 다운로드해 이 폴더에 배치해야 합니다.

This patch uses two fonts for Korean rendering. The font binaries are **not bundled** in this repo; download them yourself and place into this folder before building.

## 필요한 파일 (Required files)

```
fonts/
├── Pretendard-Variable.ttf
└── NotoSansKR-Regular.ttf
```

## 다운로드 (Downloads)

### 1. Pretendard

- **공식 깃허브 (Official GitHub)**: https://github.com/orioncactus/pretendard
- **다운로드 (Releases)**: https://github.com/orioncactus/pretendard/releases/latest
- **필요 파일**: `Pretendard-1.3.x.zip` (또는 최신) → 압축 해제 → `public/variable/PretendardVariable.ttf`를 `Pretendard-Variable.ttf`로 이름 변경 후 이 폴더에 배치
- **License**: SIL Open Font License 1.1
- **저작권 (Copyright)**: 길형진 (Kil Hyung-jin)

### 2. Noto Sans KR

- **Google Fonts**: https://fonts.google.com/noto/specimen/Noto+Sans+KR
- **다운로드 (Direct)**: 위 페이지에서 [Get font] → ZIP 다운 → 압축 해제 → `static/NotoSansKR-Regular.ttf`를 이 폴더에 배치
- **공식 깃허브 (Official GitHub)**: https://github.com/notofonts/noto-cjk
- **License**: SIL Open Font License 1.1
- **저작권 (Copyright)**: Google LLC

## 라이선스 노트 (License Notes)

두 폰트 모두 **SIL Open Font License 1.1**로 배포되며, 이는 무료 사용 / 재배포 / 임베딩을 허용합니다. 자세한 라이선스 본문은 각 폰트의 공식 배포 패키지에 동봉된 `OFL.txt` 또는 `LICENSE.txt`를 참고하세요.

Both fonts are distributed under the **SIL Open Font License 1.1**, which permits free use, redistribution, and embedding. See the `OFL.txt` / `LICENSE.txt` shipped with each font's official package for the full license text.
