# Auto Documentation with Obsidian

자동 문서화 시스템: GitHub 코드 변경사항을 자동으로 요약하여 Obsidian에서 볼 수 있게 합니다.

## Obsidian 설정 방법

1. Obsidian 설치
   - [Obsidian 공식 사이트](https://obsidian.md/)에서 다운로드 및 설치

2. Vault 연결
   ```bash
   # 1. 이 저장소를 로컬에 클론
   git clone https://github.com/[username]/auto-doc-obsidian.git
   cd auto-doc-obsidian

   # 2. Obsidian 실행 후:
   # - "Open folder as vault" 선택
   # - 클론한 폴더 선택
   ```

3. 자동 동기화 설정
   - 주기적으로 `git pull`을 실행하여 최신 요약 문서 동기화
   - 또는 Git 관련 Obsidian 플러그인 사용

## 폴더 구조
```
auto-doc-obsidian/
├── .github/
│   └── workflows/
│       └── auto-doc.yml
├── scripts/
│   └── summarize_diff_to_md.py
└── summaries/
    └── YYYY/
        └── MM/
            └── YYYY-MM-DD_HH-MM-SS_summary.md
```

## 주의사항
- `summaries/` 폴더의 문서는 자동 생성되므로 직접 수정하지 않는 것을 권장
- Git 충돌을 피하기 위해 로컬에서는 `git pull` 후 Obsidian 사용
